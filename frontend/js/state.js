/**
 * Tiny pub/sub for ephemeral session state (active practice session).
 * Not persisted — reload = lose active session.
 */

const listeners = new Set();
let state = {
  active: null, // { sessionId, lessonId, problems, cursor, retryMode, timerMode }
};

export function get() {
  return state;
}

export function set(patch) {
  state = { ...state, ...patch };
  listeners.forEach((fn) => fn(state));
}

export function subscribe(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

export function clearActive() {
  set({ active: null });
}
