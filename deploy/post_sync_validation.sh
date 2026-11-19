#!/bin/bash
# Re-run the four validations after the configuration sync. Read-only except the OTP/email
# triggers, which are the flows under test.
cd /home/bmj/bmj || exit 1
API=http://127.0.0.1:8080
QA_PHONE=9999999911          # synthetic, unused in production, not a real subscriber
QA_EMAIL=qa-nonexistent@bookmyjuice.co.in   # own domain, mailbox does not exist (no third party)

echo "############ A. OTP validation ############"
echo "-- POST /api/auth/send-otp ($QA_PHONE) --"
curl -s -m 25 -o /tmp/otp.json -w "http=%{http_code} time=%{time_total}s\n" \
  -H "Content-Type: application/json" -d "{\"phone\":\"$QA_PHONE\"}" \
  $API/api/auth/send-otp
echo -n "response: "; head -c 200 /tmp/otp.json; echo

echo
echo "-- backend log: OTP / SMS provider --"
docker logs bmj-api --since 3m 2>&1 | grep -aiE "otp|fast2sms|sms" | tail -8 || echo "(no otp lines)"

echo
echo "############ B. SMS delivery (provider response) ############"
docker logs bmj-api --since 3m 2>&1 | grep -aiE "SMS sent|SMS failed|Fast2SMS|SMS\]|error" | tail -8 || echo "(no sms lines)"

echo
echo "############ C. Email validation ############"
echo "-- POST /api/auth/reset-password-email ($QA_EMAIL) --"
curl -s -m 30 -o /tmp/mail.json -w "http=%{http_code} time=%{time_total}s\n" \
  -H "Content-Type: application/json" -d "{\"email\":\"$QA_EMAIL\"}" \
  $API/api/auth/reset-password-email
echo -n "response: "; head -c 200 /tmp/mail.json; echo
echo "-- backend log: mail --"
docker logs bmj-api --since 3m 2>&1 | grep -aiE "mail|smtp|javax.mail|MailSend|Authentication failed" | tail -8 || echo "(no mail lines)"

echo
echo "############ D. Webhook validation ############"
docker exec -i bmj-sql sh -c 'exec mysql -u root -p"$MYSQL_ROOT_PASSWORD" bmj_db -t -e \
 "SELECT IFNULL(processing_status,chr(45)) AS status, COUNT(*) AS n FROM webhook_events GROUP BY processing_status;"' 2>/dev/null
echo "-- recent Chargebee deliveries --"
sudo -S -p '' grep -h "ChargeBee" /var/log/nginx/access.log 2>/dev/null < /home/bmj/.pw | tail -4 || echo "(none)"

echo
echo "-- health --"
curl -s -m 10 $API/api/health; echo
