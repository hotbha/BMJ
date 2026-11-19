#!/bin/bash
# Compare the container's key with .env, normalising trailing CR/space on both sides.
cd /home/bmj/bmj || exit 1

echo -n "container (normalised) : "
docker exec bmj-api printenv CHARGEBEE_API_KEY | tr -d '\r\n ' | sha256sum | cut -d' ' -f1

echo -n ".env      (normalised) : "
grep '^CHARGEBEE_API_KEY=' .env | cut -d= -f2- | tr -d '\r\n ' | sha256sum | cut -d' ' -f1

echo -n "container byte length  : "
docker exec bmj-api printenv CHARGEBEE_API_KEY | tr -d '\n' | wc -c

echo -n ".env byte length       : "
grep '^CHARGEBEE_API_KEY=' .env | cut -d= -f2- | tr -d '\n' | wc -c

echo "--- does the container reach chargebee at all? ---"
docker exec bmj-api sh -c 'wget -q -S -O /dev/null --timeout=10 --header="Authorization: Basic $(printf "%s:" "$CHARGEBEE_API_KEY" | base64 -w0)" "https://bookmyjuice-test.chargebee.com/api/v2/customers?limit=1" 2>&1 | head -3' 2>&1 | head -5
