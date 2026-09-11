# Angular playbook

Angular's default change detection runs app-wide on every async event inside the zone. Most Angular weight is change-detection storms, unvirtualized lists, and eager bundles.

## Profile with

- **Angular DevTools** (extension): Profiler tab records change-detection runs per component — durations and counts. Recipe: Profiler → Start profiling → perform the scenario → stop → report the components with the most CD runs and the longest total time.
- **Chrome Performance** (core recipe, Phase 2) for long tasks.
- **Bundle**: `ng build` prints initial bundle size and warns on budget breaches. `ng build --stats-json` + `npx webpack-bundle-analyzer dist/*/stats.json` (or `source-map-explorer`) for the treemap.

## Static sweep

| Look for | Means |
|---|---|
| `*ngFor` without `trackBy` on data that refreshes | Whole-list re-render on every data change |
| Default change detection on large trees + high-frequency events (scroll, mousemove, drag) | Every event runs app-wide CD — `NgZone.runOutsideAngular` for the listener, `OnPush`/signals for the tree |
| Function calls in templates (`{{ compute() }}`, `[x]="fn()"`) | Re-evaluated on every CD cycle — pure pipe or `computed` signal |
| Long lists without `cdk-virtual-scroll-viewport` (`@angular/cdk/scrolling`) | Unvirtualized list |
| Heavy synchronous work in `ngOnInit`/constructor (parse, transform) | Long task at startup — defer it or move off-thread |
| RxJS: a heavy stream re-created per subscriber (no `shareReplay`); manual `subscribe` without `takeUntil` | Duplicate work and leaks — `shareReplay`, `async` pipe |
| Barrel or whole-library imports (`lodash`, `moment`) | Bundle bloat — per-module imports or lighter deps |
| Routes without `loadComponent` / `loadChildren` | Eager whole-app bundle |

## Ranked bottlenecks

| Signature | Bottleneck | Fix |
|---|---|---|
| DevTools Profiler: same components run CD hundreds of times during scroll/typing | Change-detection storm | `OnPush` + immutable updates (or signals); `runOutsideAngular` on the high-frequency event source |
| Long task when a big list renders or updates | Unvirtualized list | CDK virtual scrolling + `trackBy` |
| Slow input handling with template function calls | Per-CD re-evaluation | Pure pipes / `computed` signals |
| Large initial bundle; budget warnings | Bundle bloat | Lazy routes; per-module imports; keep budgets enforced |
| Slow LCP: fonts/images blocking | Blocking media | Preload; `loading="lazy"` + `srcset` |
| Dropped frames on scroll/animation | DOM/CSS layer | `references/vanilla.md` |