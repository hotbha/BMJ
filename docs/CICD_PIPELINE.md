# BookMyJuice CI/CD Pipeline

> **Last Updated:** 2026-05-17

## Overview

This document describes the CI/CD pipeline configuration for BookMyJuice.

## Secrets Strategy

### Local Development
- All secrets are stored in a single `.env` file at the project root.
- Copy `.env.example` to `.env` and fill in values.
- `.env` is gitignored — never committed.
- Docker Compose loads `../.env` via `env_file` directive.

### GitHub Actions Secrets Required

| Secret Name | Description | Required For |
|---|---|---|
| `SENTRY_DSN_BACKEND` | Sentry DSN for Spring Boot backend | Backend CI, Deploy |
| `SENTRY_DSN_FLUTTER` | Sentry DSN for Flutter | Flutter CI |
| `SENTRY_AUTH_TOKEN` | Sentry auth token (from Sentry org) | Deploy (release creation) |
| `SENTRY_ORG` | Sentry organization slug | Deploy (release creation) |
| `VPS_HOST` | VPS IP address | Deploy |
| `VPS_USER` | SSH username for VPS | Deploy |
| `VPS_SSH_KEY` | SSH private key for VPS | Deploy |
| `VPS_PORT` | SSH port (default 22) | Deploy (optional) |
| `CHARGEBEE_API_KEY` | Chargebee API key | Backend CI |
| `JWT_SECRET` | JWT signing secret | All |

## Backend CI

**File:** `.github/workflows/backend-ci.yml`

Triggered on push/PR to `main` or `develop` with changes under `bmjServer/`.

| Step | Action | Gate |
|------|--------|------|
| Checkout | `actions/checkout@v4` | — |
| Setup JDK 17 | `actions/setup-java@v4` (temurin) | — |
| Build & Test | `mvn clean verify -Pci` | All tests must pass |
| Coverage | JaCoCo report + check | ≥90% line coverage |
| Security | OWASP dependency check | Continue on warning |
| Build JAR | `mvn package -DskipTests` | — |
| Upload | Test reports + JAR artifact | — |

**Services:** MySQL 8.0 + Redis 7 (service containers)
**Sentry:** DSN injected via `SENTRY_DSN_BACKEND` env var (empty in CI, no errors sent)

## Flutter CI

**File:** `.github/workflows/flutter-ci.yml`

Triggered on push/PR to `main` or `develop` with changes under `lush/`.

| Step | Action | Gate |
|------|--------|------|
| Checkout | `actions/checkout@v4` | — |
| Setup Flutter | `subosito/flutter-action@v2` (3.x stable) | — |
| Install deps | `flutter pub get` | — |
| Analyze | `flutter analyze --fatal-infos` | Zero errors |
| Test | `flutter test --coverage` | All tests pass |
| Coverage gate | `lcov --summary` check | ≥90% line coverage |
| Build APK | `flutter build apk --debug` | — |
| Upload | Coverage report + APK artifact | — |

**Sentry:** DSN injected via `--dart-define=SENTRY_DSN_FLUTTER` (empty in CI, no errors sent)

## Deploy to VPS

**File:** `.github/workflows/deploy-vps.yml`

Manual trigger via `workflow_dispatch` with environment input (`staging` or `production`).

| Step | Action |
|------|--------|
| Checkout | `actions/checkout@v4` |
| Build JAR | `mvn package -DskipTests` (with Sentry DSN) |
| Deploy via SCP | `appleboy/scp-action` → copies JAR to VPS |
| Restart service | `appleboy/ssh-action` → systemd restart + health check |
| Rollback | Automatic if health check fails (keeps last 5 backups) |
| Sentry release | `getsentry/action-release` → creates Sentry release |

**GitHub Environments:** `staging` and `production` — both require manual approval.

## VPS Architecture

```
                    ┌─────────────┐
                    │   Nginx     │ (port 80)
                    │  Reverse    │
                    │  Proxy      │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Backend    │ (port 8080)
                    │  Spring     │
                    │  Boot JAR   │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
       ┌──────▼─────┐ ┌───▼────┐ ┌────▼─────┐
       │   MySQL    │ │ Redis  │ │  Sentry  │
       │   8.0      │ │   7    │ │  SDK     │
       └────────────┘ └────────┘ └──────────┘
```

All services (MySQL, Redis, Backend) run on localhost — no public ports exposed.  
Nginx proxies external traffic to the backend on 127.0.0.1:8080.  
UFW firewall allows only SSH (22), HTTP (80), and HTTPS (443).

## VPS Provisioning

**Script:** `ops/provision-vps.sh`

One-shot setup script for a fresh Ubuntu VPS. Installs and configures:

- Nginx reverse proxy
- MySQL 8.0 (localhost only)
- Redis 7 (localhost only)
- JDK 17 (Temurin)
- bmj-backend systemd service
- UFW firewall (SSH, HTTP, HTTPS)

Usage:
```bash
chmod +x ops/provision-vps.sh
sudo ./ops/provision-vps.sh
```

## Sentry Integration

### Backend (Spring Boot)
- **Config file:** `bmjServer/src/main/resources/sentry.properties`
- **DSN:** Loaded from env var `SENTRY_DSN_BACKEND`
- **Dependencies:** `sentry-spring-boot-starter` + `sentry-logback` (v7.14.0)
- **Sample rate:** 1.0 errors, 0.1 traces

### Frontend (Flutter)
- **Init location:** `lush/lib/main.dart` — `_initializeApp()` via `SentryFlutter.init()`
- **DSN:** Passed via `--dart-define=SENTRY_DSN_FLUTTER` at build time
- **Package:** `sentry_flutter: ^8.10.0`
- **Error handlers:** Both `FlutterError.onError` and `PlatformDispatcher.instance.onError` capture to Sentry

## Environment Files

| Environment | Property File | Source |
|---|---|---|
| Local Dev | `.env` (root) + `docker-compose.yml` | .env + docker-compose |
| CI Backend | `backend-ci.yml` env block | GitHub Secrets |
| CI Flutter | `flutter-ci.yml` env block | GitHub Secrets |
| VPS Production | `~bmj/bmj/.env` | Created by provision script |

## Dependency Updates

- Maven dependencies: `mvn versions:display-dependency-updates`
- Flutter dependencies: `flutter pub outdated`
- Automate via Dependabot or Renovate if configured.
