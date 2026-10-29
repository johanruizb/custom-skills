# Coherence Audit Checklist

Reference for Phase 2. Audit against the project's recorded design source, not against personal taste. For each dimension: what to compare, what an accidental difference looks like, and when the difference is justified or a system gap.

## 1. Spacing and rhythm

Compare gaps, margins, section padding, and vertical rhythm between screens with the same job.

- **Accidental**: `gap-6` on one card grid and `gap-4` on another serving the same role; a section title with `mt-8` in one screen and `mt-6` in its sibling; ad-hoc `p-[18px]` values.
- **Justified**: a settings form uses wider vertical spacing than a live data table because scanning density differs.
- **System gap**: the spacing scale has no value between `sm` and `md`, so both screens invented their own.

## 2. Type scale and roles

Compare headings, body, labels, and mono usage by role, not by screen.

- **Accidental**: the same section heading at `text-lg` on one screen and `text-xl` on another; labels using body size in one panel and label size in the next; three different muted colors for secondary text.
- **Justified**: a dashboard uses the display role for a single hero metric; a console has no hero and starts at title.
- **System gap**: a role used in the UI (e.g. numeric metric) has no defined type token.

## 3. Color roles and semantic usage

Compare by role: background, surface, border, text, muted, accent, success, warning, destructive.

- **Accidental**: `bg-slate-900` in one panel and `bg-[#0b1120]` in another for the same surface; success using `emerald-500` in one place and the token elsewhere; destructive used for a non-destructive action.
- **Justified**: a warning surface is tinted on a screen where the alert dominates; the same role with a different emphasis level if the system defines emphasis variants.
- **System gap**: a state (selected, active, hover) has no defined color role.

## 4. Borders, radii, elevation

- **Accidental**: `rounded-md` cards on one screen and `rounded-lg` on another; a 1px border in one panel and a shadow in its sibling; two elevation levels doing the same job.
- **Justified**: a floating overlay uses elevation where an inline panel uses a border.
- **System gap**: no rule separates inline panels from floating surfaces.

## 5. Density

Compare padding, row heights, control heights, and information per unit.

- **Accidental**: the same table row at 40px and 48px; the same primary button at 32px and 40px; inconsistent panel padding inside one screen.
- **Justified**: an operations console is denser than a summary screen; a touch surface is larger than a pointer target.
- **System gap**: density is not defined per screen job, so every screen picks its own.

## 6. Component duplication and divergent variants

- **Accidental**: two card components with the same purpose; a button reimplemented locally; a status indicator with three different dot sizes; a panel component whose local override changes its radius.
- **Justified**: a variant that exists because the function differs (compact table row vs spacious detail card) and is recorded in the design source.
- **System gap**: one component is asked to serve two incompatible jobs and grows boolean variants instead of a named variant.

## 7. Interaction states

Check every interactive element for hover, focus, disabled, loading, empty, error, and success where applicable.

- **Accidental**: hover on one button darkens and on another only changes the cursor; focus rings absent in one screen; a disabled control at 40% opacity in one place and 60% in another; loading shown as a spinner in one panel and a skeleton in the next.
- **Justified**: a destructive confirmation uses a stronger hover than a neutral action, if the system defines it.
- **System gap**: no defined focus treatment, so each component invents one.

## Signs a difference is not a finding

- Rendering noise: antialiasing, subpixel borders, font hinting, device pixel ratio.
- Viewport or theme mismatch: compare the same viewport, theme, and zoom.
- Content differences: longer labels, more data, translated strings.
- States that are genuinely unavailable in one screen because the feature does not exist there.

## Evidence standard

A finding names the screen or component, the observed value, the rule it violates (with its path in the design source), the class, and the severity. "Inconsistent" alone is not a finding; it cannot be fixed or verified.
