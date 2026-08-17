#!/usr/bin/env bash
# verify-worktrees.sh — Hard Rule 3 of herdr-parallel-dev as one command.
#
# Verifies that worktree paths you created (or discovered) belong to the
# intended project's repo and sit on sane branches. This catches
# `herdr worktree create` resolving to the WRONG project: a worktree created
# inside another repo has that repo's origin URL, and the comparison below
# fails loudly.
#
# Usage:
#   verify-worktrees.sh [--format tsv|json] <project-dir> [worktree-path...]
#
#   With paths:      verify exactly those (the dispatcher passes paths parsed
#                    from `herdr worktree create` JSON responses).
#   Without paths:   discover linked worktrees via `herdr worktree list
#                    --cwd <project-dir>` (fallback: `git worktree list`).
#
# Per path checks:
#   1. exists and is a git repo/worktree
#   2. `remote get-url origin` equals the project's origin URL (exact match)
#   3. on a branch (not detached) and NOT the repo's default branch
#
# Output contract:
#   stdout is data only: TSV fields status, worktree, branch, url, dirty, ahead
#   by default, or one JSON object with status, count, results, expected_url.
#   stderr is diagnostics and the human-readable RESULT line.
# Exit: 0 all pass · 1 at least one FAIL · 2 usage/environment error.

set -u

format=tsv

usage() {
  printf 'usage: %s [--format tsv|json] <project-dir> [worktree-path...]\n' "$0" >&2
  exit 2
}

emit_json_error() {
  [ "$format" = json ] && printf '%s\n' '{"status":"error","count":0,"results":[],"expected_url":null}'
}

die_env() {
  emit_json_error
  printf 'FAIL: %s\n' "$*" >&2
  exit 2
}

if [ $# -gt 0 ]; then
  case "$1" in
    --format)
      [ $# -ge 2 ] || usage
      format=$2
      shift 2
      ;;
    --format=tsv) format=tsv; shift ;;
    --format=json) format=json; shift ;;
    --help|-h) usage ;;
    --) shift ;;
    -*) printf 'FAIL: unknown option %s\n' "$1" >&2; usage ;;
  esac
fi
case "$format" in
  tsv|json) ;;
  *) usage ;;
esac

[ $# -ge 1 ] || die_env "missing project directory"
PROJECT=$1
shift
command -v jq >/dev/null 2>&1 || die_env "jq is required"

git -C "$PROJECT" rev-parse --is-inside-work-tree >/dev/null 2>&1 \
  || die_env "$PROJECT is not a git repository"
EXPECTED_URL=$(git -C "$PROJECT" remote get-url origin 2>/dev/null) \
  || die_env "$PROJECT has no origin remote"
DEFAULT=$(git -C "$PROJECT" symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null)
DEFAULT=${DEFAULT#origin/}
[ -n "$DEFAULT" ] || die_env "cannot resolve origin/HEAD for $PROJECT (run: git remote set-head origin --auto)"

fail_count=0
targets=()
if [ $# -gt 0 ]; then
  for p in "$@"; do targets+=("$p"); done
else
  while IFS= read -r p; do
    [ -n "$p" ] && targets+=("$p")
  done < <(
    herdr worktree list --cwd "$PROJECT" 2>/dev/null \
      | jq -r '.result.worktrees[]? | select(.is_linked_worktree == true) | .path' 2>/dev/null \
      || git -C "$PROJECT" worktree list --porcelain | awk '/^worktree /{print $2}'
  )
fi

json_results=()
if [ "$format" = tsv ]; then
  printf 'status\tworktree\tbranch\turl\tdirty\tahead\n'
fi

if [ ${#targets[@]} -eq 0 ]; then
  if [ "$format" = json ]; then
    expected_json=$(jq -Rn --arg value "$EXPECTED_URL" '$value')
    printf '{"status":"pass","count":0,"results":[],"expected_url":%s}\n' "$expected_json"
  fi
  printf 'OK: no linked worktrees registered under %s (nothing to verify)\n' "$PROJECT" >&2
  exit 0
fi

for W in "${targets[@]}"; do
  if [ ! -d "$W" ] || ! git -C "$W" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    url="<not-a-worktree>"
    branch=""
    dirty=0
    ahead="?"
    reason="not a directory / not a git worktree"
  else
    url=$(git -C "$W" remote get-url origin 2>/dev/null || echo "<no origin>")
    branch=$(git -C "$W" branch --show-current 2>/dev/null)
    dirty=$(git -C "$W" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
    ahead=$(git -C "$W" rev-list --count "origin/$DEFAULT..HEAD" 2>/dev/null || echo "?")
    reason=""
    [ "$url" = "$EXPECTED_URL" ] || reason="origin is $url, expected $EXPECTED_URL"
    if [ -z "$reason" ]; then [ -n "$branch" ] || reason="detached HEAD"; fi
    if [ -z "$reason" ] && [ "$branch" = "$DEFAULT" ]; then
      reason="checked out on default branch '$DEFAULT'"
    fi
  fi

  case "$dirty" in ''|*[!0-9]*) dirty=0 ;; esac
  if [ -n "$reason" ]; then status=FAIL; ok=false; fail_count=$((fail_count + 1)); else status=OK; ok=true; fi

  if [ "$format" = tsv ]; then
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$status" "$W" "$branch" "$url" "$dirty" "$ahead"
  else
    json_results+=("$(jq -cn \
      --arg path "$W" --arg branch "$branch" --arg url "$url" --arg ahead "$ahead" \
      --arg reason "$reason" --argjson ok "$ok" --argjson dirty "$dirty" \
      '{path:$path, branch:(if $branch == "" then null else $branch end), url:$url, ok:$ok, dirty:$dirty, ahead:(if $ahead == "?" then null else ($ahead|tonumber) end), reason:(if $reason == "" then null else $reason end)}')")
  fi
done

if [ "$format" = json ]; then
  results_json=""
  for result in "${json_results[@]}"; do
    [ -n "$results_json" ] && results_json="${results_json},"
    results_json="${results_json}${result}"
  done
  expected_json=$(jq -Rn --arg value "$EXPECTED_URL" '$value')
  if [ "$fail_count" -gt 0 ]; then status=fail; else status=pass; fi
  printf '{"status":"%s","count":%d,"results":[%s],"expected_url":%s}\n' \
    "$status" "${#targets[@]}" "$results_json" "$expected_json"
fi

if [ "$fail_count" -gt 0 ]; then
  printf 'RESULT: %d FAIL — do not dispatch agents; fix/remove the failing worktrees first\n' "$fail_count" >&2
  exit 1
fi
printf 'RESULT: all %d worktree(s) verified against %s\n' "${#targets[@]}" "$EXPECTED_URL" >&2
