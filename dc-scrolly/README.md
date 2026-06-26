# "The Midwest in the Middle" — scrollytelling data-center map

A scroll-driven version of the data-center map. Built **from** `../dc-map/dark.html`
(originals untouched) by `build_scrolly.py`, which reuses the same embedded data and
render engine, then layers on a sticky map + six scroll "scenes".

## Files
- `scroll-dark.html` / `scroll-light.html` — the graphic (these are what `dc-embed.js` loads)
- `index.html` / `light.html` — same files, for opening directly in a browser
- `dc-embed.js` — the scroll loader (same one used for the other scrolling embeds)
- `build_scrolly.py` — regenerates all of the above from `../dc-map/dark.html`

## The six scenes (match the story)
1. **The Midwest in the Middle** — pans to the Great Lakes states (MN, WI, MI, IL, IN, OH)
2. **Next up, Georgia** — pans to Georgia
3. **No statewide bans passed yet** — zooms back out to the full nation
4. **Rolled-back tax incentives** — highlights **AZ, IL, NJ, OH, OK** in purple `#C998EF`
5. **New electricity-use tax** — highlights **VA** in green `#5AC33E`
6. **Lawsuits lie ahead** — nationwide, 12 pink `#F06FAA` lawsuit markers

Wheel/drag zoom is disabled so page scroll passes through. The graphic is **progress-
driven** (no internal scroll): the host posts `dcScrollProgress {p:0..1}` and the map
maps `p` to the six scenes + card fades — exactly like the other scrolling embeds.

## ⚠️ Data notes on the 12 pink lawsuit markers
Ten of the twelve map to records in the underlying ban dataset. Three need your eye:

| Location | Status in dataset | How it's plotted |
|---|---|---|
| Jessup Borough, PA | **Not in dataset** (nearest record: Olyphant Borough) | plotted by coordinate (≈ −75.563, 41.470) |
| Prince William County, VA | **Not in dataset** (VA has only Warrenton + statewide) | plotted by coordinate (≈ −77.476, 38.701) |
| Saline Township, MI | Dataset has **"Saline City"**, no "Saline Township" | plotted at the township centroid (−83.8386, 42.1245) |

If you can give me the exact lat/lon (or the records) for Jessup and Prince William,
I'll snap the markers to them. The other nine: Commercial Point OH, Cave City KY,
Barren County KY, Chatham County NC, Hawkins County TN, Box Elder County UT,
Port Washington WI, Lordstown OH, and Hill County TX all come straight from the data.

## Embedding — same as the other scrolling pieces
Host this folder, then drop the div + loader into the story (no iframe markup, no
fixed height to manage — `dc-embed.js` builds the pinned stage at runtime):

```html
<div class="dc-scroll-embed" data-theme="dark"></div>
<script src="https://YOUR-HOST/dc-scrolly/dc-embed.js"></script>
```

- `data-theme="dark"` loads `scroll-dark.html`; omit it for `scroll-light.html`.
- Optional `data-scroll="360"` — total scroll runway in vh (raise for a slower scroll).
- Optional `data-top="56"` — sticky offset if your site has a fixed nav bar (px).
- `data-max-width`, `data-height`, `data-max-height` behave as in the other embeds.

`_embedtest.html` in this folder is a local demo of the above (open it directly to
preview the embed with filler text above/below).

Opening `index.html` / `light.html` directly also works — they fall back to driving
the scenes from the page's own scroll.

## Tweaking
Edit `build_scrolly.py` and re-run `python3 build_scrolly.py`:
- Camera targets: `frameStates([...])` calls and the `SCENES` array.
- Highlighted states / colors: `buildStateHi(...)` calls.
- Pink markers: the `PINK` array (`{lon,lat}` = coordinate, `{fips}` = county centroid).
- Card copy: the `.card` blocks in `NEW_BODY`.
- Pacing of fades / map-only gaps: the `0.26` fade fractions in `setProgress`.
