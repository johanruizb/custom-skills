#!/usr/bin/env bash
# Compact inspector and deterministic executor for the git-commit skill.
#
# Usage:
#   bash prepare_commit.sh [inspect] [--staged|--unstaged]
#   bash prepare_commit.sh commit --message "type(scope): summary" \
#     [--allow-sensitive] [--allow-detached] [-- path...]

set -euo pipefail

SENSITIVE_PATHS=()
COMMIT_PATHS=()

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

usage() {
  cat <<'EOF'
Usage:
  prepare_commit.sh [inspect] [--staged|--unstaged]
  prepare_commit.sh commit --message "type(scope): summary" \
    [--allow-sensitive] [--allow-detached] [-- path...]

inspect:
  Print compact status, sensitive-path warnings, diff stats, and five recent subjects.

commit:
  Commit the existing index, or stage explicit paths when the index is empty.
  Existing staged changes and explicit paths are never mixed.
  --allow-sensitive is valid only after explicit user confirmation.
  --allow-detached is valid only after explicit user confirmation.
EOF
}

ensure_git_repo() {
  local inside
  inside=$(git rev-parse --is-inside-work-tree 2>/dev/null || true)
  [[ "$inside" == "true" ]] || die "not inside a Git working tree"
}

active_operation() {
  local marker
  local marker_path

  for marker in MERGE_HEAD CHERRY_PICK_HEAD REVERT_HEAD; do
    marker_path=$(git rev-parse --git-path "$marker")
    if [[ -e "$marker_path" ]]; then
      printf '%s\n' "$marker"
      return
    fi
  done

  for marker in rebase-merge rebase-apply; do
    marker_path=$(git rev-parse --git-path "$marker")
    if [[ -d "$marker_path" ]]; then
      printf '%s\n' rebase
      return
    fi
  done

  printf '%s\n' none
}

has_staged_changes() {
  local status

  if git diff --cached --quiet --; then
    return 1
  else
    status=$?
  fi

  ((status == 1)) || die "unable to inspect staged changes"
  return 0
}

has_unstaged_changes() {
  local status

  if git diff --quiet --; then
    return 1
  else
    status=$?
  fi

  ((status == 1)) || die "unable to inspect unstaged changes"
  return 0
}

is_sensitive_path() {
  local path=$1
  local result=1
  local restore_nocase=false

  if ! shopt -q nocasematch; then
    shopt -s nocasematch
    restore_nocase=true
  fi

  case "$path" in
    .env.example | */.env.example | .env.sample | */.env.sample | \
      .env.template | */.env.template | .env.dist | */.env.dist)
      result=1
      ;;
    *)
      case "$path" in
        .env | */.env | .env.* | */.env.* | \
          *credentials.json | *.pem | *.key | *.p12 | *.pfx | \
          id_rsa | */id_rsa | id_ed25519 | */id_ed25519 | \
          secret.* | */secret.* | *.secret | */*.secret | \
          *serviceaccount*.json | *service-account*.json)
          result=0
          ;;
      esac
      ;;
  esac

  [[ "$restore_nocase" == false ]] || shopt -u nocasematch
  return "$result"
}

add_sensitive_path() {
  local candidate=$1
  local existing

  for existing in "${SENSITIVE_PATHS[@]}"; do
    [[ "$existing" == "$candidate" ]] && return
  done
  SENSITIVE_PATHS+=("$candidate")
}

scan_path_file() {
  local scan_file=$1
  local path

  while IFS= read -r -d '' path; do
    if is_sensitive_path "$path"; then
      add_sensitive_path "$path"
    fi
  done <"$scan_file"
}

scan_git_paths() {
  local scan_file
  local status

  scan_file=$(mktemp "${TMPDIR:-/tmp}/git-commit-scan.XXXXXX") ||
    die "unable to create temporary scan file"

  if "$@" >"$scan_file"; then
    scan_path_file "$scan_file"
    rm "$scan_file"
    return
  else
    status=$?
  fi

  rm "$scan_file"
  die "unable to inspect candidate paths (git exit $status)"
}

collect_sensitive_paths() {
  local mode=$1
  SENSITIVE_PATHS=()

  if [[ "$mode" == "all" || "$mode" == "staged" ]]; then
    scan_git_paths git diff --cached --name-only --no-renames -z
  fi

  if [[ "$mode" == "all" || "$mode" == "unstaged" ]]; then
    scan_git_paths git diff --name-only --no-renames -z
    scan_git_paths git ls-files --others --exclude-standard -z
  fi
}

print_sensitive_paths() {
  local blocking=${1:-true}
  local path

  printf '%s\n' '--- SENSITIVE PATHS ---'
  if ((${#SENSITIVE_PATHS[@]} == 0)); then
    printf '%s\n' '(none detected by filename)'
    return
  fi

  for path in "${SENSITIVE_PATHS[@]}"; do
    printf '  %q\n' "$path"
  done
  if [[ "$blocking" == true ]]; then
    printf '%s\n' 'STOP: require explicit user confirmation before committing these paths.'
  else
    printf '%s\n' 'NOTE: confirmation is required only if a listed path enters the commit.'
  fi
}

inspect_repository() {
  local mode=${1:-all}
  local branch
  local status

  case "$mode" in
    all | staged | unstaged) ;;
    *) die "invalid inspect mode: $mode" ;;
  esac

  ensure_git_repo
  collect_sensitive_paths "$mode"
  branch=$(git branch --show-current 2>/dev/null || true)
  [[ -n "$branch" ]] || branch="(detached)"

  printf '%s\n' '=== GIT COMMIT INSPECT ==='
  printf 'BRANCH: %s\n' "$branch"
  printf 'OPERATION: %s\n' "$(active_operation)"
  printf 'MODE: %s\n\n' "$mode"

  print_sensitive_paths false
  printf '\n%s\n' '--- STATUS ---'
  status=$(git status --short --untracked-files=normal)
  if [[ -n "$status" ]]; then
    printf '%s\n' "$status"
  else
    printf '%s\n' '(clean)'
  fi

  if [[ "$mode" == "all" || "$mode" == "staged" ]]; then
    printf '\n%s\n' '--- STAGED SUMMARY ---'
    if has_staged_changes; then
      git diff --cached --stat
    else
      printf '%s\n' '(none)'
    fi
  fi

  if [[ "$mode" == "all" || "$mode" == "unstaged" ]]; then
    printf '\n%s\n' '--- UNSTAGED TRACKED SUMMARY ---'
    if has_unstaged_changes; then
      git diff --stat
    else
      printf '%s\n' '(none)'
    fi
  fi

  printf '\n%s\n' '--- RECENT SUBJECTS (5) ---'
  git log -5 --format='  %s' 2>/dev/null || printf '%s\n' '(no commits yet)'
  printf '%s\n' '=== END INSPECT ==='
}

validate_message() {
  local message=$1
  local subject=${message%%$'\n'*}
  local pattern='^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([[:alnum:]_.\/-]+\))?(!)?:[[:space:]][^[:space:]].*'

  [[ -n "$subject" ]] || die "commit subject is empty"
  ((${#subject} <= 72)) || die "commit subject exceeds 72 characters"
  [[ "$subject" =~ $pattern ]] ||
    die "message must match Conventional Commits: type(scope): summary"

  shopt -s nocasematch
  if [[ "$message" =~ Co-authored-by:|Generated[[:space:]]+with|Generated[[:space:]]+by|Assisted-by: ]]; then
    die "commit message contains a co-author or AI attribution trailer"
  fi
  shopt -u nocasematch
}

collect_candidate_sensitive_paths() {
  SENSITIVE_PATHS=()
  scan_git_paths git --literal-pathspecs diff --name-only --no-renames -z -- \
    "${COMMIT_PATHS[@]}"
  scan_git_paths git --literal-pathspecs ls-files --others --exclude-standard -z -- \
    "${COMMIT_PATHS[@]}"
}

validate_commit_paths() {
  local path
  local repo_root

  repo_root=$(git rev-parse --show-toplevel)
  for path in "${COMMIT_PATHS[@]}"; do
    [[ -n "$path" ]] || die "empty commit path"
    case "$path" in
      . | ./ | .. | ../ | "$repo_root" | "$repo_root/")
        die "broad path is not allowed; pass individual task files"
        ;;
    esac
    [[ ! -d "$path" ]] ||
      die "directory path is not allowed; pass individual task files: $path"
  done
}

commit_changes() {
  local allow_detached=false
  local allow_sensitive=false
  local branch
  local message=""
  local had_staged=false
  local before_head
  local after_head
  local commit_status
  local remaining

  while (($#)); do
    case "$1" in
      -m | --message)
        shift
        (($#)) || die "--message requires a value"
        message=$1
        ;;
      --allow-sensitive)
        allow_sensitive=true
        ;;
      --allow-detached)
        allow_detached=true
        ;;
      --)
        shift
        COMMIT_PATHS=("$@")
        break
        ;;
      -h | --help)
        usage
        return
        ;;
      *)
        die "unknown commit argument: $1"
        ;;
    esac
    shift
  done

  [[ -n "$message" ]] || die "commit requires --message"
  validate_message "$message"
  ensure_git_repo
  branch=$(git symbolic-ref --quiet --short HEAD 2>/dev/null || true)
  if [[ -z "$branch" && "$allow_detached" == false ]]; then
    die "detached HEAD; require confirmation and --allow-detached"
  fi

  if [[ -n "$(git diff --name-only --diff-filter=U)" ]]; then
    die "unresolved merge conflicts detected"
  fi

  if [[ "$(active_operation)" != "none" ]]; then
    die "merge, rebase, cherry-pick, or revert operation is active"
  fi

  if has_staged_changes; then
    had_staged=true
  else
    had_staged=false
  fi

  if ((${#COMMIT_PATHS[@]} > 0)); then
    [[ "$had_staged" == false ]] ||
      die "index already has changes; commit it without paths or resolve it explicitly"

    validate_commit_paths
    collect_candidate_sensitive_paths
    if ((${#SENSITIVE_PATHS[@]} > 0)) && [[ "$allow_sensitive" == false ]]; then
      print_sensitive_paths >&2
      exit 2
    fi

    git --literal-pathspecs add -A -- "${COMMIT_PATHS[@]}"
  elif [[ "$had_staged" == false ]]; then
    die "nothing staged; pass explicit task paths after --"
  fi

  has_staged_changes || die "selected paths produced an empty index"

  collect_sensitive_paths staged
  if ((${#SENSITIVE_PATHS[@]} > 0)) && [[ "$allow_sensitive" == false ]]; then
    print_sensitive_paths >&2
    exit 2
  fi

  git diff --cached --check
  before_head=$(git rev-parse --verify HEAD 2>/dev/null || printf '%s' UNBORN)

  if git commit --message "$message"; then
    printf '\nCOMMIT: %s\n' "$(git rev-parse HEAD)"
    printf 'SUBJECT: %s\n' "$(git log -1 --format='%s')"
    remaining=$(git status --short --untracked-files=normal)
    printf '%s\n' 'REMAINING:'
    if [[ -n "$remaining" ]]; then
      printf '%s\n' "$remaining"
    else
      printf '%s\n' '(clean)'
    fi
    return
  else
    commit_status=$?
  fi

  after_head=$(git rev-parse --verify HEAD 2>/dev/null || printf '%s' UNBORN)
  if [[ "$after_head" != "$before_head" ]]; then
    printf '%s\n' \
      'ERROR: git commit returned failure but HEAD changed; inspect before retrying.' >&2
  else
    printf '%s\n' \
      'ERROR: commit failed and HEAD did not change; inspect hook output before retrying.' >&2
  fi
  exit "$commit_status"
}

main() {
  local command=${1:-inspect}

  case "$command" in
    inspect)
      shift || true
      case "${1:-}" in
        "") inspect_repository all ;;
        --staged) inspect_repository staged ;;
        --unstaged) inspect_repository unstaged ;;
        *) die "unknown inspect argument: $1" ;;
      esac
      ;;
    --staged)
      inspect_repository staged
      ;;
    --unstaged)
      inspect_repository unstaged
      ;;
    commit)
      shift
      commit_changes "$@"
      ;;
    -h | --help)
      usage
      ;;
    *)
      die "unknown command: $command"
      ;;
  esac
}

main "$@"
