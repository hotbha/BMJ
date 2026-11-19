#!/bin/bash
# Is the server's stored webhook credential self-consistent?
# Calls the public HTTPS endpoint from inside the container using the container's own
# WEBHOOK_USERNAME/WEBHOOK_PASSWORD. The secret is never printed.
cd /home/bmj/bmj || exit 1

echo "=== self-test: container credentials against the public endpoint ==="
docker exec bmj-api sh -c '
  U="$WEBHOOK_USERNAME"; P="$WEBHOOK_PASSWORD"
  echo "username length: ${#U}   password length: ${#P}"
  code=$(curl -s -o /dev/null -w "%{http_code}" -m 15 -u "$U:$P" \
    -H "Content-Type: application/json" -d "{}" \
    https://api.bookmyjuice.co.in/api/webhooks/subscriptions)
  echo "with container credentials -> HTTP $code   (400 = accepted, 401 = rejected)"
  code2=$(curl -s -o /dev/null -w "%{http_code}" -m 15 -u "$U:wrong-password" \
    -H "Content-Type: application/json" -d "{}" \
    https://api.bookmyjuice.co.in/api/webhooks/subscriptions)
  echo "with a wrong password      -> HTTP $code2  (expect 401)"
'

echo
echo "=== most recent Chargebee delivery attempts (all statuses) ==="
sudo -S -p '' grep -h "api/webhooks" /var/log/nginx/access.log 2>/dev/null < /home/bmj/.pw | \
  grep -i "ChargeBee" | tail -8

echo
echo "=== have ANY Chargebee deliveries ever succeeded? ==="
sudo -S -p '' grep -h "api/webhooks" /var/log/nginx/access.log 2>/dev/null < /home/bmj/.pw | \
  grep -i "ChargeBee" | awk '{print $9}' | sort | uniq -c
