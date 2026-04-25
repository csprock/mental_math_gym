import { api } from "../api.js";

export async function renderSessionDetail(mount, id) {
  const root = document.createElement("section");
  root.className = "stack";
  root.innerHTML = `<p class="muted">Loading session ${id}…</p>`;
  mount(root);

  let session;
  try {
    session = await api.getSession(id);
  } catch (e) {
    root.innerHTML = `<h2>Session ${id}</h2><p class="feedback-wrong">${
      e.detail ?? e.message
    }</p><p><a href="#/tracker">Back to progress</a></p>`;
    return;
  }

  const s = session.summary;
  const created = new Date(session.created_at).toLocaleString();
  const completed = session.completed_at
    ? new Date(session.completed_at).toLocaleString()
    : "—";

  root.innerHTML = `
    <nav aria-label="breadcrumb"><ul><li><a href="#/tracker">Progress</a></li><li>Session ${session.session_id}</li></ul></nav>
    <h2>${session.lesson_id}</h2>
    <p class="muted">Status: ${session.status} · Created: ${created} · Completed: ${completed}</p>

    <div class="summary-grid">
      <article><h3>${(s.score * 100).toFixed(0)}%</h3><small>Score</small></article>
      <article><h3>${s.correct_problems} / ${s.total_problems}</h3><small>Correct</small></article>
      <article><h3>${s.seconds_per_problem.toFixed(1)}s</h3><small>Per problem</small></article>
      <article><h3>${s.missed_problem_ids.length}</h3><small>Missed</small></article>
    </div>

    ${
      Object.keys(session.params || {}).length
        ? `<p class="muted">Params: ${Object.entries(session.params)
            .map(([k, v]) => `<code>${k}=${v}</code>`)
            .join(" · ")}</p>`
        : ""
    }

    <h3>Problems</h3>
    <div id="problems"></div>

    ${
      s.missed_problem_ids.length > 0 && session.status === "completed"
        ? `<button id="retry-btn">Retry missed</button><p id="retry-error" class="feedback-wrong" hidden></p>`
        : ""
    }
  `;

  const problemsEl = root.querySelector("#problems");
  for (const p of session.problems) {
    // First-try only, matching the backend score. Attempts come back ordered
    // by attempt_number, so [0] is the first one.
    const gotCorrect = p.attempts.length > 0 && p.attempts[0].is_correct;
    const div = document.createElement("div");
    div.className =
      "problem-review " + (gotCorrect ? "correct" : p.attempts.length ? "missed" : "");
    const attemptSummary =
      p.attempts.length === 0
        ? '<span class="muted">No attempts.</span>'
        : p.attempts
            .map(
              (a) =>
                `#${a.attempt_number}: <code>${a.user_answer}</code> ${
                  a.is_correct ? "✓" : "✗"
                } (${(a.elapsed_ms / 1000).toFixed(1)}s)`
            )
            .join(" · ");
    div.innerHTML = `
      <div><strong>${p.ordinal}.</strong> ${p.prompt} ${
        p.answer !== null ? `<span class="muted">= ${p.answer}</span>` : ""
      }</div>
      <div class="attempt-list">${attemptSummary}</div>
    `;
    problemsEl.appendChild(div);
  }

  const retryBtn = root.querySelector("#retry-btn");
  if (retryBtn) {
    retryBtn.addEventListener("click", async () => {
      const errEl = root.querySelector("#retry-error");
      let newSession;
      try {
        newSession = await api.retryMissed(session.session_id);
      } catch (e) {
        errEl.textContent = `Could not start retry: ${e.detail ?? e.message}`;
        errEl.hidden = false;
        return;
      }
      // Hop into the gym view with a fresh active session.
      const state = await import("../state.js");
      state.set({
        active: {
          sessionId: newSession.session_id,
          lessonId: newSession.lesson_id,
          lessonTitle: `${session.lesson_id} (retry)`,
          problems: newSession.problems,
          cursor: 0,
          retryMode: "retry",
          showTimer: true,
          startedAt: Date.now(),
          results: {},
          finished: false,
        },
      });
      location.hash = "#/gym";
    });
  }
}
