/* Applies the saved theme before the page paints (no flash). Kept tiny and separate so the page
   can run with a strict Content-Security-Policy (no inline scripts). */
try {
  var t = localStorage.getItem('pasteroll-theme');
  if (t) document.documentElement.dataset.theme = t;
} catch (e) {}
