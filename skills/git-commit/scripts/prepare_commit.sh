#!/usr/bin/env bash
# prepare_commit.sh — Mechanical data collection for git-commit skill.
# Run in the repo's working directory. Outputs structured data for the LLM
# to make semantic decisions (grouping, type, message).
#
# Usage:
#   bash scripts/prepare_commit.sh           # staged + unstaged
#   bash scripts/prepare_commit.sh --staged   # staged only
#   bash scripts/prepare_commit.sh --unstaged # unstaged only

set -euo pipefail

MODE="all"
if [[ "${1:-}" == "--staged" ]]; then
  MODE="staged"
elif [[ "${1:-}" == "--unstaged" ]]; then
  MODE="unstaged"
fi

# --- Guard: must be inside a git repo ---
if ! git rev-parse --is-inside-work-tree &>/dev/null; then
  echo "ERROR: not inside a git repository"
  exit 1
fi

echo "=== GIT COMMIT PREP ==="
echo "REPO: $(git rev-parse --show-toplevel)"
echo "BRANCH: $(git branch --show-current 2>/dev/null || echo 'detached')"
echo "MODE: $MODE"
echo ""

# --- 1. Status ---
echo "--- STATUS (porcelain) ---"
git status --porcelain
echo ""

# --- 2. Diff ---
if [[ "$MODE" == "staged" || "$MODE" == "all" ]]; then
  STAGED_COUNT=$(git diff --staged --name-only 2>/dev/null | wc -l || echo 0)
  echo "--- STAGED FILES ($STAGED_COUNT) ---"
  if [[ "$STAGED_COUNT" -gt 0 ]]; then
    git diff --staged --stat
    echo ""
    echo "--- STAGED DIFF ---"
    git diff --staged
  else
    echo "(nothing staged)"
  fi
  echo ""
fi

if [[ "$MODE" == "unstaged" || "$MODE" == "all" ]]; then
  UNSTAGED_COUNT=$(git diff --name-only 2>/dev/null | wc -l || echo 0)
  echo "--- UNSTAGED FILES ($UNSTAGED_COUNT) ---"
  if [[ "$UNSTAGED_COUNT" -gt 0 ]]; then
    git diff --stat
    echo ""
    echo "--- UNSTAGED DIFF ---"
    git diff
  else
    echo "(nothing unstaged)"
  fi
  echo ""
fi

# --- 3. Recent commit history (style reference) ---
echo "--- RECENT COMMITS (last 20) ---"
git log --oneline -20 2>/dev/null || echo "(no commits yet)"
echo ""

# --- 4. Secret detection ---
echo "--- SECRET SCAN ---"
SECRET_PATTERNS='(\.env$|\.env\.|credentials\.json|\.pem$|\.key$|\.p12$|id_rsa|id_ed25519|\.pfx$|secret\.|\.secret$|serviceaccount.*\.json)'
SUSPECT_FILES=""
if [[ "$MODE" == "staged" || "$MODE" == "all" ]]; then
  STAGED_FILES=$(git diff --staged --name-only 2>/dev/null || true)
  if [[ -n "$STAGED_FILES" ]]; then
    SUSPECT_FILES=$(echo "$STAGED_FILES" | grep -iE "$SECRET_PATTERNS" || true)
  fi
fi
if [[ "$MODE" == "unstaged" || "$MODE" == "all" ]]; then
  UNSTAGED_FILES=$(git diff --name-only 2>/dev/null || true)
  if [[ -n "$UNSTAGED_FILES" ]]; then
    MORE=$(echo "$UNSTAGED_FILES" | grep -iE "$SECRET_PATTERNS" || true)
    SUSPECT_FILES="${SUSPECT_FILES}${MORE:+$'\n'$MORE}"
  fi
fi
if [[ -n "$SUSPECT_FILES" ]]; then
  echo "WARNING: Potential secret/sensitive files detected:"
  echo "$SUSPECT_FILES" | sort -u | sed 's/^/  /'
  echo "DO NOT commit these without explicit user confirmation."
else
  echo "(no sensitive files detected)"
fi
echo ""

# --- 5. Type hints (heuristic from file patterns) ---
echo "--- TYPE HINTS (heuristic) ---"
ALL_CHANGED=""
if [[ "$MODE" == "staged" || "$MODE" == "all" ]]; then
  ALL_CHANGED+=$(git diff --staged --name-only 2>/dev/null || true)
fi
if [[ "$MODE" == "unstaged" || "$MODE" == "all" ]]; then
  UNSTAGED=$(git diff --name-only 2>/dev/null || true)
  ALL_CHANGED="${ALL_CHANGED:+$ALL_CHANGED$'\n'}$UNSTAGED"
fi

if [[ -z "$ALL_CHANGED" ]]; then
  echo "(no changes to analyze)"
  exit 0
fi

echo "$ALL_CHANGED" | sort -u | while read -r f; do
  [[ -z "$f" ]] && continue
  HINT=""
  case "$f" in
    *.md|*.rst|*.txt|docs/*|doc/*|README*|CHANGELOG*|LICENSE*) HINT="docs" ;;
    *test*|*spec*|tests/*|__tests__/*|*.test.*|*.spec.*) HINT="test" ;;
    .github/*|*.yml|*.yaml|Jenkinsfile|Dockerfile*|.dockerignore) HINT="ci/build" ;;
    package.json|package-lock.json|requirements*.txt|pyproject.toml|Cargo.toml|go.mod|go.sum|pom.xml|build.gradle) HINT="build" ;;
    *.css|*.scss|*.less|*.html) HINT="style/feat" ;;
    *.py|*.js|*.ts|*.jsx|*.tsx|*.go|*.rs|*.java|*.rb|*.php|*.c|*.cpp|*.h|*.swift|*.kt) HINT="feat/fix/refactor" ;;
    *.json|*.toml|*.ini|*.cfg|*.conf) HINT="chore/config" ;;
    *) HINT="chore" ;;
  esac
  echo "  $f → $HINT"
done
echo ""
echo "=== END PREP ==="