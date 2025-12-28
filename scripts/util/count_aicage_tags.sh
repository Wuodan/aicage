#!/usr/bin/env bash
set -euo pipefail

# Count and sanity-check GHCR tags for ghcr.io/aicage/aicage against your expected base/agent matrix.
# Assumptions:
# - Tag names contain BOTH the agent token and the base token somewhere in the tag name
#   (e.g. "codex-ubuntu-latest", "copilot-debian-0.0.1", etc.)
# - If your tag scheme differs, adjust match_tag() below.

registry_api_url="https://ghcr.io/v2"
registry_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository"
repo="aicage/aicage"

bases=(act ubuntu fedora node alpine debian)
agents=(claude copilot codex qwen droid opencode goose gemini)

ghcr_pull_token() {
  local repo="$1"
  curl -fsSL \
    "${registry_token_url}:${repo}:pull" \
    | jq -r '.token'
}

ghcr_list_all_tags() {
  local repo="$1"
  local url="${registry_api_url}/${repo}/tags/list?n=1000"
  local token resp body next
  token="$(ghcr_pull_token "$repo")"

  while [[ -n "$url" ]]; do
    resp="$(
      curl -fsSL -i \
        -H "Authorization: Bearer ${token}" \
        "$url"
    )"

    body="$(sed '1,/^\r\{0,1\}$/d' <<<"$resp")"
    echo "$body" | jq -r '.tags[]?'

    next="$(sed -n 's/.*<\([^>]*\)>;[[:space:]]*rel="next".*/\1/pI' <<<"$resp")"
    url="$next"
  done
}

# Echo "agent base" if tag matches exactly one agent and exactly one base, else return non-zero.
match_tag() {
  local tag="$1"
  local t="" b=""

  for x in "${agents[@]}"; do
    if [[ "$tag" == *"$x"* ]]; then
      if [[ -n "$t" && "$t" != "$x" ]]; then
        return 1  # ambiguous agent
      fi
      t="$x"
    fi
  done

  for x in "${bases[@]}"; do
    if [[ "$tag" == *"$x"* ]]; then
      if [[ -n "$b" && "$b" != "$x" ]]; then
        return 1  # ambiguous base
      fi
      b="$x"
    fi
  done

  [[ -n "$t" && -n "$b" ]] || return 1
  printf "%s %s\n" "$t" "$b"
}

main() {
  mapfile -t tags < <(ghcr_list_all_tags "$repo" | sort -u)
  echo "Remote unique tag count: ${#tags[@]}"
  echo

  # Matched matrix
  declare -A seen

  # Counters (must be associative; initialize explicitly under `set -u`)
  declare -A per_base=()
  declare -A per_agent=()

  declare -a unmatched=()

  for tag in "${tags[@]}"; do
    if out="$(match_tag "$tag" 2>/dev/null)"; then
      agent="${out%% *}"
      base="${out##* }"
      seen["$agent|$base"]=1

      : "${per_base["$base"]:=0}"
      : "${per_agent["$agent"]:=0}"
      per_base["$base"]=$(( per_base["$base"] + 1 ))
      per_agent["$agent"]=$(( per_agent["$agent"] + 1 ))
    else
      unmatched+=("$tag")
    fi
  done

  echo "Tags per base (matched by substring):"
  for b in "${bases[@]}"; do
    printf "  %-8s %s\n" "$b" "${per_base[$b]:-0}"
  done
  echo

  echo "Tags per agent (matched by substring):"
  for agent in "${agents[@]}"; do
    printf "  %-8s %s\n" "$agent" "${per_agent[$agent]:-0}"
  done
  echo

  echo "Missing combinations (expected 9 agents per base => 54 combos):"
  missing=0
  for b in "${bases[@]}"; do
    for agent in "${agents[@]}"; do
      if [[ -z "${seen["$agent|$b"]+x}" ]]; then
        echo "  missing: agent=$agent base=$b"
        missing=$((missing + 1))
      fi
    done
  done
  echo "Missing combo count: $missing"
  echo

  if ((${#unmatched[@]} > 0)); then
    echo "Unmatched/ambiguous tags (didn't map cleanly to exactly 1 agent + 1 base):"
    printf '  %s\n' "${unmatched[@]}"
    echo
    echo "If these are valid tags, your naming scheme likely doesn't include plain agent/base tokens."
    echo "Adjust match_tag() to parse your actual tag format."
  fi
}

main "$@"
