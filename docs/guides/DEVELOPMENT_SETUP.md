# Development Setup Guide - BookMyJuice

**Version:** 2.0
**Last Updated:** 2026-05-13

---

## Prerequisites

Java 17+, Maven 3.8+, MySQL 8.0+, Flutter 3.10+, Git 2.40+

---

## 1. Clone

```
git clone https://github.com/hotbha/BMJ.git
cd BMJ
```

---

## 2. Environment (.env)

Create `bmjServer/.env` (never committed):

```
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=bmj
MYSQL_USER=root
MYSQL_PASSWORD=yourpassword
CHARGEBEE_SITE=your-site
CHARGEBEE_API_KEY=your-api-key
JWT_SECRET=your-jwt-secret
SERVER_PORT=8080
```

---

## 3. MySQL

```
CREATE DATABASE IF NOT EXISTS bmj CHARACTER SET utf8mb4;
```

Migrations auto-run via Flyway. Manual: `cd bmjServer && mvn flyway:migrate`

---

## 4. Run Backend

```
cd bmjServer
mvn spring-boot:run -Dspring.profiles.active=dev
```

Verify: `curl http://localhost:8080/api/health`

---

## 5. Run Flutter

```
cd bmjApp
flutter pub get
flutter run
```

Set API URL in lib/service/bmj_service.dart.

---

## 6. Tests

Backend: `cd bmjServer && mvn test`
Flutter: `cd bmjApp && flutter test`

---

## 7. Build

APK: `cd bmjApp && flutter build apk --release`
JAR: `cd bmjServer && mvn clean package -DskipTests`

---

## 8. Git Workflow

Branches: feature/*, fix/*, docs/*, chore/*
Commits: Conventional Commits
PRs: branch from main, squash-merge

---

## 9. Project Structure

```
BMJ/
├── bmjServer/   # Spring Boot
├── bmjApp/      # Flutter
├── docs/        # BRD, guides, strategies
├── .github/     # CI, conventions
├── CHANGELOG.md
└── README.md
```

---

## 10. Common Issues

| Issue | Fix |
|-------|-----|
| MySQL refused | `net start MySQL80` |
| Port 8080 in use | `netstat -ano | findstr :8080` + taskkill |
| Flutter fails | `flutter clean && flutter pub get` |
| Flyway error | `mvn flyway:repair` or `flyway:clean flyway:migrate` |

---

**Maintained By:** Engineering Team
