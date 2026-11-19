#!/bin/bash
# Compare the Chargebee API key the container holds with the one that worked earlier,
# WITHOUT printing either key. Read-only.
cd /home/bmj/bmj || exit 1

echo -n "container key sha256 : "
docker exec bmj-api printenv CHARGEBEE_API_KEY | tr -d '\n' | sha256sum | cut -d' ' -f1

echo -n ".env key sha256      : "
grep '^CHARGEBEE_API_KEY=' .env | cut -d= -f2- | tr -d '\n' | sha256sum | cut -d' ' -f1

echo -n "container key length : "
docker exec bmj-api printenv CHARGEBEE_API_KEY | tr -d '\n' | wc -c

echo -n "container site       : "
docker exec bmj-api printenv CHARGEBEE_SITE
