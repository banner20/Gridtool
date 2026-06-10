# GRIDTOOL

A browser-based generative design & motion studio. One HTML file, no dependencies, no install.

## Layer types

- **▦ Visual** — the generative grid engine: noise/math sources, iterators, palettes, wallpaper symmetry
- **✦ Graphic** — typographic & graphic design elements (flyers, titles, layouts)
- **▣ Media** — image / video / webcam layers
- **🫧 Blobby** — interactive SDF blob painting: metaball strokes, carve mode, field shading, shape-aware text reflow (autofit, justify, inset, leading, tracking)
- **🫟 Marble** — mathematical ink marbling (suminagashi/ebru): drop inks, drag combs, feathers & vortices through the bath — fully replayable
- **🩰 Gesture** — a loop pedal for drawing: record canvas gestures, they replay forever with your velocity, BPM-quantized

## Systems

- **68 GPU shader filters** (per-layer + global) with motion params throughout — droste spiral, wax melt, risograph, pencil sketch, liquid chrome, pixel rain, moiré, anaglyph…
- **Masking** — shapes, stripes/rings/checker, animated noise clouds, text stencils, or any layer as a mask (luma/alpha/channel), with motion (drift/spin/pulse/scroll/boil), edge styles (soft/steps/dither), one-click presets and on-canvas aiming
- **Modulation** — LFOs, audio routing, BPM sync, timeline with keyframes, FX chains with maskable regions

## Run

Open `grid-tool-dist.html` in a browser. That's it.

## Develop

Source is split for editing:

- `grid-tool WORKING COPY.html` — markup
- `grid-tool.css` — styles
- `grid-tool.js` — engine

Rebuild the single-file distribution:

```
python build.py   # → grid-tool-dist.html
```
