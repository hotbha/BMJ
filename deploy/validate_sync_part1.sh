#!/bin/bash
# READ-ONLY validation of the live sync system. No writes, no DDL, no migration.
cd /home/bmj/bmj || exit 1

sql() {
  docker exec -i bmj-sql sh -c 'exec mysql -u root -p"$MYSQL_ROOT_PASSWORD" bmj_db -t' 2>/dev/null
}

echo "################ 1. webhook_events by status ################"
sql <<'SQL'
SELECT IFNULL(processing_status,'(null)') AS status, COUNT(*) AS n
FROM webhook_events GROUP BY processing_status ORDER BY n DESC;
SQL

echo "################ 1b. webhook_events total + window ################"
sql <<'SQL'
SELECT COUNT(*) AS total_events,
       MIN(processed_at) AS oldest,
       MAX(processed_at) AS newest
FROM webhook_events;
SQL

echo "################ 2+3. receipts by event type ################"
sql <<'SQL'
SELECT event_type,
       COUNT(*) AS n,
       SUM(processing_status='COMPLETED') AS completed,
       SUM(processing_status='FAILED') AS failed,
       SUM(processing_status='PROCESSING') AS processing,
       SUM(processing_status='DEAD_LETTER') AS dead,
       MAX(processed_at) AS latest
FROM webhook_events
GROUP BY event_type
ORDER BY latest DESC;
SQL

echo "################ 2. customer event receipts (latest 10) ################"
sql <<'SQL'
SELECT event_id, event_type, processing_status, retry_count,
       LEFT(IFNULL(last_error,''),60) AS last_error, processed_at
FROM webhook_events
WHERE event_type IN ('customer_created','customer_changed','customer_deleted','customer_entitlements_updated')
ORDER BY processed_at DESC LIMIT 10;
SQL

echo "################ 3. subscription event receipts (latest 12) ################"
sql <<'SQL'
SELECT event_id, event_type, processing_status, retry_count,
       LEFT(IFNULL(last_error,''),60) AS last_error, processed_at
FROM webhook_events
WHERE event_type LIKE 'subscription%'
ORDER BY processed_at DESC LIMIT 12;
SQL

echo "################ 3b. coverage of the five named subscription types ################"
sql <<'SQL'
SELECT event_type, COUNT(*) AS n
FROM webhook_events
WHERE event_type IN ('subscription_created','subscription_changed','subscription_activated',
                     'subscription_started','subscription_deleted')
GROUP BY event_type ORDER BY event_type;
SQL

echo "################ 4. identity coverage ################"
sql <<'SQL'
SELECT COUNT(*) AS users_total,
       SUM(chargebee_customer_id IS NOT NULL AND chargebee_customer_id<>'') AS linked,
       SUM(chargebee_customer_id IS NULL OR chargebee_customer_id='') AS unlinked
FROM users;
SQL

echo "---- 4b. dangling links (link points at a missing customer row) ----"
sql <<'SQL'
SELECT COUNT(*) AS dangling_links
FROM users u LEFT JOIN customer_entity c ON c.customer_id = u.chargebee_customer_id
WHERE u.chargebee_customer_id IS NOT NULL AND u.chargebee_customer_id<>''
  AND c.customer_id IS NULL;
SQL

echo "---- 4c. ambiguous: several users sharing one customer id ----"
sql <<'SQL'
SELECT chargebee_customer_id, COUNT(*) AS users
FROM users
WHERE chargebee_customer_id IS NOT NULL AND chargebee_customer_id<>''
GROUP BY chargebee_customer_id HAVING COUNT(*) > 1;
SQL

echo "---- 4d. conflicts: duplicate customer rows per phone ----"
sql <<'SQL'
SELECT phone, COUNT(*) AS rows_, GROUP_CONCAT(customer_id ORDER BY customer_id) AS ids
FROM customer_entity
WHERE phone IS NOT NULL AND phone<>''
GROUP BY phone HAVING COUNT(*) > 1 ORDER BY rows_ DESC LIMIT 10;
SQL

echo "---- 4e. per-user identity state ----"
sql <<'SQL'
SELECT u.id, u.username,
       IFNULL(u.chargebee_customer_id,'(none)') AS cb_id,
       (SELECT COUNT(*) FROM subscription_entity s WHERE s.customer_id = u.chargebee_customer_id) AS reachable_subs,
       (SELECT COUNT(*) FROM subscription_entity s WHERE s.customer_id = CAST(u.id AS CHAR)) AS twin_subs
FROM users u ORDER BY u.id;
SQL
