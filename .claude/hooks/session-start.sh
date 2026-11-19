#!/bin/bash
# SessionStart hook: inject the graphify dependency-graph report into context so
# Claude knows the model's god nodes + community structure before searching.
# Idempotent, non-blocking. Graph artifacts are produced by `graphify update .`
# (locally) or by .github/workflows/update-graphify.yml (CI).

set -euo pipefail

# Derive project root from this script's location (robust without CLAUDE_PROJECT_DIR).
_HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
_PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "${_HOOK_DIR}/../.." && pwd)}"

readonly GRAPHIFY_TRUNCATE_LINES=160

report="${_PROJECT_DIR}/graphify-out/GRAPH_REPORT.md"
if [ -f "$report" ]; then
  size=$(wc -c < "$report" 2>/dev/null) || size=0   # || size=0 : TOCTOU guard
  if [ "$size" -lt 32768 ]; then
    cat "$report" || true
  else
    head -n "${GRAPHIFY_TRUNCATE_LINES}" "$report" || true
    echo "[graphify] Report truncated — full report at graphify-out/GRAPH_REPORT.md"
  fi
fi

# Remote-only (Claude Code Web). Desktop/CLI users install caveman manually.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

_CAVEMAN_JUST_INSTALLED=0
install_caveman() {
  command -v claude >/dev/null 2>&1 || { echo "session-start: no claude CLI; skip caveman" >&2; return 0; }
  claude plugin list 2>/dev/null | grep -q 'caveman@caveman' && return 0
  echo "session-start: installing caveman plugin..." >&2
  claude plugin marketplace add JuliusBrussee/caveman >&2 || true
  claude plugin install caveman@caveman >&2 || { echo "session-start: caveman install failed (non-fatal)" >&2; return 0; }
  _CAVEMAN_JUST_INSTALLED=1
}
activate_caveman_now() {
  command -v node >/dev/null 2>&1 || return 0
  [ -d "$HOME/.claude/plugins/cache/caveman" ] || return 0
  local js
  js=$(find "$HOME/.claude/plugins/cache/caveman" -maxdepth 4 -path '*/hooks/caveman-activate.js' -printf '%T@\t%p\n' 2>/dev/null | sort -rn | head -1 | cut -f2-)
  [ -n "$js" ] && [ -f "$js" ] && node "$js" 2>/dev/null || true
}
install_caveman
[ "${_CAVEMAN_JUST_INSTALLED}" = "1" ] && activate_caveman_now
exit 0
