# Discovery pipelines

Run from the repository root. Adapt the exclusion list if the project has additional generated or dependency directories.

## Directory depth

```bash
find . \
  -type d \
  -not -path '*/.git/*' \
  -not -path '*/node_modules/*' \
  -not -path '*/vendor/*' \
  -not -path '*/dist/*' \
  -not -path '*/build/*' \
  -not -path '*/coverage/*' \
  -not -path '*/.next/*' \
  -not -path '*/.nuxt/*' \
  -not -path '*/.turbo/*' \
  -not -path '*/.cache/*' \
  | awk -F/ '{print NF-1}' | sort -n | uniq -c
```

## Representative files

```bash
find . \
  -type f \
  -not -path '*/.git/*' \
  -not -path '*/node_modules/*' \
  -not -path '*/vendor/*' \
  -not -path '*/dist/*' \
  -not -path '*/build/*' \
  -not -path '*/coverage/*' \
  -not -path '*/.next/*' \
  -not -path '*/.nuxt/*' \
  -not -path '*/.turbo/*' \
  -not -path '*/.cache/*' \
  | sed 's|^\./||' \
  | sort \
  | head -300
```

## Important config and context files

```bash
find . \
  -type f \( \
    -name "README.md" -o \
    -name "AGENTS.md" -o \
    -name "CLAUDE.md" -o \
    -name "package.json" -o \
    -name "pnpm-workspace.yaml" -o \
    -name "yarn.lock" -o \
    -name "package-lock.json" -o \
    -name "bun.lockb" -o \
    -name "turbo.json" -o \
    -name "nx.json" -o \
    -name "pyproject.toml" -o \
    -name "requirements.txt" -o \
    -name "uv.lock" -o \
    -name "poetry.lock" -o \
    -name "go.mod" -o \
    -name "Cargo.toml" -o \
    -name "Makefile" -o \
    -name "Dockerfile" -o \
    -name "docker-compose.yml" -o \
    -name ".editorconfig" -o \
    -name "tsconfig.json" -o \
    -name "vite.config.*" -o \
    -name "next.config.*" \
  \) \
  -not -path '*/node_modules/*' \
  -not -path '*/.git/*' \
  | sort
```
