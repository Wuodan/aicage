#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <command> [args...]" >&2
  exit 1
fi

# 1) read non-recursive content of ~ before
# before="$(ls -1A "$HOME" | sort)"
before="$(find "$HOME" | sort)"

# 2) run the given command, kill after N seconds
TIMEOUT="${TIMEOUT:-5}"   # default 5s, override via env

"$@" </dev/tty >/dev/null 2>&1 &
cmd_pid=$!

sleep "$TIMEOUT"

# if still running, kill it
if kill -0 "$cmd_pid" 2>/dev/null; then
  kill "$cmd_pid" 2>/dev/null || true
  sleep 1
  kill -9 "$cmd_pid" 2>/dev/null || true
fi

wait "$cmd_pid" 2>/dev/null || true


# 3) read non-recursive content of ~ after
# after="$(ls -1A "$HOME" | sort)"
after="$(find "$HOME" | sort)"

# print diff
# diff -u <(printf "%s\n" "$before") <(printf "%s\n" "$after") || true
diff <(printf "%s\n" "$before") <(printf "%s\n" "$after") \
  | grep -E '^[<>]' || true
