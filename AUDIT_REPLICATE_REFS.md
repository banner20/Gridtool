# Audit: Replicating Reference Posters — Build Plan

Goal: make the tool able to recreate these reference looks **effortlessly** (not element-by-element), across graphic / visual / media layers in combination.

## ⚠️ METHODOLOGY (corrected — read first)
- **Think in SYSTEMS, never per-reference.** Build the general capability; the reference is just one output it can produce.
- **NEVER hardcode to a reference.** If a ref needs something we have no system for → that's the signal to design a NEW system (new effect, new layer type, new generator, physics engine, etc.). Treat refs as opportunities to deepen the tool for real use.
- **Match the MECHANISM, not the surface.** (Mistake made earlier: Barcelona ref 1's rainbow is the COLORED 3D EXTRUSION of flat black letters converging to a vanishing point — NOT a spectrum fill painted on the text face. `spectrumfill` as a face-fill was WRONG for ref 1.)
- **Presets come LAST**, only after the system truly works, as an audit artifact in the tool's preset section so the user can confirm the match. One preset per reference.
- Each ref → identify the underlying system → build/extend that system → then preset.

## Confirmed architecture decisions
- **Extrusion/Projection system** = ONE system with BOTH modes: perspective-to-vanishing-point AND directional/parallel. Features: gradient-along-depth (repeating spectrum down the extrusion), repeat count, fold shading, vanishing-point X/Y. REPLACES the weak `extrude3d` (which is just a flat single-direction stamp — cannot converge or gradient along depth).
- Extrusion lives as a **per-element appearance effect** (composable, any text/shape).
- Build order: **WAIT for more refs first**, then design systems to cover all of them at once.

## Re-analysis of refs as SYSTEMS
| Ref | Real mechanism | System | Status |
|---|---|---|---|
| 1 Barcelona | Flat black text + perspective 3D extrusion to vanishing point, extruded BODY filled w/ repeating spectrum + fold shading | Extrusion/Projection system (NEW) | ❌ TODO (prior attempt wrong) |
| 2 NEVER SETTLE | Text density from source image | Mosaic system | ✅ built (mechanism correct) |
| 3 Colored ASCII | Mosaic + per-cell color | Mosaic system | ✅ built |
| 4 "human" | Word grid random color/size | Glyphs element | ✅ exists |
| 5 Fluid metaballs | Packed cells each w/ internal 2-tone swirl | Metaball/packed-field generator (NEW) | ❌ TODO |

NOTE: `spectrumfill` effect (built Phase 1) is still useful as a generic banded/spectrum FILL, but it does NOT solve ref 1. Keep it; ref 1 needs the Extrusion system.

## ⚠️ METHODOLOGY v2 (user corrections — supersede where conflicting)
- **ASSUME EVERYTHING IS MOTION.** This is a motion tool. For every static ref, infer the implied animation and build so it can move (noise-time, scroll, breathe, simulate).
- **Watch for capability OVERLAP across layers.** The visual layer ALREADY samples image/video/webcam into a grid of cells. The mosaic element (graphic layer) ALSO samples a source into a grid. That's duplication — "sample source → grid" is ONE core capability; only the CELL RENDERER differs (color cell / shape / glyph / bordered cell+symbol). Decide the right HOME per case; favor unifying.
- **Identify the TRUE underlying system, incl. generative/pattern/physics ones the user may not name.**

## Refs 6–9 (second image) — corrected system analysis
| Ref | TRUE mechanism (+ implied motion) | System / Home | Status |
|---|---|---|---|
| A (TL) colored cell-grid forming figures | source/noise-driven GRID of cells, each = fill color + BORDER + optional SYMBOL overlay (×,+). Motion: noise-time morph, cells flicker/pop | **VISUAL LAYER** grid (its native territory — already samples sources+noise-time). Add per-cell border + symbol renderer. NOT a mosaic extension. | ❌ TODO |
| B (TM) symmetric geometric tiling | generative geometric tile + dual-axis mirror. Motion: tiling rotates/animates thru symmetry | VISUAL LAYER symmetry groups + tile generator — mostly exists; verify/enrich geometric tiles | ⚠️ verify/extend |
| C (TR) SAINT LAURENT justified grid | ONE source text laid out to FILL a region in a repeating pattern, per-line justify-to-width / alt align. Nobody hand-places it → TEXT-PATTERN-FILL system. Motion: pattern scrolls / tracking breathes | **NEW: text-pattern-fill** system (graphic) | ❌ TODO |
| D (BM) Designzentrum clustered words | PHYSICS: word bodies attract + collide + cluster/attach into organic clumps. Inherently in motion (drift + settle) | **NEW: physics system** (likely a new physics layer type for generality; future text-falls/liquid/particles live here) | ❌ TODO |

## BUILD ORDER (user: lock plan, build in order; presets LAST; I decide architecture)
1. ✅ DONE Visual-layer **cells: per-cell border + symbol overlay** (Ref A). Native home (visual layer's grid). Per-cell BORDER (width, colorMode fixed/cell/contrast/darken/lighten, inset, threshold-gate) + per-cell SYMBOL (glyph + alt-glyph w/ row/col/checker/noise pattern, show-in modes all/threshold/invthreshold/alt/checker/noise, size, colorMode, weight/font, stroke-only, rotate + rotNoise). All numerics routable via LFO/audio (ranges + route-target list). Motion is implicit: nv is noise-time driven so threshold/noise gates animate. Verified: green border 86400px, white symbols 5600px, checker halves to 2800, threshold gates, contrast/cell colorModes resolve.
2. ✅ DONE **Text-pattern-fill** system (Ref C — SAINT LAURENT). New graphic element `textfill` (¶). ONE source text + separator, repeated to FILL a region; per-line justify modes fill/left/center/right/scroll(marquee); alt-line modes none/brick-offset/mirror; case upper/lower/as-is; font/weight/size/lineHeight; colorModes solid/duoline/duoword/gradient(vertical)/rainbow(time-drifting); tracking + **track-breathe** (motion) + breathe speed; **scrollX/scrollY** (motion: marquee + vertical crawl); bg toggle. Numerics routable (GFX_ROUTABLE: fontSize, tracking, trackingBreathe, breatheSpeed, scrollX, scrollY, lineHeight). Verified: justify-fill flush to BOTH region edges (1px gaps in 486px), vertical scroll + horizontal marquee animate per-frame, duoline splits colors 42918w/40404r, 83478 text px rendered.
3. ✅ DONE **Physics system** (Ref D — Designzentrum). ARCHITECTURE DECISION: built as a graphic ELEMENT `physics` (⚛), not a new layer type — unifies with the element architecture (composes with appearance effects + layer filters + positioning), and generalizes (word bodies / dots, multiple force modes). 2D sim: word list → bodies (circle-bound, radius from text metrics); forces = cohesion-to-center, mutual attraction (inverse-square), gravity, orbit (tangential), brownian jitter; pairwise collision (separate + normal-velocity response); damping + velocity cap + region walls. Modes cluster/fall/float/orbit. Sim state stored in module map `window._gfxPhys[el.id]` so it SURVIVES the gfxEffectiveEl clone (critical — eff el is recreated when routed). Rebuild keyed by words+size+seed+split+region. 8 routable force params (gravity/cohesion/attract/collide/jitter/simSpeed/centerX/centerY). Verified: cluster settles 10 bodies w/ ZERO overlap pairs (collision works), avg vel decays to 0.47 (stable, no explosion); fall piles bodies at 0.75 region-depth; float keeps 9/10 bodies moving (continuous motion). Inherently in motion. NOTE: future text-falls/liquid/particles can extend this element or add sibling modes; a dedicated physics LAYER can come later if a use case needs full-canvas sim independent of the graphic element box.
4. ✅ DONE (VERIFY) Geometric-tile **+ symmetry** (Ref B). Audited the existing system — it's already comprehensive: `applyWallpaperSymmetry` implements ALL 17 wallpaper groups (p1,p2,pm,pg,cm,pmm,pmg,pgg,cmm,p4,p4m,p4g,p3,p31m,p3m1,p6,p6m) + kaleidoscope filter; 19 dropdown entries; symScale/symAngle/symX/symY; tile passes through per-layer shader filters before symmetry. Geometric cell shapes (diamond/triangle/star4/star6/petal/ring/cross/hex…) feed the tile. Verified: pmm produces strong mirror structure (85% center-axis match — residual is just that wallpaper mirror axes sit at tile boundaries not exactly canvas-center; the pattern IS symmetric), and it animates (symAngle+speed → "rotates through symmetry", the implied motion). Existing presets cover it (p4m tiles, p6m hex, pmm mirror, p4g glide, p6 spin). NO new system needed — per methodology, avoided speculative enrichment. Ref B is fully replicable today.
5. ✅ DONE **Extrusion/Projection** appearance effect (Ref 1 Barcelona) — THE one I got wrong before. Upgraded `extrude3d` IN PLACE (kept key for back-compat) into a real projection system. Stamps the element's white silhouette back over `depth` steps; each step: (a) DIRECTIONAL offset along `angle`×`distance`, AND (b) `perspective` convergence toward vanishing point `vpx/vpy` (scale toward VP per depth) — both modes blend via the perspective amount. Body coloring: `spectrum` toggle → repeating palette (`palette` 0-7, `repeat` bands, `offset` phase) sampled ALONG depth, else `solid` color. `fold`+`foldFreq` = alternating facet shading; `darken` = atmospheric depth fade. Face composited ON TOP unchanged (stays flat black → correct mechanism: rainbow is the EXTRUSION BODY, not a face fill). Bug fixed during build: passed context `tc` to drawImage instead of canvas `tmp`; also hexToRgb doesn't expand 3-digit hex → default changed to 6-digit. Verified: spectrum mode → 74164 body px across 12 distinct hue buckets w/ black face intact; perspective mode converges body toward VP (333→297px). All numerics routable. THIS REPLACES spectrumfill as the ref-1 solution (spectrumfill kept as generic fill).
6. ✅ DONE **Fluid/Metaball** generator (Ref 5). New graphic element `fluid` (◍). Dart-throwing circle packing (cached in `window._gfxFluid[el.id]`, survives clone; keyed by region+density+sizeVar+minR+gap+seed) → 100s of non-overlapping circles w/ size distribution. Each circle clipped + filled with a conic-gradient pinwheel (`swirlArms`×2 alternating color1/color2 stops) whose center is offset by `twist`×r for an eddy look, rotating at `spinSpeed` per-circle (random dir/rate) = the two-tone swirl, in motion. Radial `highlight` adds a marble/bauble sheen + rim shade. Bg (dark red default). Routable: swirlArms/spinSpeed/twist/highlight/sizeVar. Verified: 356 packed circles, orange 57683px + blue 78367px (two-tone) on dark-red bg (302237px), swirls animate. Matches Ref 5.
7. ✅ DONE — PRESETS for every ref in the tool's preset section, as audit artifacts. Added 6 built-in presets (DEFAULT_PRESETS): `ref A · cell-grid + symbols`, `ref B · geometric tiling`, `ref C · justified type fill`, `ref D · word cluster (physics)`, `ref 1 · spectrum extrusion`, `ref 5 · fluid swirl`. Each is a one-layer scene wired to the system that replicates the ref. Also hardened `applyPresetData` to deep-copy `gfxElements` + assign fresh ids on load (prevents preset-literal mutation + sim-state id collisions). Verified all 6 load and render their expected output (A: 374k colorful cells; B: symmetric tiling; C: 130k px justified white text; D: black word bodies on cream; 1: black face + rainbow extrusion 122k colorful; 5: orange/blue swirls 200k colorful). NOTE: refs 2/3 (mosaic) need a user-loaded image source so they can't be a self-contained preset — mosaic element itself was built+verified earlier.

## ✅ ALL 7 BUILDS COMPLETE — every reference now has a system + audit preset.
Systems added this pass: visual-layer per-cell border+symbol (A) · textfill element (C) · physics element (D) · verified 17-group wallpaper symmetry (B) · real extrude/project effect replacing the weak one (1) · fluid swirl element (5). Plus mosaic (2/3) and glyphs (4) from earlier. Open the `— presets —` dropdown → the `ref …` entries are the audit artifacts; load each and compare to its reference.

Decisions: I decide source→grid home & physics home as I build, favoring unification + generality.

## References analyzed
1. **Orgull Barcelona** — black bold headline + rainbow spectrum pleats fanned radially, fold-shaded, masked into a downward arrow. + footer + logo pill.
2. **NEVER SETTLE** — small repeated words arranged by a source image's luminance to form a face/skull.
3. **Colored ASCII grid** — dense character grid forming letterforms, per-cell color highlights (green/pink).
4. **"human" repeated** — word grid, random bright colors, size variation. (≈ already doable via glyphs element.)
5. **Fluid metaballs** — packed circles each with two-tone swirl fill, orange/blue on dark red.

## Build order (user: do all in order; composable parts + scene templates on top)
1. **Rich gradient engine** ✳ FIRST — multi-stop (6–8) spectrum/pride presets, repeat/banding count, linear/radial/conic/fan projection, fold/pleat shading, clip-into-shape (via appearance `gradientmap` effect + element fill mode). Unlocks ref 1.
2. **Image-driven mosaic element** — source image → tiled as text/words/ASCII/dots; luminance drives density + char choice; optional per-cell color. Unlocks refs 2 & 3.
3. **Universal source-fill / masking** — fill/clip ANY region (text/shape/layer) with ANY source (gradient/image/video/another layer). Composable backbone.
4. **Fluid/metaball generator or shader** — packed cells w/ internal swirl. Ref 5.
5. **Scene templates** — bundle full looks (bg source + mask + type + post); drop-in then swap text/colors. (The "effortless" payoff.)

## Status
- [x] Phase 1: rich gradient engine — DONE. `spectrumfill` appearance effect: 8 palettes (GFX_GRAD_PALETTES), 4 types (linear/radial/conic/fan), repeat/banding, fold shading, offset, scale. Presets `pleats` (fan, ref-1 look) + `spectrum`. Verified rainbow fills text. Applies to ANY element via the appearance stack (clips into shape automatically since it's source-atop on the element buffer).
- [x] Phase 2: image-driven mosaic — DONE. New `mosaic` element type (▦). Loads image/video source, samples to cols×rows luminance+RGB grid (`_gfxMosaicSample`, cached for images, live for video). Modes: text/charset, ascii ramp, dots, binary. Luminance→density (text appears only where bright, forms the source shape), size-by-brightness option, threshold/contrast/gamma/invert. Color modes: mono / from-image (per-cell) / duotone / rainbow. Verified: words form a disc from a disc source; per-cell color matches source. Unlocks refs 2 & 3. Accepts appearance effects + layer filters like any element.
- [ ] Phase 3: universal source-fill/masking
- [ ] Phase 4: fluid/metaball
- [ ] Phase 5: scene templates

## Key code locations (grid-tool.js, split-file build; run `python build.py` after edits)
- `GFX_EFFECT_DEFS` ~3532 — appearance effects (gradientmap lives here).
- `gfxApplyElementEffects` — runs effect stack on element buffer; supports per-fx blend+opacity.
- `renderGfxEl` ~2995 — per-element draw (text/shape/etc). `renderGraphicLayer` ~3628.
- `GFX_EFFECT_PRESETS` — appearance preset stacks.
- Filters engine `FILTER_DEFS` (54 GPU shaders), `applyFilterChain`.
- Build: edit grid-tool.js / .css / "grid-tool WORKING COPY.html", then `python build.py` → grid-tool-dist.html. CSS link is `?v=N` cache-bust.
