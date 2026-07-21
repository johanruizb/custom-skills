# Batch-Scan Strategy for Large Directories

Used by Step 2 of the screaming-architecture-refactor skill. When `TARGET_PATH` has 50+ files, reading them one at a time is prohibitively slow. Use this two-pass approach instead.

## Pass 1 — Gather metadata in bulk

Use `execute_code` to read the first ~60 lines + imports/exports of every file in one batch. Store results in a JSON file.

```python
import json, os, re

ROOT = "/path/to/project"
TARGET = "frontend/src/components"  # relative to ROOT
results = []

for root, dirs, files in os.walk(os.path.join(ROOT, TARGET)):
    for f in files:
        path = os.path.join(root, f)
        rel = os.path.relpath(path, ROOT)
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        lines = text.split("\n")
        head = "\n".join(lines[:60])
        # Extract imports
        imports = re.findall(r"""from\s+['"]([^'"]+)['"]""", text)
        imports += re.findall(r"""import\s+['"]([^'"]+)['"]""", text)
        # Extract exports
        exports = re.findall(r"""export\s+(default\s+)?(const|function|class|let|var)\s+(\w+)""", text)
        exports = [e[2] for e in exports]
        results.append({
            "file": rel,
            "head": head,
            "imports": imports,
            "exports": exports,
            "size": len(text),
        })

json.dump(results, open("/tmp/components_inventory.json", "w"), ensure_ascii=False)
print(f"Scanned {len(results)} files")
```

## Pass 2 — Classify from metadata

Iterate over the stored JSON and assign capability + role to each file. Only re-read a file individually when the head + exports are insufficient to classify.

```python
import json

results = json.load(open("/tmp/components_inventory.json"))
for r in results:
    head = r["head"]
    exports = r["exports"]
    imports = r["imports"]
    # Classify based on:
    # - First meaningful line (not import/comment/blank)
    # - Export names (domain-specific naming)
    # - Import patterns (what domain modules it imports from)
    # - File path (which domain folder it lives in)
    # - File name conventions
    ...
```

## When to re-read individually

Only re-read a file when:
- The head doesn't contain a meaningful line (all imports, comments, or blank)
- The exports are empty and the filename is generic (e.g. `index.jsx`, `utils.js`)
- The imports reference multiple domains and you can't tell which one is primary
- The file is a barrel that re-exports from multiple submodules

## Performance

For 196 files, this approach completes in ~2 tool calls (1 for Pass 1, 1 for Pass 2) instead of 196 individual `read_file` calls. The JSON file is ~200-500KB for 196 files, well within `execute_code` limits.
