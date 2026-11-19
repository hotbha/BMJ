#!/bin/bash
# Install the systemd unit and the nginx proxy. Run as root:
#   sudo -S -p '' bash install-services.sh < /home/bmj/.sudo_pw
set -euo pipefail
cd /home/bmj/bmj

echo "=== systemd unit ==="
sed -i 's/\r$//' bmj-stack.service
install -m 644 bmj-stack.service /etc/systemd/system/bmj-stack.service
systemctl daemon-reload
systemctl enable bmj-stack.service >/dev/null 2>&1 || true
echo -n "enabled: "; systemctl is-enabled bmj-stack.service

echo "=== nginx proxy ==="
python3 apply-nginx.py || { echo "apply-nginx failed"; exit 1; }

echo "=== nginx config test ==="
nginx -t

echo "=== reload ==="
systemctl reload nginx
echo "nginx reloaded"
