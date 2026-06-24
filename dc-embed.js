/* dc-embed.js — Flourish-style scrollytelling loader for the data-center map.
 *
 * Paste into your CMS (survives flattening — it's just one <div> + one external <script src>):
 *
 *   <div class="dc-scroll-embed"></div>
 *   <script src="https://shane-theinfo.github.io/dc-map/dc-embed.js"></script>
 *
 * With no data-src it loads scroll-light.html from the same folder as this script.
 * For the dark version: <div class="dc-scroll-embed" data-theme="dark"></div>
 * Or point anywhere explicitly: <div class="dc-scroll-embed" data-src="https://.../scroll-light.html"></div>
 *
 * The script finds the div, builds a sticky "tractor" section, and forwards the page's
 * scroll position into the graphic so the timeline plays as the reader scrolls — then the
 * article continues underneath. No inline styles or inline scripts for the CMS to strip.
 *
 * Optional data- attributes on the div:
 *   data-scroll="760"      total scroll length, in vh — raise for slower/more resistance (default 760)
 *   data-height="85vh"     graphic height while pinned (default 85vh)
 *   data-max-height="750"  cap on graphic height, in px (default 750)
 *   data-max-width="900"   max graphic width, in px (default 900)
 *   data-top="0"           sticky offset from top, in px — set to your CMS nav-bar height if it has a fixed header
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
    var height   = div.getAttribute('data-height') || '100%';            // fill the pin -> no empty bands
    var maxH     = div.getAttribute('data-max-height') ? parseFloat(div.getAttribute('data-max-height')) + 'px' : 'none';
    var maxW     = (parseFloat(div.getAttribute('data-max-width')) || 1100) + 'px';
    var top      = (parseFloat(div.getAttribute('data-top')) || 0) + 'px';

    // tall section -> sticky stage -> iframe (all built at runtime, so the CMS can't strip it)
    var section = document.createElement('div');
    section.style.position = 'relative';
    section.style.height = scrollVh + 'vh';

    var sticky = document.createElement('div');
    sticky.style.position = 'sticky';
    sticky.style.top = top;
    sticky.style.height = 'calc(100vh - ' + top + ')';
    sticky.style.display = 'flex';
    sticky.style.alignItems = 'center';
    sticky.style.justifyContent = 'center';

    var iframe = document.createElement('iframe');
    iframe.src = src;
    iframe.setAttribute('scrolling', 'no');
    iframe.setAttribute('title', 'Data-center restrictions over time');
    iframe.style.width = '100%';
    iframe.style.maxWidth = maxW;
    iframe.style.height = height;
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
