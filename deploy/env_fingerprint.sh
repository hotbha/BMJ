#!/bin/bash
# Print KEY + sha256(value) for every key in .env. Values are never printed.
cd /home/bmj/bmj || exit 1
while IFS='=' read -r k v; do
  case "$k" in
    ''|'#'*) continue ;;
  esac
  v="${v%$'\r'}"
  h=$(printf '%s' "$v" | sha256sum | cut -c1-12)
  printf '%-30s %s\n' "$k" "$h"
done < .env

echo "--- metadata ---"
echo -n "crlf_lines: "; grep -c $'\r' .env || echo 0
echo -n "lines: "; wc -l < .env
echo -n "mode: "; stat -c '%a' .env
