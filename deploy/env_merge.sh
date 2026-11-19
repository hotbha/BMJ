#!/bin/bash
# Merge the incoming (local) .env onto the VPS .env.
#
# Local is the source of truth, with three deliberate exceptions that would break the
# running deployment if overwritten blindly:
#   DB_PASSWORD       - the MySQL container was initialised with the VPS value
#   DB_ROOT_PASSWORD  - same, and it is not defined locally at all
#   ADMIN_PASSWORD    - the local value is EMPTY; writing it would blank the admin account
#
set -uo pipefail
cd /home/bmj/bmj || exit 1

STAMP=$(date +%Y%m%d-%H%M%S)
cp -p .env ".env.bak-$STAMP"
echo "backup: .env.bak-$STAMP"

get() { grep -m1 "^$1=" .env | cut -d= -f2- | tr -d '\r' ; }
DB_PW=$(get DB_PASSWORD)
DB_ROOT_PW=$(get DB_ROOT_PASSWORD)
ADMIN_PW=$(get ADMIN_PASSWORD)

# normalise the incoming file to LF (it comes from Windows)
sed -i 's/\r$//' .env.incoming

# start from local, then force the three preserved values back in
grep -vE '^(DB_PASSWORD|DB_ROOT_PASSWORD|ADMIN_PASSWORD)=' .env.incoming > .env.merged
printf 'DB_PASSWORD=%s\n' "$DB_PW" >> .env.merged
printf 'DB_ROOT_PASSWORD=%s\n' "$DB_ROOT_PW" >> .env.merged
printf 'ADMIN_PASSWORD=%s\n' "$ADMIN_PW" >> .env.merged

# sanity: the preserved secrets must not be empty
for pair in "DB_PASSWORD:$DB_PW" "DB_ROOT_PASSWORD:$DB_ROOT_PW" "ADMIN_PASSWORD:$ADMIN_PW"; do
  k="${pair%%:*}"; v="${pair#*:}"
  if [ -z "$v" ]; then echo "ABORT: $k would be empty"; exit 1; fi
done

mv .env.merged .env
chmod 600 .env
rm -f .env.incoming

echo "--- merged .env ---"
echo -n "lines: "; wc -l < .env
echo -n "crlf : "; grep -c $'\r' .env || echo 0
echo -n "mode : "; stat -c '%a' .env
echo "keys  :"
cut -d= -f1 .env | grep -v '^#' | sort | tr '\n' ' '; echo
