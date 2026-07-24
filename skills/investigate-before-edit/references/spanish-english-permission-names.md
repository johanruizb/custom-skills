# Spanish/English Permission Name Mismatch

## The Bug Pattern

In this project, `getModelPermissions()` in `useRol.jsx` returns permission keys in **English** (`view`, `crear`, `editar`, `eliminar`, `exportar`, `administrar`), but **12+ components** across the app use **Spanish** keys (`permissions.ver`, `permissions.crear`, etc.).

When the hook returns `view` but the component reads `ver`, the value is always `undefined` — which is falsy. This causes:

- Navigation links to not render (canNavigate = false)
- Conditional UI sections to be hidden
- "No permissions" fallbacks to trigger

## Affected Files (as of Jul 2026)

Files using `permissions.ver` (Spanish — the correct convention for this project):

- `src/pages/Grupos/VerGrupos.jsx`
- `src/pages/Grupos/index.jsx`
- `src/pages/Niños/index.jsx`
- `src/pages/Servicios/DayServicesModal.jsx`
- `src/pages/Servicios/index.jsx`
- `src/pages/Creyentes/VerCreyente.jsx`
- `src/pages/Visitantes/index.jsx`
- `src/pages/Clases/index.jsx`
- `src/pages/Inventario/index.jsx`
- `src/pages/Crecimiento/components/views/individual/CellView.jsx`
- `src/components/Grupos/ListGroup.jsx`

## Root Cause

`getModelPermissions` in `src/hooks/rol/useRol.jsx`:

```js
return {
    view: !!modulePerms.ver || isAdmin,  // <-- English key
    crear: !!modulePerms.crear || isAdmin,
    editar: !!modulePerms.editar || isAdmin,
    eliminar: !!modulePerms.eliminar || isAdmin,
    exportar: !!modulePerms.exportar || isAdmin,
    administrar: !!modulePerms.administrar || isAdmin,
};
```

Should be:

```js
return {
    ver: !!modulePerms.ver || isAdmin,   // <-- Spanish key
    crear: !!modulePerms.crear || isAdmin,
    ...
};
```

## Investigation Pattern

When a user reports "clicking X does nothing" or "I can't see Y even though I'm a superuser":

1. **Read the component** that renders the clickable element. Find the condition that controls navigation/visibility.
2. **Trace the condition** back to the hook call. What key does it access? (`permissions.ver` or `permissions.view`?)
3. **Read the hook** (`useRol.jsx`). What key does `getModelPermissions` return? (`ver` or `view`?)
4. **Compare.** If they don't match, that's the bug.
5. **Fix the hook** to match the components (12 components use `ver`, 0 use `view` — fix the hook, not the components).

## Why This Happens

The original developer wrote the hook with English keys (`view`) but all the components use Spanish keys (`ver`). The commit that introduced `getModelPermissions` (`93ffa2c9`) preserved this mismatch from the legacy code. The bug existed before the permisos migration and was never caught because:
- ESLint doesn't flag undefined property access
- The components render (just with hidden sections)
- No tests check that `permissions.ver` is truthy for superusers

## Prevention

When adding a new permission check in a component:
- Use `permissions.ver` (Spanish), NOT `permissions.view` (English)
- The hook returns: `ver`, `crear`, `editar`, `eliminar`, `exportar`, `administrar`
- If you're unsure, check 3 existing components to confirm the convention
