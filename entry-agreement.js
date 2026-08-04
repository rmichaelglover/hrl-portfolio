(() => {
  "use strict";
  const VERSION = "1.0";
  const KEY = "gaia-worlds-entry-terms";
  let prior = null;
  try { prior = JSON.parse(localStorage.getItem(KEY)); } catch (_) {}
  if (prior && prior.version === VERSION && prior.agreed === true) return;

  const root = new URL("./", document.currentScript.src);
  const terms = new URL("terms/", root).href;
  const license = new URL("licensing/", root).href;
  const style = document.createElement("style");
  style.textContent = `
    .gaia-entry{position:fixed;inset:0;z-index:2147483647;display:grid;place-items:center;padding:18px;background:rgba(1,5,4,.92);backdrop-filter:blur(10px);color:#eefaf2;font:15px/1.5 system-ui,sans-serif}
    .gaia-entry *{box-sizing:border-box}.gaia-entry__card{width:min(620px,100%);max-height:calc(100vh - 36px);overflow:auto;background:#0b1712;border:1px solid #38634d;border-radius:18px;padding:clamp(22px,5vw,36px);box-shadow:0 24px 90px #000}
    .gaia-entry__eyebrow{margin:0;color:#70e7a8;text-transform:uppercase;letter-spacing:.16em;font-size:11px}.gaia-entry h1{margin:.25em 0;font:700 clamp(29px,7vw,46px)/1.08 Georgia,serif;color:#fff}.gaia-entry__lead{font-size:17px;color:#d7eadf}.gaia-entry ul{padding-left:1.25em}.gaia-entry li{margin:.55em 0}.gaia-entry a{color:#82efb5}.gaia-entry__check{display:flex;gap:10px;align-items:flex-start;margin:20px 0;padding:13px;background:#10251a;border-radius:10px}.gaia-entry__check input{width:20px;height:20px;flex:none}.gaia-entry__actions{display:flex;gap:10px;flex-wrap:wrap}.gaia-entry button{border:0;border-radius:999px;padding:12px 18px;font:700 14px system-ui;cursor:pointer}.gaia-entry__agree{background:#65dc9c;color:#052011}.gaia-entry__agree:disabled{opacity:.42;cursor:not-allowed}.gaia-entry__leave{background:#29342f;color:#eefaf2}.gaia-entry__fine{color:#9eb9aa;font-size:12px;margin-bottom:0}`;
  document.head.append(style);

  const gate = document.createElement("section");
  gate.className = "gaia-entry";
  gate.setAttribute("role", "dialog");
  gate.setAttribute("aria-modal", "true");
  gate.setAttribute("aria-labelledby", "gaia-entry-title");
  gate.innerHTML = `<div class="gaia-entry__card"><p class="gaia-entry__eyebrow">Gaia Worlds · Entry agreement v${VERSION}</p><h1 id="gaia-entry-title">Welcome. Enter in trust.</h1><p class="gaia-entry__lead">Before entering this HRL or Maestro world, please agree to these concise, binding terms:</p><ul><li>Explore lawfully and respectfully; do not disrupt, deceive, or violate others’ rights.</li><li>Protected work is MIRL-1.0 source-available. No money-making use without a published significant improvement, all other license conditions, and prior written Trust of Trusts approval.</li><li>Entry grants no ownership, endorsement, or monetization right. Third-party terms and prior MIT grants remain intact.</li><li>The worlds are experimental and educational, not professional advice, and are provided as-is to the maximum extent lawful.</li></ul><p><a href="${terms}" target="_blank" rel="noopener">Read the full Entry Terms</a> · <a href="${license}" target="_blank" rel="noopener">License &amp; stewardship</a></p><label class="gaia-entry__check"><input type="checkbox"><span>I have legal capacity to agree (or my parent/legal guardian agrees for me), I have read the Entry Terms, and I agree to be bound by version ${VERSION}.</span></label><div class="gaia-entry__actions"><button class="gaia-entry__agree" disabled>I agree — enter Gaia Worlds</button><button class="gaia-entry__leave">I do not agree</button></div><p class="gaia-entry__fine">Acceptance version and time are stored only in this browser. A new terms version will ask again.</p></div>`;
  const check = gate.querySelector("input");
  const agree = gate.querySelector(".gaia-entry__agree");
  check.addEventListener("change", () => { agree.disabled = !check.checked; });
  agree.addEventListener("click", () => {
    try { localStorage.setItem(KEY, JSON.stringify({version: VERSION, agreed: true, acceptedAt: new Date().toISOString()})); } catch (_) {}
    gate.remove(); style.remove();
  });
  gate.querySelector(".gaia-entry__leave").addEventListener("click", () => {
    if (history.length > 1) history.back(); else location.replace("about:blank");
  });
  document.body.append(gate);
  agree.focus();
})();
