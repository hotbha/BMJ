#!/bin/bash
# Has the webhook password changed since the last validation? And has anything arrived?
cd /home/bmj/bmj || exit 1

echo -n "container WEBHOOK_PASSWORD sha256 (trimmed): "
docker exec bmj-api printenv WEBHOOK_PASSWORD | tr -d '\r\n' | sha256sum | cut -d' ' -f1
echo -n "known OLD value  sha256 (trimmed)        : "
printf '%s' 'rADHASOAMI@0' | sha256sum | cut -d' ' -f1
echo -n ".env WEBHOOK_PASSWORD sha256 (trimmed)   : "
grep '^WEBHOOK_PASSWORD=' .env | cut -d= -f2- | tr -d '\r\n' | sha256sum | cut -d' ' -f1

echo
echo "=== webhook_events now ==="
docker exec -i bmj-sql sh -c 'exec mysql -u root -p"$MYSQL_ROOT_PASSWORD" bmj_db -t -e \
 "SELECT IFNULL(processing_status,chr(40)) AS status, COUNT(*) AS n FROM webhook_events GROUP BY processing_status;
  SELECT COUNT(*) AS total FROM webhook_events;"' 2>/dev/null

echo "=== users now ==="
docker exec -i bmj-sql sh -c 'exec mysql -u root -p"$MYSQL_ROOT_PASSWORD" bmj_db -t -e \
 "SELECT COUNT(*) AS users FROM users;"' 2>/dev/null

echo "=== any webhook request from Chargebee in nginx log (non-PowerShell UA)? ==="
sudo -S -p '' grep -h "api/webhooks" /var/log/nginx/access.log 2>/dev/null < /home/bmj/.pw | \
  grep -v "WindowsPowerShell" | tail -5 || echo "(none)"
