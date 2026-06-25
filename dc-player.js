/* dc-player.js — standalone loader for the data-center time-lapse PLAYER:
 * a plain fixed-height box with a top scrubber + play/pause that auto-starts when scrolled into view.
 * Separate from dc-embed.js (the scrollytelling loader) so it can be tested in isolation.
 *
 *   <div class="dc-player-embed"></div>
 *   <script src="https://shane-theinfo.github.io/dc-map/dc-player.js"></script>
 *
 * Optional on the div:
 *   data-theme="dark"      load player-dark.html
 *   data-height="720px"    box height
 *   data-max-width="1100"  max width, px
 *   data-start="75"        percent of the box visible before it plays ("75", "0.75"), or "bottom"
 *                          to wait until the bar chart (bottom of the box) scrolls in. Default 75%.
 */
(function () {
  // URL of this script, so we can default to player-light.html sitting next to it
  var SELF = (document.currentScript && document.currentScript.src) || '';

  function build(div) {
    if (div.__dcReady) return;
    div.__dcReady = true;

    var src = div.getAttribute('data-src');
    if (!src && SELF) {
      var file = div.getAttribute('data-theme') === 'dark' ? 'player-dark.html' : 'player-light.html';
      src = SELF.replace(/[^/]*(?:\?.*)?$/, file);
    }
    if (!src) return;

    var height = div.getAttribute('data-height') || '720px';
    var maxW   = (parseFloat(div.getAttribute('data-max-width')) || 1100) + 'px';

    var iframe = document.createElement('iframe');
    iframe.src = src;
    iframe.setAttribute('scrolling', 'no');
    iframe.setAttribute('loading', 'lazy');
    iframe.setAttribute('title', 'Data-center restrictions over time');
    iframe.style.cssText = 'display:block;width:100%;max-width:' + maxW + ';height:' + height + ';border:0;margin:0 auto';
    div.appendChild(iframe);

    var started = false;
    function start() {
      if (started) return; started = true;
      function go() { if (iframe.contentWindow) iframe.contentWindow.postMessage({ type: 'dcPlay' }, '*'); }
      go();                                          // post now...
      iframe.addEventListener('load', go);           // ...and again once it's loaded (covers slow loads)
    }
    function observe(target, frac) {
      if ('IntersectionObserver' in window) {
        var io = new IntersectionObserver(function (es) {
          es.forEach(function (en) { if (en.isIntersecting) { start(); io.disconnect(); } });
        }, { threshold: frac });
        io.observe(target);
      } else {
        iframe.addEventListener('load', function () { setTimeout(start, 400); });
      }
    }

    var startAt = (div.getAttribute('data-start') || '75').trim().toLowerCase();
    if (startAt === 'bottom') {                      // robust even when the box is taller than the viewport
      var sentinel = document.createElement('div');
      sentinel.style.cssText = 'width:100%;height:1px';
      div.appendChild(sentinel);
      observe(sentinel, 0);
    } else {
      var frac = parseFloat(startAt); if (isNaN(frac)) frac = 50;
      if (frac > 1) frac = frac / 100;               // "50" / "50%" -> 0.5
      observe(iframe, Math.max(0, Math.min(1, frac)));
    }
  }

  function boot() {
    var nodes = document.querySelectorAll('.dc-player-embed');
    for (var i = 0; i < nodes.length; i++) build(nodes[i]);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
