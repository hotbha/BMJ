#!/bin/bash
# Replace CHARGEBEE_API_KEY in .env with the value in .cbkey.new, restart the API,
# and verify authentication. The key is never echoed.
set -euo pipefail
cd /home/bmj/bmj

KEY="$(tr -d '\r\n' < .cbkey.new)"

# rewrite only the one line, keeping the file mode
cp -p .env .env.bak-$(date +%Y%m%d-%H%M%S)
grep -v '^CHARGEBEE_API_KEY=' .env > .env.tmp
printf 'CHARGEBEE_API_KEY=%s\n' "$KEY" >> .env.tmp
mv .env.tmp .env
chmod 600 .env
rm -f .cbkey.new

echo -n "new .env key sha256 : "
grep '^CHARGEBEE_API_KEY=' .env | cut -d= -f2- | tr -d '\r\n ' | sha256sum | cut -d' ' -f1

echo "--- restarting bmj-api ---"
docker compose --env-file .env -f docker-compose.prod.yml up -d bmj-api 2>&1 | tail -3

sleep 45
echo -n "container key sha256 : "
docker exec bmj-api printenv CHARGEBEE_API_KEY | tr -d '\r\n ' | sha256sum | cut -d' ' -f1

echo -n "health              : "
curl -s -m 10 http://127.0.0.1:8080/api/health; echo
echo -n "catalogue           : "
curl -s -m 20 -o /dev/null -w "http=%{http_code} bytes=%{size_download}\n" \
  http://127.0.0.1:8080/api/catalog/charge-items
