# Vanilla / DOM / CSS playbook

This is also the **DOM/CSS layer for every stack**: the framework playbooks send their scroll-jank, animation, and layout cases here.

## Static sweep

| Look for | Means |
|---|---|
| Scroll/resize/input handlers doing layout reads (`getBoundingClientRect`, `offsetHeight`, `getComputedStyle`) or heavy work, unthrottled | Layout/sync work per event — rAF-gate; `{ passive: true }` for scroll/touch; debounce resize |
| Loops alternating layout reads with style writes (read → write → read → write) | **Layout thrashing** — forced synchronous layout each iteration; batch all reads, then all writes |
| Animations/transitions on `top`, `left`, `width`, `height`, `margin` | Layout every frame — animate `transform`/`opacity` (compositor-only) |
| `<img>` without `width`/`height`, `loading`, `srcset` | CLS plus LCP cost; offscreen images download eagerly |
| Render-blocking `<script>` in `<head>` without `defer`; CSS `@import` chains | Waterfall — `defer`; flatten the imports or inline critical CSS |
| Very large DOM (deep tables, thousands of rows); a listener per row | Style/layout cost per change — virtualize or paginate, `content-visibility: auto`, event delegation |
| Big synchronous loops or `JSON.parse` of large payloads on the main thread | Long tasks — chunk with `setTimeout` / `scheduler.yield()` where available, or move to a Web Worker |
| Fonts without preload or `font-display`; no `preconnect` to API/font origins | Blocking text and LCP |
| Synchronous XHR; sequential `await`s that could be `Promise.all` | Waterfall and blocked parsing |

## Measuring

Chrome Performance (core recipe, Phase 2) shows this directly: Rendering/Painting time, forced-reflow warnings (layout recalculated right after script), and the FPS meter during scroll. The Coverage tab (DevTools → More tools) lists unused JS/CSS per load — a quick bundle-fat number.

## Ranked fixes

1. rAF-gate high-frequency handlers; make scroll/touch listeners passive.
2. Batch layout reads before writes; cache rects outside loops.
3. Move animations to `transform`/`opacity`.
4. `loading="lazy"` + explicit dimensions + `srcset` on images; preload the LCP image and font.
5. `defer` scripts; flatten CSS imports; `Promise.all` independent requests.
6. Virtualize or paginate giant lists; `content-visibility: auto` for below-the-fold sections.
7. Chunk long synchronous work, or off-thread it to a Web Worker.