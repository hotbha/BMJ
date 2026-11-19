#!/bin/bash
# Confirm whether Chargebee's deliveries reach nginx, and with what status.
# Needs root for /var/log/nginx. The caller supplies the sudo password file.
cd /home/bmj/bmj || exit 1

echo "=== bmj group membership ==="
id bmj

echo "=== nginx access log: webhook requests (last 20) ==="
if [ -r /var/log/nginx/access.log ]; then
  grep -h "api/webhooks" /var/log/nginx/access.log | tail -20
  echo "--- status tally ---"
  grep -h "api/webhooks" /var/log/nginx/access.log | awk '{print $9}' | sort | uniq -c | sort -rn
else
  echo "direct read denied"
fi
