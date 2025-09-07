/*
Integration (Hugo Pipes):
- In head or footer (recommended footer before </body>):
  {{ $fortressJS := resources.Get "js/fortress-ui.js" | resources.Minify | resources.Fingerprint }}
  <script defer src="{{ $fortressJS.RelPermalink }}" integrity="{{ $fortressJS.Data.Integrity }}" crossorigin="anonymous"></script>
- Include CSS in head:
  {{ $fortressCSS := resources.Get "css/fortress.css" | resources.Minify | resources.Fingerprint }}
  <link rel="stylesheet" href="{{ $fortressCSS.RelPermalink }}" integrity="{{ $fortressCSS.Data.Integrity }}" crossorigin="anonymous">
- Render cards inside your template:
  {{ partial "fortress-cards.html" . }}
*/

(function () {
  var d = document.documentElement;
  d.classList.add('js-enabled');

  // ThemeManager: auto by local hour with manual override, fallback safe if storage blocked
  var ThemeManager = (function () {
    var KEY = 'theme';
    function getHourTheme() {
      var h = new Date().getHours();
      return (h >= 6 && h < 18) ? 'light' : 'dark';
    }
    function safeGet() {
      try { return localStorage.getItem(KEY); } catch (e) { return null; }
    }
    function safeSet(val) {
      try { localStorage.setItem(KEY, val); } catch (e) { /* noop */ }
    }
    function apply(t) {
      document.documentElement.setAttribute('data-theme', t);
      document.documentElement.style.colorScheme = t;
    }
    function init() {
      var stored = safeGet();
      var theme = (stored === 'light' || stored === 'dark') ? stored : getHourTheme();
      apply(theme);
      return theme;
    }
    function toggle() {
      var cur = document.documentElement.getAttribute('data-theme') || getHourTheme();
      var next = cur === 'light' ? 'dark' : 'light';
      safeSet(next);
      apply(next);
      return next;
    }
    return { init: init, toggle: toggle };
  })();

  ThemeManager.init();

  // Accessible accordion: progressive enhancement
  var headers = Array.prototype.slice.call(document.querySelectorAll('.card-toggle'));
  var bodies = Array.prototype.slice.call(document.querySelectorAll('.card-body'));

  // Default collapsed when JS is on
  bodies.forEach(function (el) { el.classList.add('is-collapsed'); el.style.height = '0px'; el.setAttribute('aria-hidden', 'true'); });

  function setExpanded(toggle, expanded) {
    toggle.setAttribute('aria-expanded', String(expanded));
  }

  function animateHeight(el, expand) {
    var prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var start = el.getBoundingClientRect().height;
    el.classList.add('collapsing');
    el.style.height = 'auto';
    var end = el.getBoundingClientRect().height;
    if (!expand) { var tmp = start; start = end; end = 0; }
    el.style.height = start + 'px';
    // Force reflow
    el.offsetHeight; // eslint-disable-line no-unused-expressions
    if (prefersReduced) {
      el.style.height = expand ? end + 'px' : '0px';
      finish();
      return;
    }
    el.style.height = end + 'px';
    function finish() {
      el.classList.remove('collapsing');
      if (expand) {
        el.classList.remove('is-collapsed');
        el.style.height = 'auto';
        el.removeAttribute('aria-hidden');
      } else {
        el.classList.add('is-collapsed');
        el.style.height = '0px';
        el.setAttribute('aria-hidden', 'true');
      }
    }
    el.addEventListener('transitionend', function te(e) {
      if (e.propertyName === 'height') {
        el.removeEventListener('transitionend', te);
        finish();
      }
    });
  }

  function getBodyFor(toggle) {
    var id = toggle.getAttribute('aria-controls');
    return id ? document.getElementById(id) : null;
  }

  function onActivate(toggle) {
    var body = getBodyFor(toggle);
    if (!body) return;
    var expanded = toggle.getAttribute('aria-expanded') === 'true';
    setExpanded(toggle, !expanded);
    animateHeight(body, !expanded);
  }

  headers.forEach(function (toggle, idx) {
    // Ensure min touch target
    toggle.style.minHeight = '44px';
    toggle.addEventListener('click', function () { onActivate(toggle); });
    toggle.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onActivate(toggle); }
      // Optional: arrow key navigation between headers
      if (e.key === 'ArrowDown') { e.preventDefault(); var n = headers[idx + 1]; if (n) n.focus(); }
      if (e.key === 'ArrowUp') { e.preventDefault(); var p = headers[idx - 1]; if (p) p.focus(); }
    });
  });
})();
