#!/bin/bash
# Add the two env vars the application requires but the first .env revision missed.
# JWT_SECRET is generated ON the server and never leaves it.
# Idempotent: existing keys are left untouched (so the DB password is not rotated).
set -euo pipefail
cd /home/bmj/bmj

grep -q '^JWT_SECRET=' .env || printf 'JWT_SECRET=%s\n' "$(openssl rand -hex 32)" >> .env
grep -q '^MAIL_PASSWORD=' .env || printf 'MAIL_PASSWORD=%s\n' 'not-configured-email-disabled' >> .env

echo "--- env keys present ---"
cut -d= -f1 .env

echo "--- recreating api container ---"
docker compose --env-file .env -f docker-compose.prod.yml up -d bmj-api 2>&1 | tail -4
