/* Pasteroll site: navigation, theme preference and copy controls. No external requests. */
(function () {
  'use strict';
  var root = document.documentElement;
  root.classList.remove('no-js');

  var button = document.querySelector('.menu-button');
  var nav = document.getElementById('site-menu');

  function setMenu(open) {
    if (!button || !nav) return;
    nav.dataset.open = open ? 'true' : 'false';
    button.setAttribute('aria-expanded', String(open));
    var label = button.lastElementChild;
    if (label) label.textContent = open ? 'Close' : 'Menu';
  }

  if (button && nav) {
    setMenu(false);
    button.addEventListener('click', function () {
      setMenu(button.getAttribute('aria-expanded') !== 'true');
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && button.getAttribute('aria-expanded') === 'true') {
        setMenu(false);
        button.focus();
      }
    });
    document.addEventListener('click', function (event) {
      if (button.getAttribute('aria-expanded') !== 'true') return;
      if (!nav.contains(event.target) && !button.contains(event.target)) setMenu(false);
    });
    nav.addEventListener('click', function (event) {
      if (event.target.closest('a')) setMenu(false);
    });
    if (window.matchMedia) {
      var desktop = window.matchMedia('(min-width: 901px)');
      var onChange = function (event) { if (event.matches) setMenu(false); };
      if (desktop.addEventListener) desktop.addEventListener('change', onChange);
      else if (desktop.addListener) desktop.addListener(onChange);
    }
  }

  document.querySelectorAll('.copy').forEach(function (control) {
    control.addEventListener('click', function () {
      var text = control.dataset.copy || '';
      var done = function () {
        control.textContent = 'Copied';
        control.classList.add('done');
        setTimeout(function () { control.textContent = 'Copy'; control.classList.remove('done'); }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () {});
      } else {
        var area = document.createElement('textarea');
        area.value = text;
        area.style.position = 'fixed';
        area.style.opacity = '0';
        document.body.appendChild(area);
        area.select();
        try { document.execCommand('copy'); done(); } catch (error) {}
        document.body.removeChild(area);
      }
    });
  });
})();
