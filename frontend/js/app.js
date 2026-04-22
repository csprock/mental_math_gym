import { register, setNotFound, start, navigate } from "./router.js";
import { renderGym } from "./views/gym.js";
import { renderTracker } from "./views/tracker.js";
import { renderSessionDetail } from "./views/session_detail.js";

const view = document.getElementById("view");

function mount(node) {
  view.replaceChildren(node);
}

register("/", () => navigate("/gym"));
register("/gym", () => renderGym(mount));
register("/tracker", () => renderTracker(mount));
register("/session/:id", ({ id }) => renderSessionDetail(mount, id));

setNotFound(() => {
  const el = document.createElement("article");
  el.innerHTML =
    '<h2>Not found</h2><p>That page does not exist. <a href="#/gym">Back to practice</a>.</p>';
  mount(el);
});

start();
