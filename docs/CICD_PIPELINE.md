# CI/CD Pipeline — BookMyJuice

**Document Version:** 1.0  
**Last Updated:** 2026-05-08

---

## Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          GitHub Actions                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  [PR Opened]  ──►  Backend CI  ──►  Flutter CI  ──►  Merge         │
│                      ║               ║                              │
│                      ▼               ▼                              │
│                  Build Test      Analyze Test                       │
│                  Coverage Gate   Coverage Gate                      │
│                  Security Scan   Security Scan                      │
│                                                                     │
│  [Push to main] ──►  Backend CI  ──►  Flutter CI  ──►  Deploy      │
│                      ║               ║               ║             │
│                      ▼               ▼               ▼             │
│                  Pass All        Pass All        Staging/Prod      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Backend CI Pipeline

### `.github/workflows/backend-ci.yml`

```yaml
name: Backend CI

on:
  push:
    branches: [main, develop]
    paths:
      - 'bmjServer/**'
  pull_request:
    branches: [main, develop]
    paths:
      - 'bmjServer/**'

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: test
          MYSQL_DATABASE: bmj_test
          MYSQL_USER: test
          MYSQL_PASSWORD: test
        ports:
          - 3306:3306
        options: --health-cmd "mysqladmin ping" --health-interval 10s --health-timeout 5s --health-retries 5
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: --health-cmd "redis-cli ping" --health-interval 10s --health-timeout 5s --health-retries 5

    steps:
      - uses: actions/checkout@v4
      
      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: 17
          distribution: 'temurin'
          cache: maven
      
      - name: Build and run tests
        run: |
          cd bmjServer
          mvn clean verify -Pci
        env:
          DB_HOSTNAME: localhost
          DB_PORT: 3306
          DB_NAME: bmj_test
          DB_USERNAME: test
          DB_PASSWORD: test
          CHARGEBEE_SITE: bookmyjuice-test
          CHARGEBEE_API_KEY: ${{ secrets.CHARGEBEE_API_KEY }}
          JWT_SECRET: ${{ secrets.JWT_SECRET }}
          WEBHOOK_USERNAME: ${{ secrets.WEBHOOK_USERNAME }}
          WEBHOOK_PASSWORD: ${{ secrets.WEBHOOK_PASSWORD }}
          REDIS_HOST: localhost
          REDIS_PORT: 6379
      
      - name: Generate coverage report
        run: |
          cd bmjServer
          mvn jacoco:report
      
      - name: Check coverage threshold
        run: |
          cd bmjServer
          mvn jacoco:check
        # Fails if coverage < 80%
      
      - name: Dependency vulnerability check
        run: |
          cd bmjServer
          mvn org.owasp:dependency-check-maven:check
        continue-on-error: true  # Warning only, not blocking
      
      - name: Upload test artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: backend-test-reports
          path: |
            bmjServer/target/surefire-reports/
            bmjServer/target/site/jacoco/
      
      - name: Build JAR
        run: |
          cd bmjServer
          mvn package -DskipTests
      
      - name: Upload JAR artifact
        uses: actions/upload-artifact@v4
        with:
          name: backend-jar
          path: bmjServer/target/*.jar
```

### Quality Gates (Backend)

| Gate | Condition | Action |
|------|-----------|--------|
| Unit Tests | All must pass | ❌ Fail build |
| Integration Tests | All must pass | ❌ Fail build |
| Code Coverage | ≥ 80% line coverage | ❌ Fail build |
| Compilation | Must compile | ❌ Fail build |
| Checkstyle | No errors | ❌ Fail build |
| Dependency Check | No critical vulnerabilities | ⚠️ Warning |
| OWASP Scan | No critical issues | ⚠️ Warning |

---

## Flutter CI Pipeline

### `.github/workflows/flutter-ci.yml`

```yaml
name: Flutter CI

on:
  push:
    branches: [main, develop]
    paths:
      - 'lush/**'
  pull_request:
    branches: [main, develop]
    paths:
      - 'lush/**'

jobs:
  analyze-and-test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.x'
          channel: 'stable'
          cache: true
      
      - name: Install dependencies
        run: |
          cd lush
          flutter pub get
      
      - name: Analyze Dart code
        run: |
          cd lush
          flutter analyze --fatal-infos
      
      - name: Run unit tests
        run: |
          cd lush
          flutter test --coverage
      
      - name: Check coverage
        run: |
          cd lush
          # Use lcov for coverage check
          lcov --summary coverage/lcov.info | grep 'lines' | awk '{print $2}' | sed 's/%//' | xargs -I {} bash -c 'if [ {} -lt 80 ]; then echo "Coverage {}% < 80%"; exit 1; fi'
      
      - name: Upload coverage report
        uses: actions/upload-artifact@v4
        with:
          name: flutter-coverage
          path: lush/coverage/
      
      - name: Build APK (debug)
        run: |
          cd lush
          flutter build apk --debug
      
      - name: Upload APK artifact
        uses: actions/upload-artifact@v4
        with:
          name: flutter-apk
          path: lush/build/app/outputs/flutter-apk/*.apk
```

### Quality Gates (Flutter)

| Gate | Condition | Action |
|------|-----------|--------|
| `flutter analyze` | No errors | ❌ Fail build |
| Unit Tests | All must pass | ❌ Fail build |
| Widget Tests | All must pass | ❌ Fail build |
| Code Coverage | ≥ 80% | ❌ Fail build |
| Compilation | Must compile | ❌ Fail build |

---

## Environment Strategy

| Environment | Deploy Method | Trigger |
|-------------|--------------|---------|
| `local` | `docker-compose up` | Manual |
| `ci` | Ephemeral containers | PR push |
| `staging` | Docker deploy to staging server | Merge to develop |
| `production` | Docker deploy with approval | Merge to main + manual approval |

### Environment-Specific Properties

```
bmjServer/src/main/resources/
├── application.yml              # Shared (common)
├── application-dev.yml          # Local development
├── application-staging.yml      # Staging environment
└── application-production.yml   # Production environment
```

### Secrets Management

All secrets are stored as GitHub Actions secrets:
- `CHARGEBEE_API_KEY` — Chargebee API key
- `JWT_SECRET` — JWT signing secret
- `WEBHOOK_USERNAME` — Webhook basic auth username
- `WEBHOOK_PASSWORD` — Webhook basic auth password
- `DB_PASSWORD` — Database password
- `MAIL_USERNAME` — SMTP username
- `MAIL_PASSWORD` — SMTP password

No secrets are hardcoded in code or committed to the repository.

---

## Dockerfile (Backend Production)

```dockerfile
FROM eclipse-temurin:17-jre-alpine AS build
WORKDIR /app
COPY target/*.jar app.jar
RUN java -Djarmode=layertools -jar app.jar extract --destination extracted

FROM eclipse-temurin:17-jre-alpine
RUN addgroup -S app && adduser -S app -G app
USER app
WORKDIR /app
COPY --from=build /app/extracted/dependencies/ ./
COPY --from=build /app/extracted/spring-boot-loader/ ./
COPY --from=build /app/extracted/snapshot-dependencies/ ./
COPY --from=build /app/extracted/application/ ./
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

---

## Pipeline Maintenance

| Task | Frequency | Owner |
|------|-----------|-------|
| Review CI times | Weekly | DevOps |
| Update dependency versions | Monthly | Engineering |
| Audit secrets rotation | Quarterly | Security |
| Pipeline failure review | As needed | On-call |
| Coverage report review | Sprint review | QA |

---

**Document Maintained By:** DevOps Team  
**Last Review:** 2026-05-08  
**Next Review:** 2026-06-08
