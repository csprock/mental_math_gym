const BASE = "/api/v1";

async function request(path, options = {}) {
  const resp = await fetch(BASE + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!resp.ok) {
    let detail = resp.statusText;
    try {
      const body = await resp.json();
      detail = body.detail ?? detail;
    } catch (_) {
      /* ignore */
    }
    const err = new Error(`${resp.status} ${detail}`);
    err.status = resp.status;
    err.detail = detail;
    throw err;
  }
  if (resp.status === 204) return null;
  return resp.json();
}

export const api = {
  listLessons: () => request("/lessons"),
  getLesson: (id) => request(`/lessons/${encodeURIComponent(id)}`),
  getLessonStats: (id) =>
    request(`/lessons/${encodeURIComponent(id)}/stats`),

  listSessions: (params = {}) => {
    const q = new URLSearchParams();
    for (const [k, v] of Object.entries(params)) {
      if (v !== undefined && v !== null && v !== "") q.set(k, v);
    }
    const qs = q.toString();
    return request(`/sessions${qs ? `?${qs}` : ""}`);
  },
  getSession: (id) => request(`/sessions/${id}`),
  createSession: (body) =>
    request("/sessions", { method: "POST", body: JSON.stringify(body) }),
  submitAnswer: (sessionId, body) =>
    request(`/sessions/${sessionId}/answers`, {
      method: "POST",
      body: JSON.stringify(body),
    }),
  completeSession: (sessionId) =>
    request(`/sessions/${sessionId}/complete`, { method: "POST" }),
  retryMissed: (sessionId) =>
    request(`/sessions/${sessionId}/retry-missed`, { method: "POST" }),
};
