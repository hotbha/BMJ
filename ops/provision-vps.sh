#!/usr/bin/env bash
# ============================================================
# BookMyJuice — VPS Provisioning Script
# ============================================================
# One-shot setup for a fresh Ubuntu 22.04 / 24.04 VPS.
#
# Usage:
#   chmod +x ops/provision-vps.sh
#   sudo ./ops/provision-vps.sh
#
# What it installs / configures:
#   - System updates + common tools (curl, wget, git, ufw)
#   - Nginx as reverse proxy (with optional Let's Encrypt)
#   - MySQL 8.0
#   - Redis 7
#   - JDK 17 (Temurin)
#   - bmj-backend systemd service
#   - UFW firewall rules
# ============================================================
set -euo pipefail

# ─── Color output ───────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info()  { echo -e "${GREEN}[INFO]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; }

# ─── Configuration ───────────────────────────────────────────────
# Update these values to match your environment
DOMAIN="${DOMAIN:-bookmyjuice.co.in}"
APP_USER="${APP_USER:-bmj}"
APP_DIR="/home/${APP_USER}/bmj"
DB_NAME="${DB_NAME:-bmj}"
DB_USER="${DB_USER:-bmj}"
DB_PASS="${DB_PASS:-CHANGE_ME_DB_PASSWORD}"
JWT_SECRET="${JWT_SECRET:-CHANGE_ME_JWT_SECRET}"

# ─── Root check ─────────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
  error "This script must be run as root (use sudo)."
  exit 1
fi

# ══════════════════════════════════════════════════════════════════
# Phase 1: System Updates & Base Packages
# ══════════════════════════════════════════════════════════════════
info "Phase 1: System updates and base packages..."
apt-get update -qq
apt-get upgrade -y -qq
apt-get install -y -qq \
  curl wget git ufw gnupg ca-certificates lsb-release \
  software-properties-common

# ══════════════════════════════════════════════════════════════════
# Phase 2: Nginx Reverse Proxy
# ══════════════════════════════════════════════════════════════════
info "Phase 2: Installing Nginx..."
apt-get install -y -qq nginx

# Create Nginx config
cat > /etc/nginx/sites-available/bmj-backend << 'NGINX_CONF'
server {
    listen 80;
    server_name _;

    # Client max body size for order data
    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Health check endpoint - bypass auth
    location /api/health {
        proxy_pass http://127.0.0.1:8080/api/health;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        access_log off;
    }
}
NGINX_CONF

# Enable site
ln -sf /etc/nginx/sites-available/bmj-backend /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and reload
nginx -t && systemctl reload nginx
info "Nginx configured and running."

# ══════════════════════════════════════════════════════════════════
# Phase 3: MySQL 8.0
# ══════════════════════════════════════════════════════════════════
info "Phase 3: Installing MySQL 8.0..."
apt-get install -y -qq mysql-server

# Secure MySQL and create database/user
mysql <<SQL
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${DB_PASS}';
FLUSH PRIVILEGES;
CREATE DATABASE IF NOT EXISTS ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
SQL

# Only listen on localhost for security
sed -i 's/^bind-address\s*=.*/bind-address = 127.0.0.1/' /etc/mysql/mysql.conf.d/mysqld.cnf || true
systemctl restart mysql
info "MySQL configured with database '${DB_NAME}' and user '${DB_USER}'."

# ══════════════════════════════════════════════════════════════════
# Phase 4: Redis 7
# ══════════════════════════════════════════════════════════════════
info "Phase 4: Installing Redis 7..."
apt-get install -y -qq redis-server

# Bind to localhost only
sed -i 's/^bind 127.0.0.1/bind 127.0.0.1/' /etc/redis/redis.conf || true
sed -i 's/^protected-mode yes/protected-mode yes/' /etc/redis/redis.conf || true
systemctl enable redis-server
systemctl restart redis-server
info "Redis installed and running."

# ══════════════════════════════════════════════════════════════════
# Phase 5: JDK 17 (Temurin)
# ══════════════════════════════════════════════════════════════════
info "Phase 5: Installing JDK 17 (Temurin)..."
# Use Adoptium / Eclipse Temurin repository
wget -qO - https://packages.adoptium.net/artifactory/api/gpg/key/public | gpg --dearmor -o /usr/share/keyrings/adoptium.gpg
echo "deb [signed-by=/usr/share/keyrings/adoptium.gpg] https://packages.adoptium.net/artifactory/deb $(lsb_release -cs) main" \
  | tee /etc/apt/sources.list.d/adoptium.list > /dev/null
apt-get update -qq
apt-get install -y -qq temurin-17-jdk

# Verify
java -version
info "JDK 17 installed."

# ══════════════════════════════════════════════════════════════════
# Phase 6: bmj-backend systemd Service
# ══════════════════════════════════════════════════════════════════
info "Phase 6: Creating bmj-backend systemd service..."

# Create application user (non-interactive, no password, home dir)
id -u ${APP_USER} &>/dev/null || useradd -m -s /bin/bash -d /home/${APP_USER} ${APP_USER}
mkdir -p ${APP_DIR}
mkdir -p ${APP_DIR}/logs
mkdir -p ${APP_DIR}/backups

# Create systemd service file
cat > /etc/systemd/system/bmj-backend.service << SERVICE
[Unit]
Description=BookMyJuice Backend Spring Boot Application
After=network.target mysql.service redis-server.service
Wants=mysql.service redis-server.service

[Service]
Type=simple
User=${APP_USER}
Group=${APP_USER}
WorkingDirectory=${APP_DIR}

# Point to the current JAR symlink managed by deploy workflow
ExecStart=/usr/bin/java -jar ${APP_DIR}/current.jar

# Environment variables loaded from .env file
EnvironmentFile=${APP_DIR}/.env

# Restart behavior
Restart=on-failure
RestartSec=10

# Logging
StandardOutput=append:${APP_DIR}/logs/bmj-backend.log
StandardError=append:${APP_DIR}/logs/bmj-backend-error.log

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full

[Install]
WantedBy=multi-user.target
SERVICE

# Create a template .env file for the app user
cat > ${APP_DIR}/.env << ENVFILE
# ============================================================
# BookMyJuice Backend — Environment Variables
# ============================================================
DB_USERNAME=${DB_USER}
DB_PASSWORD=${DB_PASS}
DB_HOSTNAME=localhost
DB_PORT=3306
DB_NAME=${DB_NAME}

ADMIN_USER=admin
ADMIN_PASSWORD=CHANGE_ME_ADMIN_PASSWORD

CHARGEBEE_SITE=test
CHARGEBEE_API_KEY=CHANGE_ME_CHARGEBEE_KEY

JWT_SECRET=${JWT_SECRET}
JWT_EXPIRATION_MS=86400000

WEBHOOK_USERNAME=CHANGE_ME_WEBHOOK_USER
WEBHOOK_PASSWORD=CHANGE_ME_WEBHOOK_PASS

MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=support@gmail.co.in
MAIL_PASSWORD=CHANGE_ME_SMTP_PASS
MAIL_FROM=support@bookmyjuice.co.in

REDIS_HOST=localhost
REDIS_PORT=6379

SENTRY_DSN_BACKEND=
SENTRY_ENVIRONMENT=production
ENVFILE

chown -R ${APP_USER}:${APP_USER} ${APP_DIR}
chmod 600 ${APP_DIR}/.env

# Enable and start service (service will start once JAR is deployed)
systemctl daemon-reload
systemctl enable bmj-backend.service
info "bmj-backend service created (will start after first JAR deployment)."

# ══════════════════════════════════════════════════════════════════
# Phase 7: UFW Firewall
# ══════════════════════════════════════════════════════════════════
info "Phase 7: Configuring UFW firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing

# SSH
ufw allow ssh

# HTTP / HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Application port (internal - not needed if Nginx is on same host)
# ufw allow 8080/tcp

ufw --force enable
info "UFW firewall configured (SSH, HTTP, HTTPS allowed)."

# ══════════════════════════════════════════════════════════════════
# Phase 8: Optional — Let's Encrypt SSL
# ══════════════════════════════════════════════════════════════════
# Uncomment and configure if you have a domain pointed to this VPS:
#
# info "Phase 8: Setting up Let's Encrypt SSL..."
# apt-get install -y -qq certbot python3-certbot-nginx
# certbot --nginx -d ${DOMAIN} --non-interactive --agree-tos -m admin@${DOMAIN}
#
# Then update /etc/nginx/sites-available/bmj-backend to include SSL.
# ============================================================

# ══════════════════════════════════════════════════════════════════
# Summary
# ══════════════════════════════════════════════════════════════════
echo ""
info "══════════════════════════════════════════════════════════"
info "  VPS provisioning complete!"
info "══════════════════════════════════════════════════════════"
info ""
info "  Next steps:"
info "  1. Update ${APP_DIR}/.env with your real secrets"
info "  2. Copy the JAR file to ${APP_DIR}/current.jar"
info "  3. Run: sudo systemctl start bmj-backend"
info "  4. Configure GitHub Secrets for deployment:"
info "     - VPS_HOST, VPS_USER, VPS_SSH_KEY"
info "     - SENTRY_DSN_BACKEND, SENTRY_DSN_FLUTTER"
info "     - SENTRY_AUTH_TOKEN, SENTRY_ORG"
info "  5. Run CI/CD workflow from GitHub Actions"
info ""
info "  Services installed:"
info "    - Nginx (port 80)"
info "    - MySQL 8.0 (port 3306, localhost only)"
info "    - Redis 7 (port 6379, localhost only)"
info "    - JDK 17 (Temurin)"
info "    - bmj-backend systemd service"
info "    - UFW firewall (SSH, HTTP, HTTPS)"
info "══════════════════════════════════════════════════════════"
