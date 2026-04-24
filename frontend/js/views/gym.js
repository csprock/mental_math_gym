import { api } from "../api.js";
import * as state from "../state.js";
import { navigate } from "../router.js";

/**
 * Gym view — setup → play → summary. Which screen shows is driven by state:
 *   - no active session → setup
 *   - active + not finished → play
 *   - active + finished → summary
 */

export async function renderGym(mount) {
  const active = state.get().active;
  if (!active) return renderSetup(mount);
  if (active.finished) return renderSummary(mount, active);
  return renderPlay(mount, active);
}

/* ------------------------------- Setup ---------------------------------- */

async function renderSetup(mount) {
  const root = document.createElement("section");
  root.className = "stack";
  root.innerHTML = `<h2>Practice Gym</h2><p class="muted">Loading lessons…</p>`;
  mount(root);

  let lessons;
  try {
    lessons = await api.listLessons();
  } catch (e) {
    root.innerHTML = `<h2>Practice Gym</h2><p class="feedback-wrong">Failed to load lessons: ${e.detail ?? e.message}</p>`;
    return;
  }

  // Group by unit for the dropdown
  const grouped = new Map();
  for (const l of lessons) {
    const key = l.unit || "Other";
    if (!grouped.has(key)) grouped.set(key, []);
    grouped.get(key).push(l);
  }

  root.innerHTML = `
    <h2>Practice Gym</h2>
    <form id="setup-form" class="stack">
      <label>
        Lesson
        <select name="lesson" required></select>
      </label>
      <div id="lesson-description" class="muted"></div>
      <div id="param-fields"></div>
      <label>
        Number of problems
        <input type="number" name="size" value="10" min="1" max="500" required />
      </label>
      <fieldset>
        <legend>On a wrong answer</legend>
        <label><input type="radio" name="retryMode" value="retry" checked /> Let me try again (multiple attempts per problem)</label>
        <label><input type="radio" name="retryMode" value="advance" /> Reveal the answer and advance</label>
      </fieldset>
      <label>
        <input type="checkbox" name="timer" checked />
        Show session timer
      </label>
      <button type="submit">Start session</button>
      <p id="setup-error" class="feedback-wrong" hidden></p>
    </form>
  `;

  const select = root.querySelector('select[name="lesson"]');
  for (const [unit, ls] of grouped) {
    const group = document.createElement("optgroup");
    group.label = unit;
    for (const l of ls) {
      const opt = document.createElement("option");
      opt.value = l.id;
      opt.textContent = `${l.title} (${l.id})`;
      group.appendChild(opt);
    }
    select.appendChild(group);
  }

  const descEl = root.querySelector("#lesson-description");
  const paramsEl = root.querySelector("#param-fields");

  const byId = new Map(lessons.map((l) => [l.id, l]));
  function updateForLesson(id) {
    const l = byId.get(id);
    if (!l) return;
    descEl.textContent = l.description || "";
    paramsEl.innerHTML = "";
    for (const p of l.params) {
      paramsEl.appendChild(renderParamField(p));
    }
  }
  select.addEventListener("change", () => updateForLesson(select.value));
  updateForLesson(select.value);

  root.querySelector("#setup-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = e.currentTarget;
    const fd = new FormData(form);
    const lessonId = fd.get("lesson");
    const size = parseInt(fd.get("size"), 10);
    const retryMode = fd.get("retryMode");
    const showTimer = fd.get("timer") === "on";

    const lesson = byId.get(lessonId);
    const params = {};
    for (const p of lesson.params) {
      const raw = fd.get(`param_${p.name}`);
      if (p.type === "bool") {
        params[p.name] = raw === "true";
      } else if (p.type === "int") {
        params[p.name] = parseInt(raw, 10);
      } else {
        params[p.name] = raw;
      }
    }

    const errorEl = root.querySelector("#setup-error");
    errorEl.hidden = true;

    let session;
    try {
      session = await api.createSession({
        lesson_id: lessonId,
        size,
        params,
      });
    } catch (err) {
      errorEl.textContent = `Could not start session: ${err.detail ?? err.message}`;
      errorEl.hidden = false;
      return;
    }

    state.set({
      active: {
        sessionId: session.session_id,
        lessonId: session.lesson_id,
        lessonTitle: lesson.title,
        problems: session.problems,
        cursor: 0,
        retryMode,
        showTimer,
        startedAt: Date.now(),
        results: {}, // problemId -> { correct, correctAnswer, attempts }
        finished: false,
      },
    });
    renderGym(mount);
  });
}

function renderParamField(param) {
  const wrap = document.createElement("div");
  wrap.className = "param-field";
  const label = document.createElement("label");
  const title = param.description || param.name;

  if (param.type === "bool") {
    wrap.innerHTML = `
      <strong>${title}</strong>
      <div class="row">
        <label><input type="radio" name="param_${param.name}" value="true" ${
          param.default === true ? "checked" : ""
        } /> Yes</label>
        <label><input type="radio" name="param_${param.name}" value="false" ${
          param.default !== true ? "checked" : ""
        } /> No</label>
      </div>
    `;
    return wrap;
  }

  if (param.type === "int") {
    label.innerHTML = `<strong>${title}</strong>`;
    const input = document.createElement("input");
    input.type = "number";
    input.name = `param_${param.name}`;
    input.step = "1";
    input.value = param.default ?? 0;
    label.appendChild(input);
    wrap.appendChild(label);
    return wrap;
  }

  // Fallback: text input
  label.innerHTML = `<strong>${title}</strong>`;
  const input = document.createElement("input");
  input.type = "text";
  input.name = `param_${param.name}`;
  input.value = param.default ?? "";
  label.appendChild(input);
  wrap.appendChild(label);
  return wrap;
}

/* -------------------------------- Play ---------------------------------- */

function renderPlay(mount, active) {
  const root = document.createElement("section");
  root.className = "stack";
  mount(root);

  const p = active.problems[active.cursor];
  const n = active.problems.length;

  root.innerHTML = `
    <div class="progress-line">
      <span>${active.lessonTitle} · Problem ${active.cursor + 1} of ${n}</span>
      <span class="timer" id="timer" ${active.showTimer ? "" : "hidden"}>0s</span>
    </div>
    <progress value="${active.cursor}" max="${n}"></progress>
    <div class="prompt">${p.prompt}</div>
    <form id="answer-form" class="stack">
      <input type="number" step="any" class="answer-input" name="answer" required />
      <div class="row">
        <button type="submit">Submit</button>
        <button type="button" id="show-answer-btn" class="secondary">Show answer</button>
        <span class="spacer"></span>
        <button type="button" id="abort-btn" class="contrast outline">Abort session</button>
      </div>
      <div id="feedback" aria-live="polite"></div>
    </form>
  `;

  const input = root.querySelector('input[name="answer"]');
  const feedbackEl = root.querySelector("#feedback");
  const form = root.querySelector("#answer-form");

  // `autofocus` only fires on first document load, not on re-renders between
  // problems. Focus explicitly so the user can type → Enter → type without
  // reaching for the mouse. Defer to the next frame so the browser has
  // finished laying out the new form before we ask for focus — focusing an
  // element that was just attached via innerHTML can be flaky otherwise.
  requestAnimationFrame(() => input.focus());

  // Per-problem start time (reset each time we land on a new problem)
  let problemStart = Date.now();

  // Session timer tick
  if (active.showTimer) {
    const timerEl = root.querySelector("#timer");
    const tick = () => {
      if (state.get().active !== active) return; // stop when state changes
      const s = Math.floor((Date.now() - active.startedAt) / 1000);
      timerEl.textContent = `${s}s`;
      requestAnimationFrame(() => setTimeout(tick, 500));
    };
    tick();
  }

  const currentResult = () => {
    if (!active.results[p.id]) {
      active.results[p.id] = { correct: false, correctAnswer: null, attempts: 0 };
    }
    return active.results[p.id];
  };

  async function submit(userAnswer) {
    const elapsedMs = Date.now() - problemStart;
    let resp;
    try {
      resp = await api.submitAnswer(active.sessionId, {
        problem_id: p.id,
        user_answer: userAnswer,
        elapsed_ms: elapsedMs,
      });
    } catch (e) {
      feedbackEl.innerHTML = `<span class="feedback-wrong">Submit failed: ${e.detail ?? e.message}</span>`;
      return;
    }
    const r = currentResult();
    r.attempts += 1;

    if (resp.correct) {
      r.correct = true;
      r.correctAnswer = resp.correct_answer;
      feedbackEl.innerHTML = `<span class="feedback-correct">Correct!</span>`;
      setTimeout(advance, 400);
      return;
    }

    // Wrong branch
    r.correctAnswer = resp.correct_answer;
    if (active.retryMode === "advance") {
      feedbackEl.innerHTML = `<span class="feedback-wrong">Wrong. Answer: ${resp.correct_answer}</span>`;
      setTimeout(advance, 900);
    } else {
      feedbackEl.innerHTML = `<span class="feedback-wrong">Not quite — try again.</span>`;
      input.value = "";
      input.focus();
    }
  }

  function advance() {
    if (active.cursor + 1 >= active.problems.length) {
      finish();
    } else {
      state.set({
        active: { ...active, cursor: active.cursor + 1 },
      });
      renderGym(mount);
    }
  }

  async function finish() {
    let summary;
    try {
      summary = await api.completeSession(active.sessionId);
    } catch (e) {
      feedbackEl.innerHTML = `<span class="feedback-wrong">Complete failed: ${e.detail ?? e.message}</span>`;
      return;
    }
    state.set({
      active: { ...active, finished: true, summary },
    });
    renderGym(mount);
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const raw = input.value;
    if (raw === "") return;
    const num = Number(raw);
    if (!Number.isFinite(num)) {
      feedbackEl.innerHTML = `<span class="feedback-wrong">Enter a number.</span>`;
      return;
    }
    submit(num);
  });

  root.querySelector("#show-answer-btn").addEventListener("click", async () => {
    // Record whatever is in the input (default 0) as a wrong attempt; the
    // response gives us the correct answer to reveal. "Give up" is an honest
    // wrong attempt for stats purposes.
    const raw = input.value === "" ? 0 : Number(input.value);
    const elapsedMs = Date.now() - problemStart;
    let resp;
    try {
      resp = await api.submitAnswer(active.sessionId, {
        problem_id: p.id,
        user_answer: Number.isFinite(raw) ? raw : 0,
        elapsed_ms: elapsedMs,
      });
    } catch (e) {
      feedbackEl.innerHTML = `<span class="feedback-wrong">Submit failed: ${e.detail ?? e.message}</span>`;
      return;
    }
    const r = currentResult();
    r.attempts += 1;
    r.correctAnswer = resp.correct_answer;
    if (resp.correct) r.correct = true;
    feedbackEl.innerHTML = `<span class="feedback-wrong">Answer: ${resp.correct_answer}</span>`;
    setTimeout(advance, 1200);
  });

  root.querySelector("#abort-btn").addEventListener("click", () => {
    if (!confirm("Abandon this session? Progress will not be saved as completed.")) return;
    state.clearActive();
    renderGym(mount);
  });
}

/* ------------------------------- Summary -------------------------------- */

function renderSummary(mount, active) {
  const s = active.summary;
  const root = document.createElement("section");
  root.className = "stack";
  root.innerHTML = `
    <h2>Session complete</h2>
    <p class="muted">${active.lessonTitle}</p>
    <div class="summary-grid">
      <article><h3>${(s.score * 100).toFixed(0)}%</h3><small>Score</small></article>
      <article><h3>${s.correct_problems} / ${s.total_problems}</h3><small>Correct</small></article>
      <article><h3>${s.seconds_per_problem.toFixed(1)}s</h3><small>Per problem</small></article>
      <article><h3>${s.missed_problem_ids.length}</h3><small>Missed</small></article>
    </div>
    <div class="row">
      ${
        s.missed_problem_ids.length > 0
          ? `<button id="retry-btn">Retry missed</button>`
          : ""
      }
      <button id="new-btn" class="secondary">New session</button>
      <button id="review-btn" class="contrast outline">Review</button>
    </div>
    <p id="error" class="feedback-wrong" hidden></p>
  `;
  mount(root);

  const errEl = root.querySelector("#error");

  root.querySelector("#new-btn").addEventListener("click", () => {
    state.clearActive();
    renderGym(mount);
  });

  root.querySelector("#review-btn").addEventListener("click", () => {
    navigate(`/session/${s.session_id}`);
  });

  const retryBtn = root.querySelector("#retry-btn");
  if (retryBtn) {
    retryBtn.addEventListener("click", async () => {
      let newSession;
      try {
        newSession = await api.retryMissed(s.session_id);
      } catch (e) {
        errEl.textContent = `Could not start retry: ${e.detail ?? e.message}`;
        errEl.hidden = false;
        return;
      }
      // Keep retryMode + showTimer from the previous run.
      const prev = state.get().active;
      state.set({
        active: {
          sessionId: newSession.session_id,
          lessonId: newSession.lesson_id,
          lessonTitle: prev.lessonTitle + " (retry)",
          problems: newSession.problems,
          cursor: 0,
          retryMode: prev.retryMode,
          showTimer: prev.showTimer,
          startedAt: Date.now(),
          results: {},
          finished: false,
        },
      });
      renderGym(mount);
    });
  }
}
