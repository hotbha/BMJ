#!/bin/bash
# Why are deliveries being re-scheduled? Read-only forensics.
cd /home/bmj/bmj || exit 1

echo "=== nginx: recent webhook requests and their status codes ==="
sudo -n true 2>/dev/null && SUDO="sudo -n" || SUDO=""
if [ -n "$SUDO" ]; then
  $SUDO grep -h "api/webhooks" /var/log/nginx/access.log 2>/dev/null | tail -15
  echo "--- status tallies for webhook requests ---"
  $SUDO grep -h "api/webhooks" /var/log/nginx/access.log 2>/dev/null | awk '{print $9}' | sort | uniq -c | sort -rn | head
else
  echo "(no passwordless sudo; reading the container-visible log instead)"
  docker logs bmj-api 2>&1 | grep -aiE "401|Unauthorized|webhook" | tail -10
fi

echo
echo "=== application log: any webhook activity at all? ==="
docker logs bmj-api 2>&1 | grep -aiE "webhook|Event already processed|Processing customer|Processing subscription" | tail -10 || echo "(none)"

echo
echo "=== does the server still expect the OLD webhook password? ==="
echo -n "container WEBHOOK_PASSWORD sha256 : "
docker exec bmj-api printenv WEBHOOK_PASSWORD | tr -d '\r\n' | sha256sum | cut -d' ' -f1
echo -n "old value sha256 (for comparison)  : "
printf '%s' 'rADHASOAMI@0' | sha256sum | cut -d' ' -f1
echo -n "container WEBHOOK_USERNAME        : "
docker exec bmj-api printenv WEBHOOK_USERNAME

echo
echo "=== .env vs container ==="
echo -n ".env WEBHOOK_PASSWORD sha256      : "
grep '^WEBHOOK_PASSWORD=' .env | cut -d= -f2- | tr -d '\r\n' | sha256sum | cut -d' ' -f1
