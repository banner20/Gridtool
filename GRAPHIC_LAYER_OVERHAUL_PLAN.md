# GRID — Graphic Layer Overhaul: Handoff Plan for Next Agent

> **Read this whole document before touching code.** It contains the architecture,
> the exact pending task, file locations, function/line anchors, and critical
> warnings (including a data-loss incident). It is written to be executed by an AI
> coding agent with minimal re-discovery.

---

## 0. TL;DR — what you are doing

The app has **two layer types**: `visual` (generative grid visualizer) and
`graphic` (element-based flyer/design layer). The visual layer uses the shared
**top-tab ecosystem** (grid / color / motion / fx / lfo / audio) and any numeric
param can be driven by **LFO** or **audio routing**. The graphic layer currently
has its **own self-contained panel** with in-panel sub-tabs and **per-element
audio-reactivity bolted on** — this is inconsistent and the user rejected it.

**Your job: re-architect the graphic layer to live in the SAME ecosystem as the
visual layer.** Specifically (these were confirmed by the user):

1. **Reuse & relabel the top tabs** for graphic layers (no in-panel sub-tabs):
   - `grid` tab → **"elements"** → element list + add buttons + canvas/bg + the
     selected element's **transform** (pos/size/rotate/blend/opacity).
   - `color` tab → **"style"** → the selected element's **design** (type-specific
     panel: content, fill, stroke, shadow, glow, etc.).
   - `motion` tab → **"motion"** → the selected element's **motion presets**.
   - `fx` tab → **hidden** for graphic layers.
   - `lfo` tab → **works on element properties** (shared system).
   - `audio` tab → **works on element properties** (shared system).
   - **Remove** the dedicated `✦` graphic tab (`#ptab-graphic`).
2. **Move per-element motion presets** (float/spin/pulse/marquee...) into the
   **Motion top-tab** (currently inline in the element panel).
3. **Remove per-element "audio reactive"** UI (react / affects / react-amt). Audio
   reactivity must instead come from the **Audio tab routing to element props**.
4. **Audio + LFO must drive graphic element properties** through the shared
   Audio/LFO tabs, using **BOTH**:
   - **Route to selected element** via the tab's dropdown (pick element prop).
   - **Right-click an element-property slider → "send to audio (bass/mid/high)"
     and "add LFO"** (mirrors the existing right-click on visual sliders).

---

## 1. Files & locations

| Thing | Path |
|---|---|
| **Main working file (EDIT THIS)** | `C:\Users\Asus\Downloads\GRIDTOOL claude handoff\grid-tool WORKING COPY.html` |
| Timestamped backups (safety) | `C:\Users\Asus\Downloads\GRIDTOOL claude handoff\grid-tool BACKUP <YYYYMMDD-HHMM>.html` |
| Old April backup (last resort) | `C:\Users\Asus\Downloads\GridTool\grid-tool WORKING COPY.html` |
| Full session transcript (every edit) | `C:\Users\Asus\.claude\projects\C--Users-Asus-Downloads-GRIDTOOL-claude-handoff\b844532c-df2f-4023-b898-e35a9f6a2370.jsonl` |
| Local preview launch config | `.claude/launch.json` (python http.server on port 7823) |

**The file is a single self-contained HTML** (~759 KB, ~14,440 lines) with all
CSS in one `<style>`, all HTML, and all JS in one trailing `<script>` ending with
`loop();`. There is **no build step**; open the HTML directly or serve it.

---

## 2. ⚠️ CRITICAL WARNINGS

### 2a. The file is too big — context will run out
- 759 KB / ~14,440 lines in ONE file. **Do NOT read the whole file.** Use
  `grep`/Grep with line numbers, then `Read` with `offset`/`limit` on just the
  region you need. Every edit should be surgical (`Edit` with a unique
  `old_string`), never a full-file rewrite.
- **Plan your edits before reading.** Budget context: locate anchors with grep,
  read ±30 lines, edit, move on.

### 2b. DISK SPACE caused total data loss once — check before large writes
- The C: drive was at **99–100% full (~3 GB free)**. A `Write` failed mid-stream
  with `ENOSPC` and **truncated the working file to 0 bytes**, destroying a full
  session of work. It was recovered by replaying 106 edits from the JSONL
  transcript onto the April backup.
- **Before starting: run `df -h C:` (or check free space). Ensure ≥ several GB
  free.** Make a timestamped backup before each work session:
  `cp "grid-tool WORKING COPY.html" "grid-tool BACKUP $(date +%Y%m%d-%H%M).html"`
- Prefer many small `Edit`s over giant `Write`s (smaller write = less corruption risk).

### 2c. Verifying changes
- A local preview server runs via the MCP `preview_*` tools (python http.server on
  :7823, file `grid-tool%20WORKING%20COPY.html`). The **screenshot tool was flaky
  / hung** in the last session — fall back to `preview_eval` to (a) call
  `compositeAll()` and catch errors, (b) sample canvas pixels via
  `getImageData` to confirm shapes/text drew, (c) inspect `globalT` to confirm the
  loop runs. `requestAnimationFrame` pauses when the preview tab is backgrounded,
  so `globalT` "stuck" is usually NOT a bug — call `loop()` once or
  `compositeAll()` manually to verify.

### 2d. Consider componentizing FIRST (optional but recommended)
The single-file size is the root cause of context pain. Two options:
- **Option A (recommended for dev velocity):** Extract the JS into an external
  `grid-tool.js` and CSS into `grid-tool.css`, referenced via `<script src>` /
  `<link>`. Then future edits touch a smaller surface and the agent can read just
  the JS. **BUT** the user values a single portable HTML for distribution — if you
  do this, also provide a tiny build/inline step (or a `dist` single-file build).
  Confirm with the user before splitting.
- **Option B (no split):** Keep single file; just work surgically. Lower risk,
  slower. Default to this unless the user approves a split.

---

## 3. Current architecture (as-is)

### 3a. Layer model
- Global `layers[]`, `selectedLayer` index. Each layer object from
  `defaultLayerParams()`.
- `layer.layerType` = `'visual'` (default) or `'graphic'`.
- **Visual params** are flat numerics on the layer: `layer.cols`, `layer.hueShift`,
  `layer.speed`, etc.
- **Graphic content** lives in `layer.gfxElements[]` (array of element objects) plus
  layer-level graphic settings: `gfxBg`, `gfxBgColor`, `gfxBgColor2`, `gfxBgAngle`,
  `gfxCanvasPad`, `gfxFrame`, `gfxFrameColor`, `gfxFrameWeight`, `gfxFrameInset`,
  `_gfxSelectedEl` (id of selected element), `_gfxLogoEl`/`_gfxLogoName`.

### 3b. Rendering pipeline (key functions, with line anchors — may drift, re-grep)
- `compositeAll()` — **line 10286**. Clears main canvas, loops layers, calls
  `renderLayer` into per-layer offscreen `layerCanvases[i]`, composites with
  `layer.opacity` + `layer.blend`. **For graphic layers it snapshots the
  below-composite into `_gfxBelowCv`** (used by "visual" text fill) right before
  rendering that layer.
- `renderLayer(layer,lc,fbBuf,W,H)` — **line 7197**. Early-returns to
  `renderGraphicLayer` when `layer.layerType==='graphic'` (~line 7201).
- `renderGraphicLayer(lctx,layer,W,H)` — **line 5896**. Clears, draws background
  (`gfxBg`), iterates `layer.gfxElements`, calls `renderGfxEl` for each, stores
  bounding boxes in `layer._gfxBBoxes` (used for canvas click/drag hit-testing),
  draws frame.
- `renderGfxEl(lctx,el,layer,W,H)` — **line 5381**. Big function. Order:
  1. `lctx.save()`, sets `globalAlpha` from `el.opacity`, sets `el.blend`.
  2. **Motion & reactivity IIFE** — computes `mdx,mdy,mscale,mrot,mAlpha` from
     `el.mAnim`/`mSpeed`/`mAmount` and audio reactivity from
     `el.react`/`reactTarget`/`reactAmount` (reads global `audioSmoothed[0..2]`,
     `globalT`). Applies translate/scale/rotate + static `el.rotate`. Sets
     `el._reactGlowBoost`.  ← **THIS REACTIVITY BLOCK MOVES to the routing system.**
  3. Branch per `el.type`: `text`, `lineup`, `info`, `image`, `divider`, `box`,
     `shape`, `pattern`, `glyphs`. Returns bbox `{id,x1,y1,x2,y2}` (fractions).
- `gfxDefaultEl(type)` — **line 5311**. Returns default element object. `base`
  has shared props: `id,type,visible,x,y,w,opacity,rotate,blend,mAnim,mSpeed,
  mAmount,react,reactTarget,reactAmount`.
- Helpers near renderGfxEl: `gfxScratch(w,h)` (reusable offscreen for text
  texture-fill), `_gfxBelowCv/_gfxBelowCtx` (below-composite snapshot),
  `drawArcLine(...)` (curved text), `GFX_FONTS[]`, `gfxFillFontSelects()`,
  `renderGfxFrame(...)`.
- `gfxApplyTemplate(layer,tpl)` — **line 6531** (randomizeGfxDesign 6586, applyGfxDemo 6622). Quick templates (isakuiki, fuse,
  strelka, somos, poster, minimal). `randomizeGfxDesign(layer)`, `applyGfxDemo(layer)`.

### 3c. Element types & their props (in `gfxDefaultEl`)
- **text**: content, font, weight, italic, size, sizeMode('fit'|'fixed'), tracking,
  lineHeight, uppercase, color, align, fillMode('solid'|'gradient'|'image'|'visual'),
  color2, gradAngle, _fillImgEl/_fillImgName, strokeMode('none'|'stroke'|'both'),
  strokeColor, strokeWidth, shadowOn/X/Y/Blur/Color, glowOn/Color/Radius,
  extrude/extrudeColor/extrudeAngle, curve, boxStyle/boxColor/boxOpacity/boxPad.
- **lineup**: items, bodyFont, headFont, size, headlinerCount, format
  ('stack'|'2col'|'3col'|'inline'|'mixed'), sep, headColor, bodyColor, lineHeight,
  chips, uppercase.
- **info**: date, time, location, extra, font, size, align, color, accentColor,
  pills, boxStyle/boxColor/boxOpacity/boxPad.
- **image**: _imgEl/_imgName, fit('contain'|'fill'|'stretch'|'actual'), h, rotation.
- **divider**: color, weight, style('solid'|'dashed'|'dotted').
- **box**: h, fillColor, fillOpacity, strokeColor, strokeWeight, radius, label,
  labelColor, labelFont.
- **shape**: shape (circle/rect/ring/triangle/polygon/star/burst/arrow/cross/heart/
  lightning/shield/blob/speech/ticket), sides, points, innerRatio, cornerR,
  fillMode(solid/gradient/image/visual), fillColor, fillColor2, gradAngle,
  _fillImgEl, strokeColor, strokeWeight, glowOn/Color/Radius.
- **pattern**: pat (dots/scatter/grid/checker/stripes/rings/waves/crosshatch/
  halftone), density, patColor, patColor2, patBg, dotSize, angle, thickness, jitter.
- **glyphs** (type-pattern): content, font, weight, arrange(grid/scatter/wave),
  cols, rows, size, jitter, rotJitter, sizeJitter, color, color2, colorMode
  (solid/alternate/random), uppercase, gap, scatterSeed.

### 3d. Graphic panel UI (current — being replaced)
- Single `data-section="graphic"` (**line 1853**) inside `#panel-body`. Structure:
  canvas settings (1864), element list/add (1876), `#gfx-props` (1893) with
  `.gfx-subtabs` (1902), `#gfx-pane-transform` (1909), `#gfx-pane-motion` (1920),
  `#gfx-pane-design` (1933, holds all `#gfx-pp-*` 1934–2102), quick templates
  (2106), demo/clear (2120). Section closes at 2129. `#panel-body` closes 2131.
- Contains: header (`#graphicLayerType` switch), canvas settings, element add
  buttons (`#gfx-add-text` ... `#gfx-add-glyphs`), `#gfx-el-list`, and `#gfx-props`
  with an **in-panel sub-tab bar** (`.gfx-subtabs` → `data-pane` design/transform/
  motion) wrapping `#gfx-pane-transform`, `#gfx-pane-motion`, `#gfx-pane-design`.
- Design pane contains type sub-panels `#gfx-pp-text`, `#gfx-pp-lineup`,
  `#gfx-pp-info`, `#gfx-pp-image`, `#gfx-pp-divider`, `#gfx-pp-box`, `#gfx-pp-shape`,
  `#gfx-pp-pattern`, `#gfx-pp-glyphs`, `#gfx-pp-empty`.
- Property input IDs are `gfx-p-*` (e.g. `gfx-p-x`, `gfx-p-size`, `gfx-p-shshape`).

### 3e. Graphic panel JS (the wiring IIFE near end of file, before `loop();`)
- `window.renderGfxElList()` — builds `#gfx-el-list` rows (icon, preview, vis,
  up/down). Selecting sets `layer._gfxSelectedEl` and calls `syncGfxProps()`.
- `window.syncGfxProps()` — shows the correct `#gfx-pp-<type>` sub-panel, hides the
  rest (hide list includes all 9 types), populates inputs via `setV(id,val)`.
- `PMAP` — array of `[inputId, field, kind('num'|'str'|'bool')]`; one `input`
  listener per entry writes to the selected element. Special-cased: fillMode change
  re-runs syncGfxProps for row visibility; image loaders.
- Add-button map `ADD={'gfx-add-text':'text',...}`. Template buttons `.gfx-tpl`.
  Clear-all `#btn-gfx-clearall`. Demo `#btn-gfx-demo`. Dup/del `#gfx-el-dup`/
  `#gfx-el-del`. Sub-tab switching `.gfx-subtab` (REMOVE in refactor).
- Canvas **click-to-select + drag-to-move** on `#main-canvas` using
  `layer._gfxBBoxes` (only active when selected layer is graphic).
- `syncLayerUI` is wrapped at end so it also calls `renderGfxElList()`.

### 3f. Visual ecosystem to MIRROR (this is the target pattern)
- Tabs: `.ptab` elements with `data-tab` (layers/grid/color/motion/fx/lfo/audio),
  click handler **~line 11437-ish** shows `[data-section="<tab>"]`.
- `getParam(layer,key)` — TWO definitions: line 4295 and **line 12863**; the LATER
  (12863) wins by function-declaration order. Returns `layer['_lfo_'+key]` /
  `layer['_audio_'+key]` override if present else `layer[key]`.
- `lfoValue(lfo,t,bpm,sync)` — **line 3826**. LFOs are global `lfos[]`, each
  `{layerIdx,target,rangeMin,rangeMax,shape,rate,...}`. The main `loop()`
  (**line 10879**) sets `layer['_lfo_'+target]=mapped` for each lfo.
- `applyAudioRouting(layer)` — **line 4282**. Reads `#audioRoute0/1/2` selects
  (bass/mid/high target param), `#audioMin/Max/BandSens N`, writes
  `layer['_audio_'+target]`. Audio bands in `audioSmoothed[0..2]` (0..1), updated by
  `updateAudio()`.
- Audio route dropdowns populated by an IIFE that lists visual params grouped by
  category. LFO_PARAM_RANGES / `getParamRange(target)` give min/max per param.
- **Right-click context menu** `#ctx-menu` (HTML line 2152) with items
  `#ctx-add-lfo`, `#ctx-audio-bass/mid/high`, `#ctx-reset-val`. Handler
  `wireRightClick()` **line 13145** on `#panel-body` `contextmenu`, reads
  `ctxTargetId` = the slider id.
- `updateConditionalUI(layer)` — **line 11636**, inside a closure, exposed as
  `window._updateConditionalUI` (line 11753). The graphic-tab toggle logic is the
  `isGraphic` block at **line 11702** (gfxTab ref 11703). This is where tab
  relabel/mapping logic goes.
- Tab elements: lines **289–295** (`#ptab-grid/color/motion`, `fx`, `lfo`, `audio`,
  `#ptab-graphic` at 295). Data-sections: grid 429, lfo 1757, audio 1777,
  graphic 1853. There are THREE `.ptab` click handlers (lines 12500, 13280, 14837)
  — re-grep `tab.addEventListener` to update all relevant ones.
- Graphic panel JS: `window.renderGfxElList` line 14665, `window.syncGfxProps`
  line 14702, `PMAP` line 14781. `_gfxBelowCv` declared line 5343.

---

## 4. THE PLAN — step by step (do in this order, verify after each)

### Phase A — Restructure the graphic panel into 3 top-tab sections
Goal: replace single `data-section="graphic"` + in-panel subtabs with three
sections shown via the existing top tabs.

1. **Create three `data-section` blocks** (siblings inside `#panel-body`):
   - `data-section="graphic-elements"`: header (keep `#graphicLayerType` switch) +
     canvas settings (bg/frame/padding) + element add buttons + `#gfx-el-list` +
     element header (`#gfx-props-title`, `#gfx-el-dup`, `#gfx-el-del`) +
     `#gfx-pane-transform` (pos/size/rotate/blend/opacity) + quick templates + demo.
   - `data-section="graphic-style"`: a title + `#gfx-pane-design` (all `#gfx-pp-*`)
     + an "empty" hint when nothing selected.
   - `data-section="graphic-motion"`: a title + `#gfx-pane-motion` containing ONLY
     motion presets (animate/speed/amount). **Delete** the "audio reactive" rows
     (`#gfx-p-react`, `#gfx-p-rtarget`, `#gfx-p-ramount`) and their labels.
   - **Remove** the `.gfx-subtabs` bar and its JS handler.
   - The inner `#gfx-pp-*` and `#gfx-p-*` IDs **stay the same** so existing PMAP /
     syncGfxProps keep working with minimal change.
   - **Implementation tip:** the design pane (`#gfx-pp-*`, ~170 lines) is large —
     do NOT retype it. Re-bracket with surgical edits: close one section / open the
     next around the existing panes. DOM order does not matter (visibility is by
     tab). Watch `<div>` balance carefully (a prior session broke the layout by
     leaving 2 unclosed `</div>` which nested the canvas inside the panel —
     symptom: canvas collapses to tiny size).

2. **Tab mapping + relabel.** Add a helper:
   ```js
   function sectionForTab(tabName){
     const l=layers[selectedLayer];
     if(l && l.layerType==='graphic'){
       if(tabName==='grid')   return 'graphic-elements';
       if(tabName==='color')  return 'graphic-style';
       if(tabName==='motion') return 'graphic-motion';
     }
     return tabName;
   }
   ```
   Use it in the `.ptab` click handler and in any programmatic tab switch
   (search for `[data-section="` usages, and the graphic add-button which force-
   switches tabs ~line 11719/12535).

3. **In `updateConditionalUI(layer)`** (the `isGraphic` block): when graphic —
   relabel tab text (`grid`→"elements", `color`→"style", keep `motion`), hide the
   `fx` tab, hide/remove `#ptab-graphic`, ensure `lfo`/`audio` visible. When
   visual — restore labels grid/color/motion/fx, hide graphic-* sections. Make sure
   if the active tab is one that's hidden for the new layer type, switch to a valid
   one (e.g. → grid/elements).

4. **Delete** `#ptab-graphic` tab element and the old `data-section="graphic"`
   wrapper once content is moved.

5. **Verify (Phase A):** add a graphic layer, confirm grid/color/motion tabs show
   elements/style/motion content; selecting an element in Elements shows its
   transform; Style shows its design; Motion shows motion presets; switching to a
   visual layer restores normal tabs. Use `preview_eval` + pixel checks.

### Phase B — Per-element override plumbing (enables routing)
Goal: let external systems (LFO/audio) override element numeric props without
rewriting `renderGfxEl`.

1. Add a merge helper and use it in `renderGraphicLayer`:
   ```js
   function gfxEffectiveEl(el){
     if(!el._ov) return el;
     const e=Object.assign({},el,el._ov);
     // keep non-cloneable refs
     e._fillImgEl=el._fillImgEl; e._imgEl=el._imgEl;
     return e;
   }
   ```
   In `renderGraphicLayer`, render `renderGfxEl(lctx, gfxEffectiveEl(el), layer, W,H)`
   but **keep bbox/selection keyed to the real `el.id`** (gfxEffectiveEl copies id).
2. Each frame, BEFORE rendering, clear/compute overrides: set `el._ov = {}` (or
   delete) at the start, then routing (Phase C) fills it.
3. **Routable element props** (whitelist with ranges) — define a table:
   ```js
   const GFX_ROUTABLE = {
     x:[0,1], y:[0,1], w:[0.05,1], opacity:[0,1], rotate:[-180,180],
     size:[0.2,10], glowRadius:[0,80], tracking:[-5,60], gradAngle:[0,360],
     strokeWidth:[0,30], h:[0.02,1], density:[2,60], thickness:[0.5,12], angle:[0,360]
     // extend per needs
   };
   ```
   Used for routing dropdown options and LFO range defaults.
4. **Remove the old reactivity block** from `renderGfxEl`'s motion IIFE (the
   `el.react`/`reactTarget`/`reactAmount` handling and `_reactGlowBoost`). Motion
   presets (`mAnim` etc.) STAY (they are intrinsic animation). Reactivity now
   arrives as `_ov` values from Phase C.

### Phase C — Route Audio + LFO to element properties
Target identifier convention: **`"gfx:<elId>:<prop>"`** (e.g. `gfx:el_a1b2c3:size`).

1. **LFO apply** (in `loop()` where `layer['_lfo_'+target]=mapped` is set): detect
   `target.startsWith('gfx:')`, parse `elId` + `prop`, find element in
   `layer.gfxElements`, set `el._ov[prop]=mapped`. Use `GFX_ROUTABLE[prop]` for the
   LFO's default `rangeMin/rangeMax`.
2. **Audio apply** (in `applyAudioRouting(layer)`): same detection for the band's
   target; map band level → `GFX_ROUTABLE[prop]` range, set `el._ov[prop]`.
3. **Routing targets in the dropdowns:** when the selected layer is graphic,
   repopulate `#audioRoute0/1/2` options to list element props as
   `gfx:<elId>:<prop>` grouped by element name (use a readable label, e.g.
   "TITLE ▸ size"). When visual, restore the visual-param option list. Do this in
   `updateConditionalUI` or when entering the audio tab.
4. **getParamRange / LFO target ranges:** extend `getParamRange(target)` to handle
   `gfx:` targets via `GFX_ROUTABLE`.
5. **Right-click routing (reuse existing ctx-menu):** the element property sliders
   are `#gfx-p-*`. Extend `wireRightClick`/the `#ctx-menu` handlers so that when the
   right-clicked slider is a `gfx-p-*` slider AND a graphic layer is selected, the
   menu's "add LFO" / "send to audio bass|mid|high" set the target to
   `gfx:<_gfxSelectedEl>:<prop>` (map the slider id → element prop using the PMAP
   reverse lookup). "add LFO" pushes to `lfos[]` with `layerIdx=selectedLayer`,
   `target='gfx:'+id+':'+prop`, ranges from GFX_ROUTABLE.
6. **Selected-element dropdown routing (the other half of "both"):** in the Audio
   and LFO tabs, also allow choosing the target element prop directly (the
   repopulated dropdown from C3 covers audio; for LFO, the LFO "add" UI should let
   you pick a `gfx:` target when a graphic layer is active).
7. **Visual feedback (optional, nice-to-have):** mirror the existing slider-driven
   highlight for `gfx-p-*` sliders being driven.

### Phase D — cleanup & polish
- Remove now-dead fields from `gfxDefaultEl` base: `react`, `reactTarget`,
  `reactAmount` (or leave for back-compat but no UI — leaving is harmless).
- Update `syncGfxProps` hide-list / PMAP to drop removed audio-reactive inputs.
- Make sure `renderGfxElList` (element list) still lives in the Elements tab and
  selection persists across tab switches.
- Re-test templates, demo, dup/del, drag-to-move, visual-fill text, all 9 element
  types, motion presets, and the new audio/LFO routing end-to-end.

---

## 5. What we built this session (context for "the pipeline")

Chronological feature work already DONE and in the file:
1. **Audio loading** (mic + audio file) feeding `analyser`/`audioSmoothed`.
2. **Audio routing overhaul** — route bass/mid/high to many params, per-band
   min→max range (drag handles on sliders), per-band sensitivity; right-click
   slider → send to audio; dropdown marks active params.
3. **Missing params added** to audio/LFO routing (cols, rows, all math/noise, all
   FX params).
4. **Image overlay layer** (`patternSrc:'overlay'`) — full-canvas PNG.
5. **Flyer system** (legacy `patternSrc:'flyer'`, `renderFlyerLayer`) — superseded
   by the graphic layer but still present.
6. **Performance**: live-preview resolution scale (`liveScale`, default 0.5; export
   re-renders at full res via `buildExportCanvas`); throttled UI redraws
   (`_uiTick`); cached panel slider queries. Default canvas **9:16 1080×1920**.
7. **Graphic layer system** (the big one):
   - Layer type `graphic`; `+ graphic` add button; ✦ tab.
   - 9 element types (text, lineup, info, image, divider, box, shape, pattern,
     glyphs). Element list, add, select, drag-to-move, dup/del, reorder.
   - Text treatments: gradient/image/**visual-below** fill, stroke (none/outline/
     both), drop shadow, glow, 3D extrude, curve/arc.
   - Graphic-layer backgrounds (solid/gradient) + frames.
   - Per-element motion (8 anims) + audio reactivity (← being moved).
   - Per-element rotation + blend mode.
   - 15 shapes, 9 pattern fields, type-pattern grids.
   - Quick templates (isakuiki/fuse/strelka/somos/poster/minimal), demo, randomize.
   - In-panel sub-tabs (design/transform/motion) ← being replaced by top tabs.

## 6. What the user ultimately wants (vision)
- A motion-flyer tool where the generative visualizer and a deep graphic/design
  layer **share one consistent ecosystem**. Same tab structure, same LFO/audio
  modulation for both layer types. Abstract graphics, interesting text patterns,
  highly functional and "really interesting." References provided: STGO (chrome
  3D type), ISAKUIKI (pill date/time + big lineup), FUSE (info cards), STRELKA
  (overlapping editorial type), SOMOS (outline+fill stacked type with red glow).
- After this overhaul, the likely next requests: SVG path import for logos/icons,
  alignment & snapping guides, more sticker/badge presets, and then expanding the
  **visual engine** (new FX/post + palette/duotone systems — user already flagged
  "New FX / post" and "Color & palette systems").

---

## 7. Quick-start checklist for the next agent
1. `df -h C:` — confirm free disk space (≥ a few GB). 
2. Back up: `cp "grid-tool WORKING COPY.html" "grid-tool BACKUP $(date +%Y%m%d-%H%M).html"`.
3. Re-grep the anchors in §3 (line numbers drift as you edit).
4. Execute Phase A → verify → B → verify → C → verify → D. Surgical edits only.
5. Verify with `preview_eval` (call `compositeAll()`, sample pixels, check
   `globalT`); screenshots may hang.
6. Keep `<div>` balance correct (count opens/closes when re-bracketing the panel).
7. Commit a timestamped backup after each green phase.
