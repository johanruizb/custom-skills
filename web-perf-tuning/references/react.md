# React / Next.js playbook

## Profile with

- **React DevTools Profiler** (browser extension). Recipe for the user: open the app → Profiler tab → settings (⚙) → enable "Record why each component rendered" → Record → perform the scenario → stop. Report back: the top 3 commits by duration, the components that re-rendered in each, and the recorded "why" (props / state / context).
- **Chrome Performance** (core recipe, Phase 2) for long tasks.
- **Bundle**: `next build` prints per-route First Load JS — record the slow route's row. Vite/CRA: build once with `rollup-plugin-visualizer` (or `source-map-explorer` over the production build) and read the largest modules.

## Static sweep

Search the code for these; each is a common React bottleneck:

| Look for | Means |
|---|---|
| `.map(` rendering long lists with no `react-window` / `@tanstack/react-virtual` / `virtuoso` | Unvirtualized list — the top long-task source in data-heavy UIs |
| `<X.Provider value={{ … }}>` (object literal) or `value={fn}` recreated per render | Every context consumer re-renders on each provider render — split the context or `useMemo` the value |
| Input/page state held high while only leaves use it | Wide re-render trees per keystroke |
| `memo(` components receiving inline `style={{…}}`, `onClick={…}`, `options={[…]}` | memo defeated: new prop identities every render |
| `key={i}` (index keys) on lists that reorder or filter | Remount churn — state loss plus full re-render per change |
| Large sort/filter/aggregate computed inline in render bodies | Expensive work re-run every render — `useMemo`, or precompute |
| Route/modal/chart components statically imported | Everything ships in the first bundle — `lazy()` / `next/dynamic` |
| `useStore()` or a selector returning whole state (Zustand/Redux) | Re-render on any store change — select slices |
| React Query with default `staleTime: 0` and `refetchOnWindowFocus` | Refetch storms on focus and remount — set `staleTime`, disable focus refetch for heavy queries |
| Next.js: large trees under `"use client"`, `<img>` instead of `next/image`, barrel imports (`@mui/icons-material`, `lodash`) | Client JS and image weight — shrink the client boundary, use `next/image`, import modules directly (`lodash-es`) |

## Ranked bottlenecks

| Signature | Bottleneck | Fix |
|---|---|---|
| Profiler: same components re-render per keystroke; wide commit flamegraphs | Re-render storm | Colocate state, split the context, stabilize props; `memo` only the proven-hot leaves |
| Long task on list render/filter/scroll | Unvirtualized list | Virtualize; `useMemo` the derived data |
| Scripting dominates on load; first-load JS over ~200 KB gz on the slow route | Bundle bloat | Code-split routes and heavy components, replace heavy deps, trim the client boundary |
| Network tab: fetch chains firing sequentially (one request per `useEffect` stage) | Data waterfall | Parallelize, prefetch, or move the fetch to a loader / server component |
| Slow LCP with large image/font transfer | Blocking media | `next/image` or `loading="lazy"` + `srcset`; preload the LCP font and image; `font-display: swap` |
| Dropped frames on scroll/animation (frames, not long tasks) | DOM/CSS layer | See the DOM/CSS layer in `references/vanilla.md` |