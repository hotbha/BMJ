#!/bin/bash
# QA account inventory on the VPS. READ-ONLY.
cd /home/bmj/bmj || exit 1

sql() {
  docker exec -i bmj-sql sh -c 'exec mysql -u root -p"$MYSQL_ROOT_PASSWORD" bmj_db -t' 2>/dev/null
}

echo "=== BMJ users (all) ==="
sql <<'Q'
SELECT id, username, IFNULL(email,'-') AS email,
       IFNULL(chargebee_customer_id,'-') AS chargebee_id
FROM users ORDER BY id;
Q

echo "=== Chargebee-mirrored customers that look like QA/E2E fixtures ==="
sql <<'Q'
SELECT customer_id, IFNULL(phone,'-') AS phone, IFNULL(email,'-') AS email,
       IFNULL(first_name,'-') AS first_name
FROM customer_entity
WHERE LOWER(email) LIKE '%qa%' OR LOWER(email) LIKE '%test%'
   OR LOWER(email) LIKE '%e2e%' OR first_name IN ('QA','E2E','TEST','Bharat')
LIMIT 15;
Q

echo "=== customers with active subscriptions (candidates to reuse) ==="
sql <<'Q'
SELECT s.customer_id, s.id AS subscription_id, s.status,
       IFNULL(c.email,'-') AS customer_email, IFNULL(c.phone,'-') AS customer_phone
FROM subscription_entity s
LEFT JOIN customer_entity c ON c.customer_id = s.customer_id
WHERE s.status = 'ACTIVE' ORDER BY s.customer_id LIMIT 15;
Q

echo "=== email configuration state (mail password placeholder?) ==="
docker exec bmj-api printenv MAIL_PASSWORD 2>/dev/null | sed 's/./x/g' | head -c 40; echo
echo -n "spring profile: "; docker exec bmj-api printenv SPRING_PROFILES_ACTIVE 2>/dev/null || echo "(default)"
