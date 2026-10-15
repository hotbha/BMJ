# BookMyJuice (BMJ) Quickstart Guide

Get the enterprise-grade juice subscription platform running locally in 5 minutes.

## Prerequisites

- **Docker Desktop** (v20.10+) with Compose
- **Flutter SDK** (v3.19+)
- **Java 17 OpenJDK** & **Apache Maven** (v3.9+)
- **Chargebee Test Account** credentials in `.env`

---

## 5-Minute Local Setup

### 1. Environment Configuration
Copy the example `.env` file from the root directory:
```bash
cp .env.example .env
```
Ensure `CHARGEBEE_SITE` and `CHARGEBEE_API_KEY` are set to your Chargebee test account credentials.

### 2. Launch Backend Infrastructure (Docker)
From the project root directory (`x:\BMJ`):
```bash
docker-compose --env-file .env up -d --build
```
This boots up:
- **MySQL 8.0** database container (`bmj-mysql` on port `3307`)
- **Redis 7** cache container (`bmj-redis` on port `6379`)
- **Spring Boot Backend** container (`bmj-backend` on port `8080`)
- **phpMyAdmin** database UI (`bmj-phpmyadmin` on port `8081`)

Verify container health:
```bash
docker-compose ps
```

### 3. Launch Mobile Application (Flutter)
Navigate to the mobile app directory and run:
```bash
cd lush
flutter pub get
flutter run
```

---

## Common Errors & Quick Fixes

### 1. Maven Compilation Errors
- **Symptom**: Unresolved symbol or method missing on Chargebee models.
- **Fix**: Verify Chargebee SDK v3.x getters (e.g. `getItem()`, `getItemPrice()`). Run:
  ```bash
  cd bmjServer
  mvn clean compile
  ```

### 2. Port Conflicts (8080, 3307, 6379)
- **Symptom**: `Bind for 0.0.0.0:8080 failed: port is already allocated`.
- **Fix**: Check running processes on ports `8080`, `3307`, `6379`:
  ```bash
  netstat -ano | findstr :8080
  taskkill /PID <PID> /F
  ```

### 3. Backend Startup Database Connection Timeout
- **Symptom**: Flyway migration failed or MySQL connection refused.
- **Fix**: Ensure `bmj-mysql` container is reported healthy (`healthcheck: mysqladmin ping`). Restart stack:
  ```bash
  docker-compose restart mysql backend
  ```
