#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"

# Groups "_name" and "name" together by treating leading "_" as optional.
# Special case: dunder methods like "__init__" are kept intact.
find "$ROOT" -type f -name '*.py' -print0 |
  xargs -0 awk '
    {
      line = $0
      sub(/[ \t]*#.*/, "", line)  # strip trailing comment (heuristic)

      if (match(line, /^[ \t]*def[ \t]+([A-Za-z_][A-Za-z0-9_]*)[ \t]*\(/, m)) {
        raw  = m[1]

        # Normalize: strip leading underscores, except for dunder names.
        norm = raw
        if (!(raw ~ /^__.*__$/)) {
          sub(/^_+/, "", norm)
        }

        file = FILENAME
        key  = norm SUBSEP file

        if (!(key in seen)) {
          seen[key] = 1
          count[norm]++
          files[norm, file] = 1
          variants[norm, raw] = 1
        }
      }
    }

    function sort_array(a, n,    i,j,tmp) {
      for (i = 2; i <= n; i++) {
        tmp = a[i]
        j = i - 1
        while (j >= 1 && a[j] > tmp) { a[j+1] = a[j]; j-- }
        a[j+1] = tmp
      }
    }

    END {
      n_names = 0
      for (n in count) if (count[n] > 1) names[++n_names] = n
      sort_array(names, n_names)

      for (i = 1; i <= n_names; i++) {
        n = names[i]

        n_vars = 0
        for (k in variants) {
          split(k, p, SUBSEP)
          if (p[1] == n) v[++n_vars] = p[2]
        }
        sort_array(v, n_vars)

        header = "=== " n " (" count[n] " files)"
        if (n_vars > 1) {
          header = header "  [variants: "
          for (j = 1; j <= n_vars; j++) header = header v[j] (j < n_vars ? ", " : "")
          header = header "]"
        }
        header = header " ==="
        print header

        n_files = 0
        for (k in files) {
          split(k, p, SUBSEP)
          if (p[1] == n) f[++n_files] = p[2]
        }
        sort_array(f, n_files)

        for (j = 1; j <= n_files; j++) print f[j]
        print ""

        for (j = 1; j <= n_files; j++) delete f[j]
        for (j = 1; j <= n_vars; j++) delete v[j]
      }
    }
  '
