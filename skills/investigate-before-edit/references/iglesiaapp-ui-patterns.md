# IglesiaApp UI Design Patterns

> Reference for the IglesiaApp frontend (React 18 + MUI v7). These are user-established preferences, not generic best practices.

## Layout

- **No tables.** Use cards, lists, or accordion-based layouts. The user explicitly rejected MUI Table / `<table>` elements.
- **Block page scroll.** The page container should use `flex: 1, minHeight: 0, overflow: hidden`. Independent scrollable areas inside (sidebar scroll, content scroll). Body should never scroll.
- **Categorize and group items.** Use collapsible sections (MUI Accordion or custom) with category headers. Only one section open at a time (controlled accordion pattern).
- **Sidebar + content split layout.** Sidebar ~300-340px wide with search/filter. Content area fills remaining space.

## Components

- **Action buttons in Paper headers.** When a Paper/card has actions (save, delete, etc.), put them in the header area, not floating loose below.
- **Back button in fullScreen dialogs.** Any fullScreen dialog must have a back/close button in the top bar.
- **Chips for metadata.** Use MUI Chip components for counts, statuses, and badges (e.g., "22 permisos" chip next to a role name).
- **SectionHeader component.** Use the existing `SectionHeader` for page section titles with action buttons.
- **FormSection component.** Use the existing `FormSection` for form groupings with title and optional action prop.
- **ListCardItem component.** Use for list items in cards (icon + text + secondary text + optional action).

## Colors & Theme

- All colors from `theme.palette.*` tokens — no hardcoded hex values.
- Semantic colors: `primary.main` for main actions, `warning.main` for caution, `error.main` for delete/danger, `success.main` for active/confirmed, `info.main` for informational.
- Icons should use semantic colors to convey meaning (e.g., shield icon in `primary.main`, delete icon in `error.main`).

## Permission Admin UI (specific patterns)

- **Role list in sidebar:** Grouped by `category` field. Collapsible sections with category name in uppercase. Chip showing permission count. Search/filter at top.
- **Role editor in main content:** FormSection with role name + description. Permission catalog as categorized accordion list. Save button in FormSection header.
- **User assignment:** Searchable user list with checkboxes. Show current role assignment.
- **Protected roles:** System roles (`is_system=True`) cannot be deleted or renamed. Global roles (`is_global=True`) cannot be deleted or renamed but permissions can be customized per church. Show badge/label for protected roles.

### Permission Catalog List (PermissionCatalogList.jsx)

- **Layout:** Grid of 2 modules per row (`xs: 12, sm: 6`). Each module is an MUI Accordion.
- **Select-all wiring pattern:** The select-all button is NOT rendered inside PermissionCatalogList. Instead, the component exposes `onAllSelectedChange({ allSelected, toggleAll })` to the parent. The parent (RoleEditor or UserPermissionEditor) renders the button in the `action` prop of FormSection. This keeps the button in the header area, not inside the catalog list.
  - The parent must pass `onToggleAll(perms, checked)` to PermissionCatalogList for the select-all to work.
  - Common bug: parent doesn't pass `onToggleAll` — the button renders but does nothing.
  - The `handleSelectAll` function was removed from PermissionCatalogList; the `toggleAll` callback is now provided via `onAllSelectedChange`.
- **Per-module checkbox:** In the AccordionSummary header, before the module name. Three states: unchecked (none selected), indeterminate (some selected), checked (all selected). Uses `stopPropagation` to prevent accordion toggle when clicking the checkbox.
- **Permission rows:** Inside AccordionDetails, grouped by resource. Each resource has a label and a Grid of 3 permission checkboxes per row (`xs: 6, sm: 4`). Actions are translated: `ver` → "Ver", `crear` → "Crear", `editar` → "Editar", `eliminar` → "Eliminar", `exportar` → "Exportar", `administrar` → "Administrar".
- **Override support:** When `overrideMap` is provided, shows grant/revoke icons on overridden permissions.
- **Props:** `modules` (array), `selected` (Set), `onToggle(perm, checked)`, `onToggleAll(perms, checked)`, `overrideMap`.
- **Data format:** The `modules` prop is a **list** directly (e.g., `[{key, label, resources}, ...]`), NOT an object with a `modules` key. The component accesses `modules.map(...)` directly, not `modules.modules.map(...)`.
- **Permission key construction:** Each permission key is built as `mod.key + "." + resource + "." + action` (3-part, e.g., `cultos.actas.crear`). The `selected` Set must contain keys in this exact format. A common bug is constructing 2-part keys (`recurso.accion`) which never match the 3-part keys from the backend.

### Role Editor (RoleEditor.jsx)

- **Layout:** FormSection with role name + description TextFields. Permission catalog below.
- **Loading state:** Shows CircularProgress while catalog loads.
- **Save:** Button in FormSection header. Calls `API_SaveRole(roleId, { name, description, permissions })`.
- **Delete:** Button in FormSection header (hidden for system/global roles). Calls `API_DeleteRole(roleId)`.
- **New role:** When `role` is null/undefined, shows create form. On save, calls `API_CreateRole({ name, description, permissions })`.
- **Permission format:** Permissions are stored as `modulo.recurso.accion` (3-part keys like `cultos.actas.crear`). The catalog list constructs these from `mod.key + "." + resource + "." + action`.
- **Propagate button:** Visible only for superusers editing system or global roles. Calls `API_PropagateRole(roleId)` which copies permissions to all churches. Uses `useConfirm` dialog before executing. Icon: `SyncIcon` with `color="info"`.
- **isSuperuser detection:** Uses `useRol()` hook which exposes `isSuperuser: Boolean(rol.is_superuser)`. The `is_superuser` field comes from the `auth/permissions` endpoint via the `group_serializer` in the backend.

### User Permission Editor (UserPermissionEditor.jsx)

- **Layout:** Searchable user list on left, permission overrides on right.
- **Search:** Debounced text input, calls `API_SearchUsers(query)` which hits `GET permisos/users/search?q=...`.
- **User data format:** Search returns `{ user_id, firstname, lastname, num_doc, foto }` where `user_id` is the Django `User.id` (NOT `person_spiritual.id`). The `userId` used for overrides must be `user.user_id`.
- **Override management:** Shows current role permissions with grant/revoke toggles per permission.
- **Override data format:** The `granted` field is a **boolean** (`true` for grant, `false` for revoke), NOT a string like `"grant"`/`"revoke"`. The overrideMap interprets `ov.granted ? "grant" : "revoke"`.
- **Save:** Sends override list to `API_SaveUserOverrides(userId, overrides)`.

### PermisosPage.jsx

- **RoleEditor onSave:** The `onSave` callback passed to `RoleEditor` receives `(payload)` with `{ name, description, permissions }`. The callback MUST call the backend API (`API_SaveRole` / `API_CreateRole`) — it should NOT just clear the selection. Common bug: passing `onSave={() => setSelectedRoleId(null)}` which ignores the payload entirely.
- **RoleEditor onDelete:** The `onDelete` callback must call `API_DeleteRole(roleId)` and then clear the selection. Common bug: passing `onDelete={() => setSelectedRoleId(null)}` without calling the API.

### PermisosSidebar.jsx

- **Layout:** Fixed-height sidebar with search input at top, scrollable role list below.
- **View toggle:** ToggleButtonGroup at the top switches between "Roles" and "Personas" views. Only one view shown at a time to save space. Uses `exclusive` mode with `ShieldIcon` for roles and `PersonIcon` for personas. The search TextField only renders in "personas" view (with `autoFocus`).
- **ToggleButton styling (user preference):**
  - Touching edges must have `borderRadius: 0` (the inner edges where buttons meet).
  - Active button: `bgcolor: primary.main` + `color: white`.
  - Inactive button: `border: 1px solid divider` + `bgcolor: white`.
  - Compact padding: `py: 0.75`, icons at 18px.
  - Overall borderRadius: 2px (small, not large).
  - Use `sx` prop directly on ToggleButton, not on ToggleButtonGroup.
- **Category grouping:** Roles grouped by `category` field. Only one category open at a time (controlled accordion pattern). State `openCategory` lives in the sidebar, passed down to `CategoryGroup` as `isOpen` + `onToggle`.
- **CategoryGroup component:** Receives `isOpen`, `onToggle`, `category`, `roles`, `selectedRoleId`, `onSelect`. Shows category name in uppercase with count chip. Each role is a clickable ListItemButton with role name and permission count chip.
- **Search:** Debounced text input, calls `API_SearchUsers(query)`. Only visible in "personas" view.
- **New role button:** At bottom of sidebar (only in "roles" view). Calls `onNewRole()` to set `selectedRoleId = "new"`.

## ListCardItem Navigation (CRITICAL)

- **NEVER use `LinkComponent` or `component={Link}` on `ListItemButton` for navigation** — these props don't work reliably in practice. The `ListItemButton` renders as a `<div>` with `role="button"` even when `component={Link}` and `to={...}` are passed.
- **Correct pattern:** Wrap the entire `ListCardItem` in a `<Link to={...}>` from react-router-dom. The `<Link>` creates a proper `<a>` element with `href`. IconButtons inside the wrapper (for edit/delete) still work because they have their own `LinkComponent={Link}` which stops event propagation.
- **Subgroup handling:** When a list item has sub-items (expandable), do NOT wrap it in a `<Link>`. Use `onClick: handleOpen` to toggle expansion instead. The `canNavigate` condition should check: `permissions.ver && (subgroup || data.role || isAdmin)` — if the item has sub-items, it should expand, not navigate.
- **Example pattern:**
  ```jsx
  {canNavigate ? (
    <Link to={data.id} style={{ textDecoration: "none", color: "inherit" }}>
      <ListCardItem ... />
    </Link>
  ) : (
    <ListCardItem onClick={() => handleOpen(data.id)} ... />
  )}
  ```
