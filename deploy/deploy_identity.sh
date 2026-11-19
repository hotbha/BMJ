#!/bin/bash
# Deployment identity snapshot for DEPLOYMENT_VERIFICATION_REPORT.md. Read-only.
cd /home/bmj/bmj || exit 1

echo "== running build =="
docker inspect --format 'image_id={{.Image}} restarts={{.RestartCount}} started={{.State.StartedAt}}' bmj-api
echo -n "image created       : "
docker inspect --format '{{.Created}}' bmj-backend:vps
echo -n "jar in container    : "
docker exec bmj-api sha256sum /app/app.jar | cut -d' ' -f1
echo -n "jar on host         : "
sha256sum app.jar | cut -d' ' -f1
echo -n "jar.prev on host    : "
sha256sum app.jar.prev | cut -d' ' -f1

echo "== stack =="
docker ps --format '{{.Names}}|{{.Status}}|{{.Ports}}'
echo -n "systemd             : "
systemctl is-enabled bmj-stack.service
echo -n "nginx               : "
systemctl is-active nginx

echo "== data =="
docker exec bmj-sql sh -c 'mysql -u root -p"$MYSQL_ROOT_PASSWORD" -N -e \
 "select concat(""customers="", (select count(*) from customer_entity), "" subs="", (select count(*) from subscription_entity), "" users="", (select count(*) from users), "" linked="", (select count(*) from users where chargebee_customer_id is not null and chargebee_customer_id<>""""));" bmj_db' 2>/dev/null
