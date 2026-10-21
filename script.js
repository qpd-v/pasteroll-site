/* Pasteroll site. No libraries, no network requests except looking for your own media files. */
(function () {
  'use strict';
  var root = document.documentElement;
  root.classList.remove('no-js');

  // ------------------------------------------------------------ theme picker (temporary)
  var THEMES = ['cinnamon', 'frappe', 'macchiato', 'mocha', 'latte'];
  var NAMES = { cinnamon: 'Cinnamon', frappe: 'Frappé', macchiato: 'Macchiato', mocha: 'Mocha', latte: 'Latte' };
  var BARS = { cinnamon: '#1f1713', frappe: '#303446', macchiato: '#24273a', mocha: '#1e1e2e', latte: '#eff1f5' };
  var picker = document.getElementById('picker');
  var toggle = picker && picker.querySelector('.picker-toggle');
  var list = picker && picker.querySelector('.picker-list');
  var nameEl = picker && picker.querySelector('.picker-name');
  var nowEl = picker && picker.querySelector('.sw-now');

  function setTheme(t, save) {
    if (THEMES.indexOf(t) < 0) t = 'cinnamon';
    root.dataset.theme = t;
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', BARS[t]);
    if (nameEl) nameEl.textContent = NAMES[t];
    if (nowEl) nowEl.setAttribute('data-sw', t);
    if (list) list.querySelectorAll('[data-set]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.set === t)); });
    if (save) { try { localStorage.setItem('pasteroll-theme', t); } catch (e) {} }
  }
  setTheme(root.dataset.theme, false);

  if (picker) {
    toggle.addEventListener('click', function () {
      var open = list.hidden;
      list.hidden = !open;
      toggle.setAttribute('aria-expanded', String(open));
    });
    list.addEventListener('click', function (e) {
      var b = e.target.closest('[data-set]');
      if (b) setTheme(b.dataset.set, true);
    });
    document.addEventListener('click', function (e) {
      if (!picker.contains(e.target) && !list.hidden) { list.hidden = true; toggle.setAttribute('aria-expanded', 'false'); }
    });
    document.addEventListener('keydown', function (e) {
      if (e.target.closest && e.target.closest('input, textarea, select, [contenteditable]')) return;
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      if (e.key === 't' || e.key === 'T') {
        setTheme(THEMES[(THEMES.indexOf(root.dataset.theme) + 1) % THEMES.length], true);
      } else if (e.key === 'Escape' && !list.hidden) {
        list.hidden = true; toggle.setAttribute('aria-expanded', 'false'); toggle.focus();
      }
    });
  }

  // ------------------------------------------------------------ the keys press, one group after another
  // The tree plays top to bottom: first the keys that open the carousel, then each branch in turn.
  // A group's data-seq is a list of steps "time:action:key[:ms]". Actions: down (hold the key),
  // up (let go), tap (press and release after ms). The opening keys hold Ctrl, then Shift, tap the
  // middle button once, then let go of both, as a person would. It plays while the tree is on
  // screen, and the branch being shown is outlined.
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var tree = document.getElementById('tree');

  function parse(text) {
    return text.split(',').map(function (p) {
      var a = p.split(':');
      return { t: +a[0], act: a[1], k: +a[2], ms: +(a[3] || 170) };
    });
  }
  function clear(tr) {
    (tr._timers || []).forEach(clearTimeout);
    tr._timers = [];
    tr.querySelectorAll('.key.down').forEach(function (k) { k.classList.remove('down'); });
    tr.querySelectorAll('.branch.lit').forEach(function (b) { b.classList.remove('lit'); });
  }
  function play(tr) {
    clear(tr);
    function at(ms, fn) { tr._timers.push(setTimeout(fn, ms)); }
    var base = 0;
    tr.querySelectorAll('[data-seq]').forEach(function (group) {
      var keys = group.querySelectorAll('.key');
      var branch = group.closest('.branch');
      var end = 0;
      if (branch) at(base, function () { branch.classList.add('lit'); });
      parse(group.dataset.seq).forEach(function (s) {
        var el = keys[s.k];
        if (!el) return;
        if (s.act === 'down') {
          at(base + s.t, function () { el.classList.add('down'); });
          end = Math.max(end, s.t);
        } else if (s.act === 'up') {
          at(base + s.t, function () { el.classList.remove('down'); });
          end = Math.max(end, s.t);
        } else {
          at(base + s.t, function () { el.classList.add('down'); });
          at(base + s.t + s.ms, function () { el.classList.remove('down'); });
          end = Math.max(end, s.t + s.ms);
        }
      });
      // let go of everything in the group, then on to the next one
      at(base + end + 700, function () {
        group.querySelectorAll('.key.down').forEach(function (k) { k.classList.remove('down'); });
        if (branch) branch.classList.remove('lit');
      });
      base += end + 700 + (branch ? 300 : 600);
    });
    at(base + 3000, function () { if (tr._live) play(tr); });
  }
  if (tree && !reduce && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          if (!tree._live) { tree._live = true; play(tree); }
        } else {
          tree._live = false;
          clear(tree);
        }
      });
    }, { threshold: 0.35 }).observe(tree);
  }

  // ------------------------------------------------------------ copy buttons
  document.querySelectorAll('.copy').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var text = btn.dataset.copy || '';
      var done = function () {
        btn.textContent = 'Copied'; btn.classList.add('done');
        setTimeout(function () { btn.textContent = 'Copy'; btn.classList.remove('done'); }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () {});
      } else {
        var ta = document.createElement('textarea');
        ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
        document.body.appendChild(ta); ta.select();
        try { document.execCommand('copy'); done(); } catch (e) {}
        document.body.removeChild(ta);
      }
    });
  });
})();
