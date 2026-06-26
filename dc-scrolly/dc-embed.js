/* dc-embed.js — scroll-driven embed loader for the data-center time-lapse map.
 *
 *   <div class="dc-scroll-embed"></div>
 *   <script src="https://shane-theinfo.github.io/dc-map/dc-embed.js"></script>
 *
 * With no data-src it loads scroll-light.html from the same folder as this script;
 * use data-theme="dark" for scroll-dark.html, or data-src="..." to point anywhere.
 *
 * Optional data- attributes on the div:
 *   data-scroll   total scroll length, in vh (raise for a slower scroll)
 *   data-height   graphic height while pinned
 *   data-max-height / data-max-width   caps, in px
 *   data-top      sticky offset from top, in px (set to a fixed nav-bar height)
 */
(function () {
  // URL of this script, so we can default to scroll-light.html sitting next to it
  var SELF = (document.currentScript && document.currentScript.src) || '';

  function build(div) {
    if (div.__dcReady) return;
    div.__dcReady = true;

    // data-src wins; otherwise load scroll-light.html (or scroll-dark.html via data-theme="dark")
    // from the same folder as this script
    var src = div.getAttribute('data-src');
    if (!src && SELF) {
      var file = div.getAttribute('data-theme') === 'dark' ? 'scroll-dark.html' : 'scroll-light.html';
      src = SELF.replace(/[^/]*(?:\?.*)?$/, file);
    }
    if (!src) return;
    var scrollVh = parseFloat(div.getAttribute('data-scroll')) || 320;   // shorter runway by default
    var height   = div.getAttribute('data-height') || '700px';           // graphic height — a centered band, NOT full viewport
    var maxH     = div.getAttribute('data-max-height') ? parseFloat(div.getAttribute('data-max-height')) + 'px' : '100%';
    var maxW     = (parseFloat(div.getAttribute('data-max-width')) || 1100) + 'px';
    var top      = (parseFloat(div.getAttribute('data-top')) || 0) + 'px';

    // tall section -> sticky stage -> iframe (all built at runtime, so the CMS can't strip it)
    var section = document.createElement('div');
    section.style.position = 'relative';
    section.style.height = scrollVh + 'vh';

    var sticky = document.createElement('div');
    sticky.style.position = 'sticky';
    sticky.style.top = top;
    sticky.style.height = 'calc(100vh - ' + top + ')';   // full pin area; the graphic centers within it
    sticky.style.display = 'flex';
    sticky.style.alignItems = 'center';
    sticky.style.justifyContent = 'center';

    var iframe = document.createElement('iframe');
    iframe.src = src;
    iframe.setAttribute('scrolling', 'no');
    iframe.setAttribute('title', 'Data-center restrictions over time');
    iframe.style.width = '100%';
    iframe.style.maxWidth = maxW;
    iframe.style.height = height;              // graphic height — centered band
    iframe.style.maxHeight = maxH;
    iframe.style.border = '0';
    iframe.style.display = 'block';

    sticky.appendChild(iframe);
    section.appendChild(sticky);
    div.appendChild(section);

    // forward scroll position (0..1 through the section) into the graphic
    var last = -1;
    function post() {
      var total = section.offsetHeight - window.innerHeight;
      var p = total > 0 ? Math.min(1, Math.max(0, -section.getBoundingClientRect().top / total)) : 0;
      if (p === last) return;
      last = p;
      if (iframe.contentWindow) iframe.contentWindow.postMessage({ type: 'dcScrollProgress', p: p }, '*');
    }
    window.addEventListener('scroll', post, { passive: true });
    window.addEventListener('resize', post);
    iframe.addEventListener('load', function () { post(); setTimeout(post, 250); });
  }

  function boot() {
    var nodes = document.querySelectorAll('.dc-scroll-embed');
    for (var i = 0; i < nodes.length; i++) build(nodes[i]);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
