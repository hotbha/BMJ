#!/bin/bash
# Trigger the real SMTP path: email verification code for a QA address we own
# (mailbox does not need to exist - what matters is the SMTP handshake result).
cd /home/bmj/bmj || exit 1
QA_EMAIL=qa-nonexistent@bookmyjuice.co.in

echo "-- POST /api/auth/send-email-verification --"
curl -s -m 40 -o /tmp/m.json -w 'http=%{http_code} time=%{time_total}s\n' \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"$QA_EMAIL\"}" \
  http://127.0.0.1:8080/api/auth/send-email-verification
echo -n "response: "; head -c 300 /tmp/m.json; echo

echo
echo "-- mail-related log lines --"
docker logs bmj-api --since 3m 2>&1 | grep -aiE "mail|smtp|verification code|Authentication|MailSend|MailException" | tail -10 || echo "(none)"
