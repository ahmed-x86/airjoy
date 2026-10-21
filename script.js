const statusEl = document.getElementById('status');
let ws = null, pending = {}, raf = 0;
const releasers = [];

function send(o, now) {
  Object.assign(pending, o);
  if (now) flush();
  else if (!raf) raf = requestAnimationFrame(flush);
}

function flush() {
  raf = 0;
  if (ws && ws.readyState === 1 && Object.keys(pending).length) ws.send(JSON.stringify(pending));
  pending = {};
}
const buzz = () => navigator.vibrate && navigator.vibrate(8);

/* buttons, triggers, d-pad */
document.querySelectorAll('.k[data-k],.k[data-t],.k[data-d]').forEach(el => {
  const { k, t, d } = el.dataset;
  const set = v => {
    el.classList.toggle('on', !!v);
    if (k) send({ [k]: v }, true);
    else if (t) send({ [t]: v }, true);
    else { const [axis, val] = d.split(':'); send({ [axis]: v ? +val : 0 }, true); }
  };
  el.addEventListener('pointerdown', ev => { el.setPointerCapture(ev.pointerId); set(1); buzz(); ev.preventDefault(); });
  ['pointerup', 'pointercancel'].forEach(n => el.addEventListener(n, () => set(0)));
  releasers.push(() => { if (el.classList.contains('on')) set(0); });
});

/* analog sticks */
document.querySelectorAll('.stick').forEach(el => {
  const knob = el.firstElementChild, kx = el.dataset.x, ky = el.dataset.y, click = el.dataset.click;
  let id = null, moved = false, t0 = 0;
  const move = ev => {
    const r = el.getBoundingClientRect(), R = r.width / 2;
    let dx = (ev.clientX - r.left - R) / R, dy = (ev.clientY - r.top - R) / R;
    const m = Math.hypot(dx, dy);
    if (m > 1) { dx /= m; dy /= m; }
    if (m > 0.25) moved = true;
    knob.style.transform = `translate(${dx * R * 0.55}px,${dy * R * 0.55}px)`;
    send({ [kx]: +dx.toFixed(3), [ky]: +dy.toFixed(3) });
  };
  el.addEventListener('pointerdown', ev => {
    id = ev.pointerId; moved = false; t0 = performance.now();
    el.setPointerCapture(id); el.classList.add('live'); move(ev); ev.preventDefault();
  });
  el.addEventListener('pointermove', ev => { if (ev.pointerId === id) move(ev); });
  const rest = () => {
    id = null; el.classList.remove('live'); knob.style.transform = '';
    send({ [kx]: 0, [ky]: 0 }, true);
  };
  const end = ev => {
    if (ev.pointerId !== id) return;
    rest();
    if (!moved && performance.now() - t0 < 250) {
      send({ [click]: 1 }, true);
      setTimeout(() => send({ [click]: 0 }, true), 60);
    }
  };
  el.addEventListener('pointerup', end);
  el.addEventListener('pointercancel', end);
  releasers.push(() => { if (id !== null) rest(); });
});

/* Steam Keyboard Keys (sent with KB_ prefix so they don't clash with gamepad buttons) */
document.querySelectorAll('.kb-key[data-key]').forEach(el => {
  const key = el.dataset.key;
  const set = v => {
    el.classList.toggle('on', !!v);
    send({ ['KB_' + key]: v }, true);
  };
  el.addEventListener('pointerdown', ev => { el.setPointerCapture(ev.pointerId); set(1); buzz(); ev.preventDefault(); });
  ['pointerup', 'pointercancel'].forEach(n => el.addEventListener(n, () => set(0)));
  releasers.push(() => { if (el.classList.contains('on')) set(0); });
});

/* Toggle Steam Keyboard Drawer & Native Mobile Keyboard */
const kbToggle = document.getElementById('kb-toggle');
const kbDrawer = document.getElementById('kb-drawer');
const nativeKbBtn = document.getElementById('native-kb-btn');
const nativeKb = document.getElementById('native-kb');

kbToggle.addEventListener('pointerdown', ev => {
  ev.preventDefault();
  buzz();
  kbDrawer.classList.toggle('open');
  kbToggle.classList.toggle('active-toggle', kbDrawer.classList.contains('open'));
});

nativeKbBtn.addEventListener('click', () => {
  buzz();
  nativeKb.value = '';
  nativeKb.focus();
});

nativeKb.addEventListener('input', () => {
  if (nativeKb.value) {
    send({ TEXT: nativeKb.value }, true);
    nativeKb.value = '';
  }
});

nativeKb.addEventListener('keydown', ev => {
  if (ev.key === 'Backspace') {
    send({ KB_BACKSPACE: 1 }, true);
    setTimeout(() => send({ KB_BACKSPACE: 0 }, true), 40);
  } else if (ev.key === 'Enter') {
    send({ KB_ENTER: 1 }, true);
    setTimeout(() => send({ KB_ENTER: 0 }, true), 40);
  }
});

/* Steam Trackpad */
const tpToggle = document.getElementById('tp-toggle');
const trackpad = document.getElementById('trackpad');
let tpId = null, tpX = 0, tpY = 0, tpMoved = false, tpT0 = 0, tpFingers = 0;

tpToggle.addEventListener('pointerdown', ev => {
  ev.preventDefault();
  buzz();
  trackpad.classList.toggle('open');
  tpToggle.classList.toggle('active-toggle', trackpad.classList.contains('open'));
});

trackpad.addEventListener('pointerdown', ev => {
  tpFingers++;
  if (tpId === null) {
    tpId = ev.pointerId;
    tpX = ev.clientX; tpY = ev.clientY;
    tpMoved = false; tpT0 = performance.now();
    trackpad.setPointerCapture(tpId);
  }
  ev.preventDefault();
});

trackpad.addEventListener('pointermove', ev => {
  if (ev.pointerId !== tpId) return;
  const dx = (ev.clientX - tpX) * 1.8;
  const dy = (ev.clientY - tpY) * 1.8;
  if (Math.hypot(dx, dy) > 2) {
    tpMoved = true;
    tpX = ev.clientX; tpY = ev.clientY;
    send({ MX: Math.round(dx), MY: Math.round(dy) }, true);
  }
});

const endTrackpad = ev => {
  if (ev.pointerId === tpId) {
    tpId = null;
    if (!tpMoved && performance.now() - tpT0 < 250) {
      const btn = tpFingers > 1 ? 'M_RIGHT' : 'M_LEFT';
      send({ [btn]: 1 }, true);
      setTimeout(() => send({ [btn]: 0 }, true), 50);
    }
  }
  tpFingers = Math.max(0, tpFingers - 1);
};
trackpad.addEventListener('pointerup', endTrackpad);
trackpad.addEventListener('pointercancel', endTrackpad);

const releaseAll = () => releasers.forEach(f => f());
window.addEventListener('blur', releaseAll);
document.addEventListener('visibilitychange', () => { if (document.hidden) releaseAll(); });

/* labels per controller type */
const LABELS = {
  xbox:  { A: 'A', B: 'B', X: 'X', Y: 'Y', LB: 'LB', RB: 'RB', LT: 'LT', RT: 'RT', BACK: 'Back', START: 'Start', GUIDE: 'Xbox' },
  ps4:   { A: '\u2715', B: '\u25CB', X: '\u25A1', Y: '\u25B3', LB: 'L1', RB: 'R1', LT: 'L2', RT: 'R2', BACK: 'Share', START: 'Options', GUIDE: 'PS' },
  steam: { A: 'A', B: 'B', X: 'X', Y: 'Y', LB: 'L1', RB: 'R1', LT: 'L2', RT: 'R2', BACK: 'View', START: 'Menu', GUIDE: 'Steam', L4: 'L4', R4: 'R4' },
};
let mode = 'xbox';

function connect() {
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  ws = new WebSocket(`${proto}://${location.host}/ws?mode=${mode}`);
  ws.onopen = () => { statusEl.textContent = 'Connected'; };
  ws.onmessage = m => {
    const d = JSON.parse(m.data);
    if (d.player) statusEl.textContent = 'Player ' + d.player;
    if (d.error) statusEl.textContent = d.error;
  };
  ws.onclose = () => { releaseAll(); statusEl.textContent = 'Reconnecting...'; setTimeout(connect, 1000); };
}

function applyMode(m) {
  mode = m;
  document.body.dataset.mode = m;
  document.querySelectorAll('.k[data-k],.k[data-t]').forEach(el => {
    const key = el.dataset.k || el.dataset.t;
    if (LABELS[m][key]) el.textContent = LABELS[m][key];
  });
}

document.querySelectorAll('#gate button').forEach(btn => btn.addEventListener('click', async () => {
  applyMode(btn.dataset.mode);
  try { await document.documentElement.requestFullscreen(); } catch (_) {}
  try { await screen.orientation.lock('landscape'); } catch (_) {}
  try { await navigator.wakeLock.request('screen'); } catch (_) {}
  document.getElementById('gate').remove();
  connect();
}));
document.addEventListener('contextmenu', ev => ev.preventDefault());