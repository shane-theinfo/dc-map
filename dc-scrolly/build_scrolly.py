#!/usr/bin/env python3
"""
Build the "Midwest in the Middle" scrollytelling map from the existing
dark.html, WITHOUT editing any original file.

Reuses the embedded DB data + render engine verbatim and layers on a sticky
map + six scroll "scenes" matching the story:

  1. Pan to the Great Lakes states              ("The Midwest in the Middle")
  2. Pan to Georgia                              ("Next up, Georgia")
  3. Zoom out to the full nation                 ("No statewide bans passed yet")
  4. Highlight AZ, IL, NJ, OH, OK  purple #C998EF (rolled-back tax incentives)
  5. Highlight VA only             green  #5AC33E (new electricity-use tax)
  6. Nationwide pink markers       pink   #F06FAA (12 lawsuit locations)

Outputs index.html (dark) and light.html.
"""
import re, sys, pathlib

SRC = pathlib.Path.home() / "Desktop/GitHub/dc-map/dark.html"
OUT = pathlib.Path(__file__).resolve().parent

text = SRC.read_text(encoding="utf-8")

m = re.search(r'<img class="logo"[^>]*>', text)
if not m:
    sys.exit("could not find logo img tag")
LOGO = m.group(0)

# ---------------------------------------------------------------------------
# 1. scrollytelling CSS
# ---------------------------------------------------------------------------
SCROLLY_CSS = r"""
  /* ===================== progress-driven scrollytelling stage ===================== */
  html,body{height:auto}
  body.dark{background:#2F3538}
  #story{position:relative;margin:0;padding:0}

  /* the graphic is a fixed-height stage; dc-embed.js pins it and posts progress */
  #stage{position:sticky;top:0;height:100vh;height:100dvh;display:flex;flex-direction:column;
    align-items:center;justify-content:center;overflow:hidden}
  #stage #wrap{min-height:0;height:auto;max-width:820px;width:100%;padding:14px 18px;justify-content:center}
  #stage #mapbox{margin-top:6px}
  #stage svg.map{max-height:62vh}
  #sheet{display:none!important}                 /* uses the floating tip only */
  #stage .foot{position:static;background:none;text-align:left;margin-top:8px;padding:6px 0 0}

  /* standalone scroll runway (hidden once a host drives progress) */
  #spacer{height:560vh}

  /* story cards overlay the stage; one shown at a time, opacity driven by progress */
  #cards{position:absolute;inset:0;pointer-events:none;z-index:3}
  .card{position:absolute;left:50%;bottom:7vh;transform:translateX(-50%) translateY(18px);
    width:calc(100% - 40px);max-width:500px;max-height:80%;overflow-y:auto;overscroll-behavior:contain;
    pointer-events:auto;opacity:0;will-change:opacity,transform;
    background:rgba(255,255,255,.94);backdrop-filter:blur(5px);-webkit-backdrop-filter:blur(5px);
    border:1px solid rgba(20,24,30,.10);border-radius:13px;padding:17px 20px 18px;
    box-shadow:0 12px 40px rgba(20,24,30,.20)}
  /* card color-keys match the map legend keys (same font + swatch) */
  .card .tag{display:inline-flex;align-items:center;
    font-family:'Suisse Screen SemiBold',-apple-system,Arial,sans-serif;
    font-size:14px;color:#3b3f45;margin:0 0 8px}
  .card .tag .sw{width:14px;height:14px;border-radius:50%;margin-right:7px;box-shadow:0 0 0 1px #fff inset}
  .card h3{font-family:'Suisse Works',Georgia,serif;font-weight:600;font-size:21px;line-height:1.2;margin:0 0 9px;color:#1a1a1a}
  .card p{font-family:'Suisse Screen',-apple-system,Arial,sans-serif;font-size:15px;line-height:1.52;color:#41464c;margin:0 0 9px}
  .card p:last-child{margin-bottom:0}

  body.dark .card{background:rgba(28,33,36,.92);border-color:rgba(255,255,255,.15);box-shadow:0 12px 40px rgba(0,0,0,.5)}
  body.dark .card .tag{color:#fff}
  body.dark .card h3{color:#fff}
  body.dark .card p{color:#d2d6d9}

  @media (max-width:479px){
    #stage{justify-content:flex-start}
    #stage #wrap{padding:10px 12px 0}
    #stage .legend{padding-bottom:8px;margin-bottom:2px}
    #stage .lg-lab{font-size:11px}
    #stage .key{font-size:13px}
    #stage svg.map{max-height:54vh}
    .card{bottom:4vh;width:calc(100% - 24px);max-width:none;padding:13px 15px;max-height:46%}
    .card h3{font-size:17px;margin-bottom:7px}
    .card p{font-size:14px;line-height:1.48;margin-bottom:7px}
    .card .tag{font-size:13px}
  }
"""
assert "</style>" in text
text = text.replace("</style>", SCROLLY_CSS + "\n</style>", 1)

# ---------------------------------------------------------------------------
# 2. body markup — 6 story steps, real copy
# ---------------------------------------------------------------------------
NEW_BODY = f"""<body class="dark">
<main id="story">
  <div id="stage">
    <div id="wrap">
      <div class="legend">
        <div class="lg-group" id="statusKeys"><span class="lg-lab">Ban status</span></div>
        <div class="lg-group" id="levelKeys"><span class="lg-lab">Level</span></div>
      </div>
      <div id="mapbox">
        <svg class="map" id="map"></svg>
        <div id="zoom">
          <button id="zin" title="Zoom in">+</button>
          <button id="zout" title="Zoom out">&minus;</button>
        </div>
        <div id="tip"></div>
      </div>
      <div id="sheet"></div>
      <div class="foot" id="foot">Notes: As of June 24. No entries in Hawaii or Alaska. &bull; Map: Shane Burke &bull; Source: The Information reporting, public records, local news sources</div>
    </div>

    <div id="cards">
      <div class="card" data-scene="0">
        <h3>The Midwest in the Middle</h3>
        <p>Developers are increasingly choosing the Midwest for hyperscale projects, drawn by cheap, flat farmland and business-friendly officials eager to court them. Some of the largest campuses from Amazon, Meta Platforms, OpenAI, Anthropic and Oracle call the region home.</p>
        <p>So does the fiercest pushback. There are more than 100 active bans across the Great Lakes states. Our original piece broke down a Michigan fight over OpenAI and Oracle&rsquo;s Stargate project that spawned a ring of bans in nearby towns. Because zoning laws vary, some states impose county-level bans while others favor local ones.</p>
      </div>

      <div class="card" data-scene="1">
        <h3>Next up, Georgia</h3>
        <p>The South is also drawing hyperscalers, and Georgia is a top destination. The New York Times reported this month on the state&rsquo;s infrastructure buildout, with public utility companies using eminent domain to force rural landowners to sell parcels to build power lines.</p>
        <p>Opposition is bipartisan, with right-wing critics focusing mostly on energy prices, and left-wing ones bringing up environmental concerns, too.</p>
        <p>Now, 18 active bans span Georgia, including entire counties. Most are pausing applications while localities draft codes to deal with the issue.</p>
      </div>

      <div class="card" data-scene="2">
        <h3>No statewide bans passed yet, but some are taking other approaches</h3>
        <p>This movement is finding success from the bottom up, at small levels of government rather than state or nationwide. Some moratoriums have cleared state legislatures but stalled: In April, Maine Gov. Janet Mills vetoed a bill for a moratorium pausing large data centers until November 2027. In New York, a similar measure awaits a decision from Gov. Kathy Hochul.</p>
      </div>

      <div class="card" data-scene="3">
        <span class="tag"><span class="sw" style="background:#C998EF"></span>Rolled back tax incentives</span>
        <p>That&rsquo;s not to say other states aren&rsquo;t heeding constituent concerns. Some are taking a different tack, asking more of the developers that want to call their states home. Arizona, Illinois, New Jersey, Ohio and Oklahoma have rolled back tax incentives for data centers, and other states are considering similar actions.</p>
      </div>

      <div class="card" data-scene="4">
        <span class="tag"><span class="sw" style="background:#5AC33E"></span>New electricity-use tax</span>
        <p>This week in Virginia, home to a region nicknamed Data Center Alley, lawmakers voted to tax data centers for their electricity use up to $600 million annually. Politico reports the governor is likely to sign: Just days ago, she called an energy consumption tax on data centers &ldquo;an idea I first proposed this spring.&rdquo;</p>
      </div>

      <div class="card" data-scene="5">
        <span class="tag"><span class="sw" style="background:#F06FAA"></span>Facing lawsuits</span>
        <h3>Lawsuits lie ahead</h3>
        <p>Even the permanent bans aren&rsquo;t airtight. Some developers have challenged them in court, leading areas to downgrade or rescind them outright. In our original piece, we broke down how lawsuits in Saline Township, Mich., and Lordstown, Ohio, shaped local organizing strategies. In Texas, Hill County rescinded its moratorium after a developer sued.</p>
        <p>More than a dozen suits are now pending nationwide, with developers threatening more.</p>
      </div>
    </div>
  </div>

  <div id="spacer"></div>
</main>"""

bstart = text.index('<body class="dark">')
smark = text.index('\n<script>')
text = text[:bstart] + NEW_BODY + text[smark:]

# ---------------------------------------------------------------------------
# 3. relax zoom translate extent so we can frame any region
# ---------------------------------------------------------------------------
old_ext = ".translateExtent([[0,0],[W,HMAP]])"
new_ext = ".translateExtent([[-W,-HMAP],[2*W,2*HMAP]])"
assert old_ext in text
text = text.replace(old_ext, new_ext, 1)

# ---------------------------------------------------------------------------
# 4. disable the auto-height postMessage (fixed-height iframe embed)
# ---------------------------------------------------------------------------
old_post = "parent.postMessage({type:'dcMapHeight',height:h}, '*');"
assert old_post in text
text = text.replace(old_post, "void h; /* scrolly: fixed-height embed, no auto-resize */", 1)

# ---------------------------------------------------------------------------
# 5. scrolly controller appended before the last </script>
# ---------------------------------------------------------------------------
SCROLLY_JS = r"""

// ===================== scrollytelling controller =====================
// Disable user wheel/drag zoom so page scroll passes through (+/- still work).
svg.on('wheel.zoom',null).on('dblclick.zoom',null).on('mousedown.zoom',null)
   .on('pointerdown.zoom',null)
   .on('touchstart.zoom',null).on('touchmove.zoom',null).on('touchend.zoom',null);

const DUR = 1200, EASE = d3.easeCubicInOut;

// ---- camera ----
function flyHome(){
  svg.transition().duration(DUR).ease(EASE).call(zoom.transform, d3.zoomIdentity);
}
function frameStates(abbrs, pad){
  pad = (pad==null)?0.14:pad;
  const fs = abbrs.map(a=>stFeat[a]).filter(Boolean);
  if(!fs.length) return flyHome();
  let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;
  fs.forEach(f=>{ const b=path.bounds(f);
    if(b[0][0]<x0)x0=b[0][0]; if(b[0][1]<y0)y0=b[0][1];
    if(b[1][0]>x1)x1=b[1][0]; if(b[1][1]>y1)y1=b[1][1]; });
  const bw=Math.max(1,x1-x0), bh=Math.max(1,y1-y0);
  let k=Math.min(W/(bw*(1+2*pad)), HMAP/(bh*(1+2*pad)));
  k=Math.max(1, Math.min(k,16));
  const cx=(x0+x1)/2, cy=(y0+y1)/2;
  const t=d3.zoomIdentity.translate(W/2,HMAP/2).scale(k).translate(-cx,-cy);
  svg.transition().duration(DUR).ease(EASE).call(zoom.transform, t);
}

// ---- whole-state highlight layers (purple, green) ----
function buildStateHi(group, abbrs, fill, stroke){
  group.selectAll('path').data(abbrs.filter(a=>stFeat[a])).join('path')
    .attr('d', a=>path(stFeat[a]))
    .attr('fill',fill).attr('fill-opacity',0)
    .attr('stroke',stroke).attr('stroke-opacity',0).attr('stroke-width',1.4)
    .attr('vector-effect','non-scaling-stroke');
}
const gPurple = root.append('g').attr('pointer-events','none');
const gGreen  = root.append('g').attr('pointer-events','none');
buildStateHi(gPurple, ['AZ','IL','NJ','OH','OK'], '#C998EF', '#9b59d0');
buildStateHi(gGreen,  ['VA'],                     '#5AC33E', '#3f9e29');
function toggleStateHi(group,on,op){
  group.selectAll('path').transition().duration(650)
    .attr('fill-opacity', on?(op||0.6):0).attr('stroke-opacity', on?0.9:0);
}

// ---- pink lawsuit markers (12 locations) ----
// {lon,lat} = plotted by coordinate; {fips} = county polygon centroid.
// NOTE: Jessup Borough PA and Prince William County VA are NOT in the ban
// dataset; they are plotted by known coordinate. Saline Township is plotted at
// its civil-township centroid (the dataset's only Saline record is "Saline City").
const PINK = [
  {lon:-83.019, lat:39.789},  // Commercial Point, OH
  {lon:-85.964, lat:37.139},  // Cave City, KY
  {lon:-85.477, lat:37.667},  // Barren County, KY (planning commission)
  {fips:'37037'},             // Chatham County, NC
  {fips:'47073'},             // Hawkins County, TN
  {lon:-75.563, lat:41.470},  // Jessup Borough, PA  (not in dataset)
  {fips:'49003'},             // Box Elder County, UT
  {lon:-77.476, lat:38.701},  // Prince William County, VA  (not in dataset)
  {lon:-87.869, lat:43.389},  // Port Washington, WI
  {lon:-80.921, lat:41.036},  // Lordstown, OH
  {fips:'48217'},             // Hill County, TX
  {lon:-83.8386, lat:42.1245}, // Saline Township, MI (civil township, not Saline City)
];
const regByFips={}; DB.regions.features.forEach(f=>{ regByFips[f.properties.fips]=f; });
function pinkXY(d){
  if(d.lon!=null) return proj([d.lon,d.lat]);
  const f=regByFips[d.fips]; return f?path.centroid(f):null;
}
const gPink = root.append('g').attr('pointer-events','none').attr('opacity',0);
gPink.selectAll('g.pink').data(PINK).join('g').attr('class','pink').each(function(d){
  const xy=pinkXY(d); if(!xy) return;
  const s=d3.select(this).attr('transform',`translate(${xy[0]},${xy[1]})`);
  s.append('circle').attr('r',9).attr('fill','#F06FAA').attr('fill-opacity',.18);   // soft halo
  s.append('circle').attr('r',6).attr('fill','#fff');                               // white ring
  s.append('circle').attr('r',4.6).attr('fill','#F06FAA').attr('stroke','#b03a6e').attr('stroke-width',.8);
});
function togglePink(on){ gPink.transition().duration(650).attr('opacity', on?1:0); }

function clearHi(){ toggleStateHi(gPurple,false); toggleStateHi(gGreen,false); togglePink(false); }

// show/hide the regular ban marks (state washes, county regions, city points).
// The lawsuits scene hides them so only the pink markers read on the base map.
function showData(on){
  [gWash,gReg,gPt].forEach(g=>{
    g.transition().duration(500).attr('opacity', on?1:0);
    g.attr('pointer-events', on?null:'none');   // hidden marks must not catch hover/tooltips
  });
  if(!on && typeof killTip==='function') killTip();
}

// ---- scenes ----
const GREAT_LAKES = ['WI','MI','IL','IN','OH'];   // core five, a little room outside
const SCENES = [
  ()=>{ clearHi(); frameStates(GREAT_LAKES, 0.07); },                 // 0 Midwest (tight)
  ()=>{ clearHi(); frameStates(['GA'], 0.22); },                      // 1 Georgia (tight)
  ()=>{ clearHi(); flyHome(); },                                      // 2 zoom out
  ()=>{ toggleStateHi(gGreen,false); togglePink(false); flyHome(); toggleStateHi(gPurple,true,0.58); }, // 3 purple
  ()=>{ toggleStateHi(gPurple,false); togglePink(false); flyHome(); toggleStateHi(gGreen,true,0.62); }, // 4 green VA
  ()=>{ toggleStateHi(gPurple,false); toggleStateHi(gGreen,false); flyHome(); togglePink(true); },      // 5 pink
];
let curScene=-1;
function goScene(i){ if(i===curScene) return; curScene=i; showData(i!==5); SCENES[i](); }

// ---- progress-driven playback (matches dc-embed.js: host posts dcScrollProgress {p:0..1}) ----
const cards = Array.from(document.querySelectorAll('#cards .card'));
const N = SCENES.length;
function setProgress(p){
  p = Math.max(0, Math.min(1, p));
  const i = Math.min(N-1, Math.floor(p*N));
  goScene(i);
  const local = p*N - i;                       // 0..1 within the current scene's band
  // fade the card in over the first ~26% and out over the last ~26% of its band,
  // leaving a map-only beat before and after each box
  let op = local<0.26 ? local/0.26 : local>0.74 ? (1-local)/0.26 : 1;
  op = Math.max(0, Math.min(1, op));
  cards.forEach((c,idx)=>{
    if(idx===i){ c.style.opacity = op; c.style.transform = `translateX(-50%) translateY(${(1-op)*18}px)`; }
    else if(c.style.opacity!=='0'){ c.style.opacity = '0'; }
  });
}

// Parent-driven mode: dc-embed.js pins this iframe and posts scroll progress.
let externallyDriven = false;
window.addEventListener('message', e=>{
  const d = e.data; if(!d || typeof d!=='object') return;
  if(d.type==='dcScrollProgress' && typeof d.p==='number'){
    if(!externallyDriven){
      externallyDriven = true;
      const sp=document.getElementById('spacer'); if(sp) sp.style.display='none';
      const st=document.getElementById('stage'); if(st) st.style.position='relative';
    }
    setProgress(d.p);
  }
});

// Standalone fallback: when opened directly (not embedded), drive from window scroll.
function readScroll(){ const max=document.documentElement.scrollHeight-window.innerHeight; return max>0? window.scrollY/max : 0; }
window.addEventListener('scroll', ()=>{ if(!externallyDriven) setProgress(readScroll()); }, {passive:true});
window.addEventListener('resize', ()=>{ if(!externallyDriven) setProgress(readScroll()); });
setProgress(0);
"""

last = text.rfind("</script>")
assert last != -1
text = text[:last] + SCROLLY_JS + "\n" + text[last:]

dark  = text
light = text.replace('<body class="dark">', '<body>', 1)

# dc-embed.js defaults to scroll-light.html / scroll-dark.html next to the script,
# so emit those names; index.html / light.html are the same files for direct viewing.
(OUT / "scroll-dark.html").write_text(dark,  encoding="utf-8")
(OUT / "scroll-light.html").write_text(light, encoding="utf-8")
(OUT / "index.html").write_text(dark,  encoding="utf-8")
(OUT / "light.html").write_text(light, encoding="utf-8")

# bring the existing loader alongside so the embed works the same way as the others
EMBED_SRC = pathlib.Path.home() / "Desktop/GitHub/dc-map/dc-embed.js"
if EMBED_SRC.exists():
    (OUT / "dc-embed.js").write_text(EMBED_SRC.read_text(encoding="utf-8"), encoding="utf-8")

print("wrote scroll-dark.html, scroll-light.html, index.html, light.html, dc-embed.js")
print("dark size:", (OUT/'scroll-dark.html').stat().st_size, "bytes")
