# Import-Rewrite Algorithm

Used by Step 8 and Step 9 of the screaming-architecture-refactor skill. This is the exact algorithm for computing new import paths after a file move, preserving the original import's extension pattern.

## Core Rule

**The new import path must match the original import's extension pattern, not the destination file's actual extension.**

| Original import | Destination file | Correct new import | Wrong new import |
|---|---|---|---|
| `./components/AppBar` | `shell/appbar/index.jsx` | `./components/shell/appbar` | `./components/shell/appbar/index.jsx` |
| `./components/AppBar.jsx` | `shell/appbar/index.jsx` | `./components/shell/appbar/index.jsx` | `./components/shell/appbar` |
| `@components/TextField/X` | `forms/fields/X.jsx` | `@components/forms/fields/X` | `@components/forms/fields/X.jsx` |
| `@components/TextField/X.jsx` | `forms/fields/X.jsx` | `@components/forms/fields/X.jsx` | `@components/forms/fields/X` |

## Algorithm (pseudocode)

```
function compute_new_import(original_import, importer_path, new_dest):
    orig_has_ext = os.path.splitext(original_import)[1] != ""
    
    if original_import starts with "@components/":
        # @components/ maps to frontend/src/components/
        new_rel = new_dest[len("frontend/src/components/"):]
        
        if not orig_has_ext:
            # Original had no extension — strip it from new path
            if basename(new_dest) starts with "index.":
                # Barrel: drop the index file, keep directory
                new_rel = dirname(new_rel)
            else:
                # Regular file: drop extension
                new_rel = splitext(new_rel)[0]
        
        return "@components/" + new_rel
    
    else:
        # Relative import (starts with .)
        imp_dir = dirname(importer_path)
        new_rel = relpath(new_dest, imp_dir)
        
        if not orig_has_ext:
            if basename(new_dest) starts with "index.":
                new_rel = dirname(new_rel)
            else:
                new_rel = splitext(new_rel)[0]
        
        if not new_rel starts with ".":
            new_rel = "./" + new_rel
        
        return new_rel
```

## Barrel Resolution

When an import resolves to a barrel file (e.g. `./components/AppBar` → `AppBar/index.jsx`), the new import should point to the **directory**, not the index file:

- `./components/AppBar` → `./components/shell/appbar` (not `./components/shell/appbar/index`)
- `@components/AppBar` → `@components/shell/appbar` (not `@components/shell/appbar/index`)

This matches how JavaScript/TypeScript module resolution works: `import from "./dir"` resolves to `./dir/index.js` automatically.

## Extension Detection

The original import's extension is determined by the string itself, not by the resolved file:

- `"./foo"` → no extension (orig_has_ext = false)
- `"./foo.jsx"` → has extension (orig_has_ext = true)
- `"./foo.js"` → has extension (orig_has_ext = true)

The destination file's actual extension is irrelevant for the output — only the original import's pattern matters.

## Deduplication

When scanning a file for imports to rewrite, use a `seen` set of `(old_import, new_import)` tuples to avoid duplicate rewrites of the same import string within the same file. This prevents `patch` from matching the same string twice and producing a double-replacement.
