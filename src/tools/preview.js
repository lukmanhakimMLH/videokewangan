(function () {
  const v = document.getElementById("a-roll"), tl = window.__timelines.main;
  const stage = document.getElementById("stage"), wrap = document.getElementById("stagewrap");
  const seek = document.getElementById("seek"), tc = document.getElementById("tc");
  const pp = document.getElementById("pp"), big = document.getElementById("play");
  const clips = [...document.querySelectorAll("#root [data-start]")].filter(e => e !== v && e.tagName !== "AUDIO");
  v.removeAttribute("data-duration"); v.preload = "auto";
  function fit() { const s = Math.min(wrap.clientWidth / 1080, wrap.clientHeight / 1920); stage.style.transform = "scale(" + s + ")"; }
  addEventListener("resize", fit); fit();
  function render(t) {
    for (const c of clips) { const s = +c.dataset.start, d = +c.dataset.duration; c.style.visibility = (t >= s && t < s + d) ? "visible" : "hidden"; }
    tl.seek(t, false);
    seek.value = t; tc.textContent = t.toFixed(1) + " / 23.0";
  }
  function loop() { render(v.currentTime); if (!v.paused) requestAnimationFrame(loop); }
  function setUI() { const p = v.paused; pp.textContent = p ? "▶" : "❚❚"; big.style.display = p ? "block" : "none"; }
  function toggle() { if (v.paused) { if (v.ended || v.currentTime >= 22.95) v.currentTime = 0; v.play(); } else v.pause(); }
  v.addEventListener("play", () => { setUI(); requestAnimationFrame(loop); });
  v.addEventListener("pause", setUI); v.addEventListener("ended", setUI);
  v.addEventListener("seeked", () => render(v.currentTime));
  big.onclick = toggle; pp.onclick = toggle; stage.onclick = toggle;
  seek.oninput = () => { v.currentTime = +seek.value; render(+seek.value); };
  render(0); setUI();
})();
