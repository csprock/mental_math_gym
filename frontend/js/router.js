const routes = [];
let notFoundHandler = null;

export function register(pattern, handler) {
  const keys = [];
  const regex = new RegExp(
    "^" +
      pattern
        .replace(/\//g, "\\/")
        .replace(/:([A-Za-z_]+)/g, (_, k) => {
          keys.push(k);
          return "([^/]+)";
        }) +
      "$"
  );
  routes.push({ regex, keys, handler });
}

export function setNotFound(handler) {
  notFoundHandler = handler;
}

export function navigate(path) {
  if (location.hash === `#${path}`) {
    resolve();
  } else {
    location.hash = path;
  }
}

function resolve() {
  const raw = location.hash.slice(1) || "/gym";
  for (const { regex, keys, handler } of routes) {
    const match = raw.match(regex);
    if (match) {
      const params = {};
      keys.forEach((k, i) => (params[k] = decodeURIComponent(match[i + 1])));
      handler(params);
      updateNavHighlight(raw);
      return;
    }
  }
  if (notFoundHandler) notFoundHandler(raw);
}

function updateNavHighlight(raw) {
  const section = raw.split("/")[1] || "";
  document.querySelectorAll("[data-nav]").forEach((el) => {
    if (el.dataset.nav === section) {
      el.setAttribute("aria-current", "page");
    } else {
      el.removeAttribute("aria-current");
    }
  });
}

export function start() {
  window.addEventListener("hashchange", resolve);
  resolve();
}
