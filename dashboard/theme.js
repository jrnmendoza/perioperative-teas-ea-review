/* Colour theme, applied in <head> before the first paint so the page never flashes the wrong theme.
   Without an explicit choice the system setting (prefers-color-scheme) applies. An explicit choice is kept
   in this browser under one key only; nothing else is stored and nothing is sent anywhere. */
(function () {
  'use strict';
  var KEY = 'teas-ea-review-theme', root = document.documentElement;
  var media = window.matchMedia ? window.matchMedia('(prefers-color-scheme: light)') : null;
  function stored() { try { var v = window.localStorage.getItem(KEY); return v === 'light' || v === 'dark' ? v : null; } catch (e) { return null; } }
  function system() { return media && media.matches ? 'light' : 'dark'; }
  var initial = stored();
  if (initial) root.setAttribute('data-theme', initial);
  window.reviewTheme = {
    // The theme in effect: the explicit choice if there is one, else the system setting.
    current: function () { return root.getAttribute('data-theme') || system(); },
    set: function (theme) {
      if (theme !== 'light' && theme !== 'dark') return;
      root.setAttribute('data-theme', theme);
      try { window.localStorage.setItem(KEY, theme); } catch (e) { /* storage blocked: the choice lasts for this page only */ }
    },
    onSystemChange: function (fn) { if (media && media.addEventListener) media.addEventListener('change', fn); }
  };
})();
