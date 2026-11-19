#!/bin/bash
# READ-ONLY validation, part 2: drift detectors, retry worker, migration scope.
cd /home/bmj/bmj || exit 1

sql() {
  docker exec -i bmj-sql sh -c 'exec mysql -u root -p"$MYSQL_ROOT_PASSWORD" bmj_db -t' 2>/dev/null
}

echo "################ 5. drift detectors (D1-D4 + duplicates) ################"
echo "---- D1: users with subscriptions but no link ----"
sql <<'SQL'
SELECT COUNT(*) AS d1_null_link_users_with_subs
FROM users u
WHERE (u.chargebee_customer_id IS NULL OR u.chargebee_customer_id='')
  AND EXISTS (SELECT 1 FROM subscription_entity s WHERE s.customer_id = CAST(u.id AS CHAR));
SQL

echo "---- D2: duplicate customer identities per phone (count of affected phones) ----"
sql <<'SQL'
SELECT COUNT(*) AS d2_duplicate_phones FROM (
  SELECT phone FROM customer_entity
  WHERE phone IS NOT NULL AND phone<>''
  GROUP BY phone HAVING COUNT(*) > 1
) t;
SQL

echo "---- D3: subscription rows no user can reach ----"
sql <<'SQL'
SELECT COUNT(*) AS d3_orphan_subs
FROM subscription_entity s
LEFT JOIN users u ON u.chargebee_customer_id = s.customer_id
WHERE u.id IS NULL;
SQL

echo "---- D4: subscription rows on a legacy numeric (twin) key ----"
sql <<'SQL'
SELECT COUNT(*) AS d4_twin_key_rows,
       SUM(s.status='ACTIVE') AS d4_active_rows
FROM subscription_entity s
JOIN users u ON s.customer_id = CAST(u.id AS CHAR)
WHERE u.chargebee_customer_id IS NOT NULL AND u.chargebee_customer_id<>''
  AND u.chargebee_customer_id <> s.customer_id;
SQL

echo "---- D4b: which users are affected, and by how many rows ----"
sql <<'SQL'
SELECT u.id, u.username, u.chargebee_customer_id AS correct_key,
       s.customer_id AS stored_key, COUNT(*) AS rows_
FROM subscription_entity s
JOIN users u ON s.customer_id = CAST(u.id AS CHAR)
WHERE u.chargebee_customer_id IS NOT NULL AND u.chargebee_customer_id<>''
  AND u.chargebee_customer_id <> s.customer_id
GROUP BY u.id, u.username, u.chargebee_customer_id, s.customer_id;
SQL

echo "################ 6. retry worker ################"
sql <<'SQL'
SELECT 'failed_total' AS metric, COUNT(*) AS n FROM webhook_events WHERE processing_status='FAILED'
UNION ALL
SELECT 'retry_queue(FAILED and retry_count<3)', COUNT(*) FROM webhook_events
  WHERE processing_status='FAILED' AND retry_count < 3
UNION ALL
SELECT 'dead_letter', COUNT(*) FROM webhook_events WHERE processing_status='DEAD_LETTER'
UNION ALL
SELECT 'stuck_processing(>15min)', COUNT(*) FROM webhook_events
  WHERE processing_status='PROCESSING' AND processed_at < (NOW() - INTERVAL 15 MINUTE)
UNION ALL
SELECT 'completed', COUNT(*) FROM webhook_events WHERE processing_status='COMPLETED';
SQL

echo "---- 6b. retry worker activity in the log ----"
docker logs bmj-api 2>&1 | grep -aiE "retry drain|dead-lettered|Replayed event" | tail -8 || echo "(no retry activity logged)"

echo "################ 7. remaining migration scope ################"
sql <<'SQL'
SELECT
  (SELECT COUNT(*) FROM users) AS users_total,
  (SELECT COUNT(*) FROM users WHERE chargebee_customer_id IS NULL OR chargebee_customer_id='') AS users_unlinked,
  (SELECT COUNT(*) FROM subscription_entity s JOIN users u ON s.customer_id=CAST(u.id AS CHAR)
     WHERE u.chargebee_customer_id IS NOT NULL AND u.chargebee_customer_id<>''
       AND u.chargebee_customer_id<>s.customer_id) AS rows_needing_rekey,
  (SELECT COUNT(DISTINCT u.id) FROM subscription_entity s JOIN users u ON s.customer_id=CAST(u.id AS CHAR)
     WHERE u.chargebee_customer_id IS NOT NULL AND u.chargebee_customer_id<>''
       AND u.chargebee_customer_id<>s.customer_id) AS users_needing_rekey,
  (SELECT COUNT(*) FROM subscription_entity) AS rows_total;
SQL

echo "################ current server time ################"
date -u
