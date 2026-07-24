# MUI ListItemButton + Nested `<a>` Elements

## Problem

When a `ListItemButton` contains a `secondaryAction` with `IconButton` elements that use `LinkComponent={Link}`, the ListItemButton itself CANNOT use `component={Link}`. This creates nested `<a>` elements (HTML invalid), and the browser ignores the outer `<a>`, making the ListItemButton unclickable for navigation.

## Symptoms

- Clicking a ListItemButton does nothing, even though `component={Link}` and `to` are correctly set
- The element has no `href` in the DOM (the browser strips it from nested `<a>`)
- Console shows no errors
- The `secondaryAction` buttons (edit, delete) work fine because they are the innermost `<a>`

## Root Cause

MUI's `ListItemButton` renders as `<div>` by default. When `component={Link}` is passed, it renders as `<a>`. But the `secondaryAction` `IconButton` elements with `LinkComponent={Link}` also render as `<a>`. HTML spec does not allow `<a>` inside `<a>` — the browser ignores the outer `<a>`.

## Fix

Replace `component={Link}` with `onClick` + `useNavigate()` on the ListItemButton. Keep `LinkComponent={Link}` on the inner IconButtons.

### Before (broken)

```jsx
<ListCardItem
    buttonProps={{
        ...(canNavigate
            ? { component: Link, to: `${data.id}`, state: { group: data } }
            : { onClick: handleOpen }),
        sx: { ... },
    }}
    secondaryAction={
        <Acciones>
            <IconButton LinkComponent={Link} to={`${data.id}/editar`}>
                <EditIcon />
            </IconButton>
        </Acciones>
    }
/>
```

### After (fixed)

```jsx
import { Link, useNavigate } from "react-router-dom";

// Inside component:
const navigate = useNavigate();

<ListCardItem
    buttonProps={{
        onClick: canNavigate
            ? () => navigate(`${data.id}`, { state: { group: data } })
            : handleOpen,
        sx: { ... },
    }}
    secondaryAction={
        <Acciones>
            <IconButton LinkComponent={Link} to={`${data.id}/editar`}>
                <EditIcon />
            </IconButton>
        </Acciones>
    }
/>
```

## When to Apply

- Any MUI `ListItemButton` that has `secondaryAction` with `LinkComponent={Link}` IconButtons
- Any MUI `ListItemButton` that contains interactive children that render as `<a>` or `<button>`
- Any situation where a clickable container contains other clickable elements that need independent navigation

## Verification

1. Build passes (`vite build`)
2. Lint passes (0 warnings)
3. In the browser: clicking the ListItemButton navigates to the detail page
4. In the browser: clicking the secondaryAction IconButtons (edit/delete) still works independently
5. DOM inspection: ListItemButton is a `<div>` with `role="button"`, not an `<a>`
