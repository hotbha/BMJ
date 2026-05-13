# BookMyJuice CI/CD Pipeline

> **Last Updated:** 2026-05-09

## Overview

This document describes the CI/CD pipeline configuration for BookMyJuice.

## Secrets Strategy

### Local Development
- All secrets are stored in a single `.env` file at the project root.
- Copy `.env.example` to `.env` and fill in values.
- `.env` is gitignored — never committed.
- Docker Compose loads `../.env` via `env_file` directive.

### CI/CD (GitHub Actions)
- Secrets are configured as [GitHub Actions repository secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets).
- The CI pipelines reference them via `${{ secrets.SECRET_NAME }}`.
- No `.env` file is used in CI — secrets are injected directly.

## Backend CI

**File:** `.github/workflows/backend-ci.yml`

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

## Flutter CI

**File:** `.github/workflows/flutter-ci.yml`

| Step | Action | Gate |
|------|--------|------|
| Checkout | `actions/checkout@v4` | — |
| Setup Flutter | `subosito/flutter-action@v2` (3.x stable) | — |
| Install deps | `flutter pub get` | — |
| Analyze | `flutter analyze --fatal-infos` | Zero errors |
| Test | `flutter test --coverage` | All tests pass |
| Coverage gate | `lcov —summary` check | ≥90% line coverage |
| Build APK | `flutter build apk —debug` | — |
| Upload | Coverage report + APK artifact | — |

## Environment Files

| Environment | Property File | Source |
|-------------|--------------|--------|
| Local Dev | `.env` (root) + `docker-compose.yml` | .env + docker-compose |
| CI Backend | `backend-ci.yml` env block | GitHub Secrets |
| CI Flutter | `flutter-ci.yml` env block | GitHub Secrets |

## Dependency Updates

- Maven dependencies: `mvn versions:display-dependency-updates`
- Flutter dependencies: `flutter pub outdated`
- Automate via Dependabot or Renovate if configured.
