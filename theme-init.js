/* Apply the saved theme before first paint. */
try {
  var choice = localStorage.getItem('pasteroll-theme');
  if (choice !== 'light' && choice !== 'dark') choice = 'system';
  var light = choice === 'light' || (choice === 'system' && window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches);
  document.documentElement.dataset.theme = light ? 'light' : 'dark';
} catch (error) {}
