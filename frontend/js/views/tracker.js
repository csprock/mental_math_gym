import { api } from "../api.js";
import { navigate } from "../router.js";

/**
 * Progress Tracker
 * Hierarchy: All units → Unit → Lesson
 *   - Lesson level: uses /lessons/{id}/stats directly
 *   - Unit / All: aggregates completed sessions client-side
 */

let chartInstance = null;

export async function renderTracker(mount) {
  const root = document.createElement("section");
  root.className = "stack";
  root.innerHTML = `<h2>Progress</h2><p class="muted">Loading…</p>`;
  mount(root);

  let lessons, sessions;
  try {
    [lessons, sessions] = await Promise.all([
      api.listLessons(),
      api.listSessions({ status: "completed", limit: 200 }),
    ]);
  } catch (e) {
    root.innerHTML = `<h2>Progress</h2><p class="feedback-wrong">Failed to load: ${e.detail ?? e.message}</p>`;
    return;
  }

  const unitsMap = new Map();
  for (const l of lessons) {
    const unit = l.unit || "Other";
    if (!unitsMap.has(unit)) unitsMap.set(unit, []);
    unitsMap.get(unit).push(l);
  }
  const lessonById = new Map(lessons.map((l) => [l.id, l]));

  root.innerHTML = `
    <h2>Progress</h2>
    <div class="row">
      <label style="flex:1 1 200px">
        Unit
        <select id="unit-select">
          <option value="__all">All units</option>
          ${Array.from(unitsMap.keys())
            .map((u) => `<option value="${u}">${u}</option>`)
            .join("")}
        </select>
      </label>
      <label style="flex:1 1 200px">
        Lesson
        <select id="lesson-select">
          <option value="__all">All lessons</option>
        </select>
      </label>
    </div>

    <article id="summary-card">
      <header><strong id="scope-title">All units</strong></header>
      <div class="summary-grid">
        <article><h3 id="k-sessions">–</h3><small>Completed sessions</small></article>
        <article><h3 id="k-problems">–</h3><small>Problems</small></article>
        <article><h3 id="k-correct">–</h3><small>Correct</small></article>
        <article><h3 id="k-avg-score">–</h3><small>Avg score</small></article>
        <article><h3 id="k-avg-spp">–</h3><small>Avg sec/problem</small></article>
      </div>
    </article>

    <article>
      <header><strong>Score over time</strong></header>
      <div class="chart-container"><canvas id="score-chart"></canvas></div>
    </article>

    <article>
      <header><strong>Sessions</strong></header>
      <div style="overflow-x:auto">
        <table class="sessions">
          <thead>
            <tr>
              <th>When</th>
              <th>Lesson</th>
              <th>Problems</th>
              <th>Score</th>
              <th>Sec/problem</th>
            </tr>
          </thead>
          <tbody id="sessions-body"></tbody>
        </table>
      </div>
      <p id="empty-hint" class="muted" hidden>No completed sessions yet. Go do some practice!</p>
    </article>
  `;

  const unitSelect = root.querySelector("#unit-select");
  const lessonSelect = root.querySelector("#lesson-select");

  function refreshLessonOptions() {
    const unit = unitSelect.value;
    lessonSelect.innerHTML = `<option value="__all">All lessons</option>`;
    const pool = unit === "__all" ? lessons : unitsMap.get(unit) || [];
    for (const l of pool) {
      const opt = document.createElement("option");
      opt.value = l.id;
      opt.textContent = l.title;
      lessonSelect.appendChild(opt);
    }
  }
  refreshLessonOptions();

  async function refreshScope() {
    const unit = unitSelect.value;
    const lessonId = lessonSelect.value;

    let scopedSessions;
    let scopeTitle;
    if (lessonId !== "__all") {
      scopedSessions = sessions.filter((s) => s.lesson_id === lessonId);
      scopeTitle = lessonById.get(lessonId)?.title ?? lessonId;
    } else if (unit !== "__all") {
      const unitIds = new Set((unitsMap.get(unit) || []).map((l) => l.id));
      scopedSessions = sessions.filter((s) => unitIds.has(s.lesson_id));
      scopeTitle = unit;
    } else {
      scopedSessions = sessions;
      scopeTitle = "All units";
    }

    root.querySelector("#scope-title").textContent = scopeTitle;
    renderSummaryCards(root, scopedSessions);
    renderChart(root, scopedSessions);
    renderTable(root, scopedSessions, lessonById);
  }

  unitSelect.addEventListener("change", () => {
    refreshLessonOptions();
    refreshScope();
  });
  lessonSelect.addEventListener("change", refreshScope);

  refreshScope();
}

function renderSummaryCards(root, scoped) {
  const n = scoped.length;
  const totalProblems = scoped.reduce((acc, s) => acc + s.total_problems, 0);
  const totalCorrect = scoped.reduce(
    (acc, s) => acc + Math.round((s.score ?? 0) * s.total_problems),
    0
  );
  const avgScore =
    n === 0 ? 0 : scoped.reduce((acc, s) => acc + (s.score ?? 0), 0) / n;
  const avgSpp =
    n === 0
      ? 0
      : scoped.reduce((acc, s) => acc + (s.seconds_per_problem ?? 0), 0) / n;

  root.querySelector("#k-sessions").textContent = n;
  root.querySelector("#k-problems").textContent = totalProblems;
  root.querySelector("#k-correct").textContent = totalCorrect;
  root.querySelector("#k-avg-score").textContent =
    n === 0 ? "–" : `${(avgScore * 100).toFixed(0)}%`;
  root.querySelector("#k-avg-spp").textContent =
    n === 0 ? "–" : `${avgSpp.toFixed(1)}s`;
}

function renderChart(root, scoped) {
  const canvas = root.querySelector("#score-chart");
  if (chartInstance) {
    chartInstance.destroy();
    chartInstance = null;
  }
  if (scoped.length === 0) {
    return;
  }
  // Oldest-first for the chart
  const points = [...scoped]
    .filter((s) => s.completed_at)
    .sort(
      (a, b) => new Date(a.completed_at) - new Date(b.completed_at)
    )
    .map((s) => ({
      x: new Date(s.completed_at).getTime(),
      y: Math.round((s.score ?? 0) * 100),
    }));

  chartInstance = new Chart(canvas, {
    type: "line",
    data: {
      datasets: [
        {
          label: "Score %",
          data: points,
          borderColor: "#1095c1",
          backgroundColor: "rgba(16,149,193,0.15)",
          tension: 0.2,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { min: 0, max: 100, title: { display: true, text: "Score %" } },
        x: {
          type: "linear",
          ticks: {
            callback: (v) => new Date(v).toLocaleDateString(),
            maxTicksLimit: 6,
          },
        },
      },
      plugins: { legend: { display: false } },
    },
  });
}

function renderTable(root, scoped, lessonById) {
  const tbody = root.querySelector("#sessions-body");
  const emptyHint = root.querySelector("#empty-hint");
  tbody.innerHTML = "";
  if (scoped.length === 0) {
    emptyHint.hidden = false;
    return;
  }
  emptyHint.hidden = true;
  const sorted = [...scoped].sort(
    (a, b) => new Date(b.completed_at ?? b.created_at) - new Date(a.completed_at ?? a.created_at)
  );
  for (const s of sorted) {
    const tr = document.createElement("tr");
    tr.dataset.sessionId = s.session_id;
    const when = s.completed_at
      ? new Date(s.completed_at).toLocaleString()
      : new Date(s.created_at).toLocaleString();
    tr.innerHTML = `
      <td>${when}</td>
      <td>${lessonById.get(s.lesson_id)?.title ?? s.lesson_id}</td>
      <td>${s.total_problems}</td>
      <td>${s.score !== null ? `${(s.score * 100).toFixed(0)}%` : "—"}</td>
      <td>${s.seconds_per_problem !== null ? `${s.seconds_per_problem.toFixed(1)}s` : "—"}</td>
    `;
    tr.addEventListener("click", () => navigate(`/session/${s.session_id}`));
    tbody.appendChild(tr);
  }
}
