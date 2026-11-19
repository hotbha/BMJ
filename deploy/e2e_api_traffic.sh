#!/bin/bash
# Did the Android app reach the VPS API? Look for non-Chargebee, non-PowerShell clients.
cd /home/bmj/bmj || exit 1

echo "=== API requests in the last part of the nginx log, by user agent ==="
sudo -S -p '' tail -400 /var/log/nginx/access.log 2>/dev/null < /home/bmj/.pw | \
  awk '{print $9, $12}' | sed 's/"//g' | sort | uniq -c | sort -rn | head -12

echo
echo "=== any request with a Dart/OkHttp/Flutter user agent? ==="
sudo -S -p '' grep -hiE 'dart|okhttp|flutter' /var/log/nginx/access.log 2>/dev/null < /home/bmj/.pw | tail -8 || echo "(none)"

echo
echo "=== most recent 10 API requests (any client) ==="
sudo -S -p '' grep -h " /api/" /var/log/nginx/access.log 2>/dev/null < /home/bmj/.pw | tail -10

echo
echo "=== backend log: catalogue / auth activity ==="
docker logs bmj-api 2>&1 | grep -aiE "charge items|catalog|send-otp|login-otp|Identity link" | tail -10 || echo "(none)"
