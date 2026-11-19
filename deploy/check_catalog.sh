#!/bin/bash
# Diagnose an empty catalogue after the 865fb16 deployment. Read-only.
cd /home/bmj/bmj || exit 1

echo "=== db counts (items, item_prices, customers, subscriptions) ==="
docker exec bmj-sql sh -c 'mysql -u root -p"$MYSQL_ROOT_PASSWORD" -N -e \
 "select (select count(*) from item_entity), (select count(*) from item_price_entity), (select count(*) from customer_entity), (select count(*) from subscription_entity);" bmj_db' 2>/dev/null

echo "=== sync / catalogue log lines ==="
docker logs bmj-api 2>&1 | grep -aiE "sync|catalog|Catalogue|chargebee" | tail -12

echo "=== catalogue endpoint (inside container network) ==="
curl -s -m 10 -o /dev/null -w "charge-items: http=%{http_code} bytes=%{size_download}\n" \
  http://127.0.0.1:8080/api/catalog/charge-items
echo -n "body head: "
curl -s -m 10 http://127.0.0.1:8080/api/catalog/charge-items | head -c 180
echo

echo "=== container start time ==="
docker inspect --format 'started={{.State.StartedAt}} restarts={{.RestartCount}}' bmj-api
