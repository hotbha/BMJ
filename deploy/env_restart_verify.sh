#!/bin/bash
# Restart only bmj-api and verify the runtime configuration. Values are never printed.
cd /home/bmj/bmj || exit 1

echo "=== docker compose up -d bmj-api ==="
docker compose --env-file .env -f docker-compose.prod.yml up -d bmj-api 2>&1 | tail -4

echo
echo "=== waiting for boot ==="
for i in $(seq 1 20); do
  sleep 5
  if docker exec bmj-api sh -c 'curl -s -m 3 -o /dev/null http://127.0.0.1:8080/api/health' 2>/dev/null; then
    echo "api responding after $((i*5))s"; break
  fi
done

echo
echo "=== runtime configuration (presence + length only) ==="
for k in FAST2SMS_API_KEY MAIL_PASSWORD WEBHOOK_USERNAME WEBHOOK_PASSWORD CHARGEBEE_API_KEY \
         MAIL_HOST MAIL_USERNAME JWT_SECRET ADMIN_PASSWORD DB_PASSWORD GOOGLE_CLIENT_ID; do
  v=$(docker exec bmj-api printenv "$k" 2>/dev/null)
  printf '%-22s %s\n' "$k" "$(if [ -n "$v" ]; then echo "present len=${#v}"; else echo 'MISSING'; fi)"
done

echo
echo "=== container state ==="
docker inspect --format 'restarts={{.RestartCount}} status={{.State.Status}}' bmj-api
docker exec bmj-api sha256sum /app/app.jar | cut -d' ' -f1

echo
echo "=== startup log tail ==="
docker logs bmj-api 2>&1 | grep -aE "Started bmjServer|Webhook Basic Auth|Could not resolve|APPLICATION FAILED|HikariPool-1 - Start completed" | tail -5
