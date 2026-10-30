# BookMyJuice - Development Tools & Configuration Guide

**Document Version:** 1.0  
**Date:** March 27, 2026  
**Purpose:** Professional SDLC setup with proper testing infrastructure  

---

## Table of Contents

1. [Required VS Code Extensions](#1-required-vs-code-extensions)
2. [MCP Servers Configuration](#2-mcp-servers-configuration)
3. [Flutter/Dart Plugins](#3-flutterdart-plugins)
4. [Backend Development Tools](#4-backend-development-tools)
5. [Testing Frameworks Setup](#5-testing-frameworks-setup)
6. [CI/CD Configuration](#6-cicd-configuration)
7. [Database Tools](#7-database-tools)
8. [API Development Tools](#8-api-development-tools)
9. [Code Quality Tools](#9-code-quality-tools)
10. [Development Environment Checklist](#10-development-environment-checklist)
11. [Local Backend on the LAN (physical device testing)](#11-local-backend-on-the-lan-physical-device-testing)

---

## 1. Required VS Code Extensions

### 1.1 Core Extensions (Mandatory)

```json
{
  "recommendations": [
    // Flutter & Dart
    "Dart-Code.dart",                    // Dart language support
    "Dart-Code.flutter",                 // Flutter development
    
    // Java & Spring Boot
    "vscjava.vscode-java-pack",          // Java extension pack
    "vmware.vscode-spring-boot",         // Spring Boot tools
    
    // Testing
    "hbenl.vscode-test-explorer",        // Test explorer UI
    "hbenl.vscode-java-test",            // Java test runner
    "FlutterGen.flutter-gen",            // Flutter test generator
    
    // Code Quality
    "esbenp.prettier-vscode",            // Code formatter
    "streetsidesoftware.code-spell-checker", // Spell checker
    
    // Git & Version Control
    "GitHub.vscode-pull-request-github", // GitHub PR integration
    "GitLab.gitlab-workflow",            // GitLab integration (if needed)
    
    // Database
    "mtxr.sqltools",                     // Database client
    "mtxr.sqltools-driver-mysql",        // MySQL driver
    
    // API Development
    "humao.rest-client",                 // REST client for testing
    "42Crunch.vscode-openapi",           // OpenAPI/Swagger support
    
    // Docker & DevOps
    "ms-azuretools.vscode-docker",       // Docker tools
    "ms-kubernetes-tools.vscode-kubernetes-tools", // Kubernetes
    
    // Productivity
    "shd101wyy.markdown-preview-enhanced", // Markdown preview
    "yzhang.markdown-all-in-one",        // Markdown utilities
    "bierner.markdown-mermaid",          // Mermaid diagrams in markdown
  ]
}
```

### 1.2 Extension Installation Command

```powershell
# Install all extensions via command line
code --install-extension Dart-Code.dart
code --install-extension Dart-Code.flutter
code --install-extension vscjava.vscode-java-pack
code --install-extension vmware.vscode-spring-boot
code --install-extension hbenl.vscode-test-explorer
code --install-extension hbenl.vscode-java-test
code --install-extension esbenp.prettier-vscode
code --install-extension streetsidesoftware.code-spell-checker
code --install-extension GitHub.vscode-pull-request-github
code --install-extension mtxr.sqltools
code --install-extension mtxr.sqltools-driver-mysql
code --install-extension humao.rest-client
code --install-extension 42Crunch.vscode-openapi
code --install-extension ms-azuretools.vscode-docker
code --install-extension bierner.markdown-mermaid
```

---

## 2. MCP Servers Configuration

### 2.1 What is MCP?

Model Context Protocol (MCP) allows AI assistants to interact with external tools and services. For professional development, we recommend:

### 2.2 Recommended MCP Servers

#### GitHub MCP
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${input:githubToken}"
      }
    }
  }
}
```
**Purpose:** Repository management, PR creation, issue tracking  
**Setup:**  
1. Generate GitHub Personal Access Token (classic)
2. Scopes: repo, workflow, read:org
3. Add to VS Code settings

#### PostgreSQL MCP (for database queries)
```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://bmj:PASS@123@localhost:3306/bmj_db"]
    }
  }
}
```

#### Filesystem MCP (for file operations)
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "x:/BMJ"]
    }
  }
}
```

### 2.3 VS Code MCP Configuration

Add to `.vscode/mcp.json`:

```json
{
  "inputs": [
    {
      "id": "githubToken",
      "type": "promptString",
      "description": "GitHub Personal Access Token"
    }
  ],
  "mcp": {
    "servers": {
      "github": {
        "type": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {
          "GITHUB_PERSONAL_ACCESS_TOKEN": "${input:githubToken}"
        }
      }
    }
  }
}
```

---

## 3. Flutter/Dart Plugins

### 3.1 pubspec.yaml - Development Dependencies

```yaml
dev_dependencies:
  flutter_test:
    sdk: flutter
  
  # Unit Testing
  mockito: ^5.4.4           # Mocking for unit tests
  mocktail: ^1.0.3          # Mock library for Dart
  bloc_test: ^9.1.7         # Testing utilities for BLoC
  
  # Integration Testing
  integration_test:
    sdk: flutter
  patrol: ^3.7.0            # E2E testing framework
  
  # Code Quality
  flutter_lints: ^4.0.0     # Linting rules
  very_good_analysis: ^6.0.0 # Strict lint rules (optional)
  
  # Code Generation
  build_runner: ^2.4.9      # Build system
  mockito: ^5.4.4           # Mock code generation
  
  # Coverage
  lcov_digraph: ^1.0.0      # Coverage visualization
  
  # Test Organization
  group: ^4.0.0             # Test grouping
  test: ^1.25.7             # Dart test framework
```

### 3.2 Test Directory Structure

```
lush/
├── test/
│   ├── unit/
│   │   ├── bloc/
│   │   │   ├── auth_bloc_test.dart
│   │   │   ├── cart_bloc_test.dart
│   │   │   └── products_bloc_test.dart
│   │   ├── models/
│   │   │   ├── product_test.dart
│   │   │   └── cart_item_test.dart
│   │   ├── repositories/
│   │   │   ├── cart_repository_test.dart
│   │   │   └── user_repository_test.dart
│   │   └── services/
│   │       ├── api_service_test.dart
│   │       └── auth_service_test.dart
│   └── widget/
│       ├── screens/
│       │   ├── login_screen_test.dart
│       │   ├── cart_screen_test.dart
│       │   └── product_list_screen_test.dart
│       └── widgets/
│           ├── product_card_test.dart
│           └── cart_item_tile_test.dart
├── integration_test/
│   ├── app_smoke_test.dart
│   ├── auth_flow_test.dart
│   ├── cart_flow_test.dart
│   ├── checkout_flow_test.dart
│   └── subscription_flow_test.dart
└── test_fixtures/
    ├── mock_products.json
    ├── mock_user.json
    └── test_constants.dart
```

---

## 4. Backend Development Tools

### 4.1 pom.xml - Test Dependencies

```xml
<dependencies>
    <!-- Testing -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>
    
    <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter</artifactId>
        <version>5.10.2</version>
        <scope>test</scope>
    </dependency>
    
    <dependency>
        <groupId>org.mockito</groupId>
        <artifactId>mockito-core</artifactId>
        <version>5.12.0</version>
        <scope>test</scope>
    </dependency>
    
    <dependency>
        <groupId>org.mockito</groupId>
        <artifactId>mockito-junit-jupiter</artifactId>
        <version>5.12.0</version>
        <scope>test</scope>
    </dependency>
    
    <dependency>
        <groupId>org.assertj</groupId>
        <artifactId>assertj-core</artifactId>
        <version>3.25.3</version>
        <scope>test</scope>
    </dependency>
    
    <!-- Integration Testing -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-webflux</artifactId>
        <scope>test</scope>
    </dependency>
    
    <dependency>
        <groupId>io.rest-assured</groupId>
        <artifactId>rest-assured</artifactId>
        <version>5.4.0</version>
        <scope>test</scope>
    </dependency>
    
    <!-- Test Containers (for integration tests) -->
    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>testcontainers</artifactId>
        <version>1.19.8</version>
        <scope>test</scope>
    </dependency>
    
    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>mysql</artifactId>
        <version>1.19.8</version>
        <scope>test</scope>
    </dependency>
    
    <!-- Code Coverage -->
    <dependency>
        <groupId>org.jacoco</groupId>
        <artifactId>jacoco-maven-plugin</artifactId>
        <version>0.8.12</version>
    </dependency>
</dependencies>

<build>
    <plugins>
        <!-- JaCoCo Coverage Plugin -->
        <plugin>
            <groupId>org.jacoco</groupId>
            <artifactId>jacoco-maven-plugin</artifactId>
            <version>0.8.12</version>
            <executions>
                <execution>
                    <goals>
                        <goal>prepare-agent</goal>
                    </goals>
                </execution>
                <execution>
                    <id>report</id>
                    <phase>test</phase>
                    <goals>
                        <goal>report</goal>
                    </goals>
                </execution>
            </executions>
            <configuration>
                <excludes>
                    <exclude>**/dto/**</exclude>
                    <exclude>**/entity/**</exclude>
                    <exclude>**/config/**</exclude>
                </excludes>
            </configuration>
        </plugin>
        
        <!-- Surefire Plugin for Test Execution -->
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-surefire-plugin</artifactId>
            <version>3.2.5</version>
            <configuration>
                <includes>
                    <include>**/*Test.java</include>
                    <include>**/*Tests.java</include>
                </includes>
            </configuration>
        </plugin>
    </plugins>
</build>
```

### 4.2 Backend Test Directory Structure

```
bmjServer/
├── src/
│   ├── test/
│   │   ├── java/
│   │   │   └── com/bookmyjuice/
│   │   │       ├── controllers/
│   │   │       │   ├── AuthControllerTest.java
│   │   │       │   ├── CheckoutControllerTest.java
│   │   │       │   └── OrderControllerTest.java
│   │   │       ├── services/
│   │   │       │   ├── AuthServiceTest.java
│   │   │       │   ├── ChargebeeServiceTest.java
│   │   │       │   └── OrderServiceTest.java
│   │   │       ├── repositories/
│   │   │       │   ├── UserRepositoryTest.java
│   │   │       │   └── OrderRepositoryTest.java
│   │   │       └── security/
│   │   │           ├── JwtUtilsTest.java
│   │   │           └── RateLimiterServiceTest.java
│   │   └── resources/
│   │       ├── application-test.properties
│   │       ├── test-data.sql
│   │       └── chargebee/
│   │           ├── mock-products.json
│   │           └── mock-subscriptions.json
```

---

## 5. Testing Frameworks Setup

### 5.1 Flutter Test Configuration

Create `lush/test/helpers/test_helpers.dart`:

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';

@GenerateMocks([
  UserRepository,
  CartRepository,
  ApiService,
  ChargebeeService,
])
void main() {}
```

Create `lush/test/helpers/test_constants.dart`:

```dart
class TestConstants {
  // Test User Data
  static const String testEmail = 'test@test.com';
  static const String testPassword = 'Test123!';
  static const String testFirstName = 'Test';
  static const String testLastName = 'User';
  static const String testPhone = '9876543210';
  
  // Test Product Data
  static const String testProductId = 'prod_test_juice';
  static const String testProductName = 'Test Juice';
  static const double testProductPrice = 100.0;
  
  // API Configuration
  static const String testApiUrl = 'http://localhost:8080';
  
  // Timeouts
  static const Duration apiTimeout = Duration(seconds: 30);
  static const Duration shortTimeout = Duration(seconds: 5);
}
```

### 5.2 Backend Test Configuration

Create `bmjServer/src/test/resources/application-test.properties`:

```properties
# Test Database Configuration
spring.datasource.url=jdbc:h2:mem:testdb;DB_CLOSE_DELAY=-1;DB_CLOSE_ON_EXIT=FALSE
spring.datasource.driverClassName=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=

# JPA Configuration
spring.jpa.database-platform=org.hibernate.dialect.H2Dialect
spring.jpa.hibernate.ddl-auto=create-drop
spring.jpa.show-sql=true

# Security Configuration
bezkoder.app.jwtSecret=TestJWTSecretKeyForTestingOnlyMustBe32CharsOrMore
bezkoder.app.jwtExpirationMs=900000

# Chargebee Test Configuration
chargebee.site=bookmyjuice-test
chargebee.apiKey=test_fake_key_for_testing

# Disable Email in Tests
spring.mail.host=localhost
spring.mail.port=0

# Logging
logging.level.com.bookmyjuice=DEBUG
logging.level.org.springframework=INFO
```

---

## 6. CI/CD Configuration

### 6.1 GitHub Actions Workflow

Create `.github/workflows/ci-cd.yml`:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  # Backend Tests
  backend-test:
    runs-on: ubuntu-latest
    
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: test_password
          MYSQL_DATABASE: bmj_test
          MYSQL_USER: bmj_test
          MYSQL_PASSWORD: test_password
        options: >-
          --health-cmd "mysqladmin ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 3306:3306
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: maven
      
      - name: Run Backend Tests
        run: |
          cd bmjServer
          mvn clean test -Dspring.profiles.active=test
      
      - name: Upload Test Results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: backend-test-results
          path: bmjServer/target/surefire-reports/
      
      - name: Upload Coverage Report
        uses: actions/upload-artifact@v4
        with:
          name: backend-coverage
          path: bmjServer/target/site/jacoco/

  # Frontend Tests
  frontend-test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.24.3'
          channel: 'stable'
      
      - name: Install Dependencies
        run: |
          cd lush
          flutter pub get
      
      - name: Run Flutter Analyzer
        run: |
          cd lush
          flutter analyze
      
      - name: Run Unit Tests
        run: |
          cd lush
          flutter test --coverage
      
      - name: Upload Coverage
        uses: codecov/codecov-action@v4
        with:
          file: lush/coverage/lcov.info
          flags: frontend

  # Build APK
  build-apk:
    needs: [backend-test, frontend-test]
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.24.3'
      
      - name: Build APK
        run: |
          cd lush
          flutter build apk --debug
      
      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: app-debug.apk
          path: lush/build/app/outputs/flutter-apk/app-debug.apk
```

---

## 7. Database Tools

### 7.1 SQLTools Configuration

Add to `.vscode/settings.json`:

```json
{
  "sqltools.connections": [
    {
      "name": "BookMyJuice DB (Local)",
      "driver": "MySQL",
      "server": "localhost",
      "port": 3306,
      "database": "bmj_db",
      "username": "bmj",
      "password": "PASS@123",
      "askForPassword": false
    },
    {
      "name": "BookMyJuice DB (Test)",
      "driver": "MySQL",
      "server": "localhost",
      "port": 3306,
      "database": "bmj_test",
      "username": "bmj_test",
      "password": "test_password",
      "askForPassword": false
    }
  ]
}
```

### 7.2 Database Migration Tool

Install Flyway CLI:

```powershell
# Windows (Chocolatey)
choco install flyway

# Verify installation
flyway --version
```

Configure `bmjServer/src/main/resources/flyway.conf`:

```properties
flyway.url=jdbc:mysql://localhost:3306/bmj_db
flyway.user=bmj
flyway.password=PASS@123
flyway.locations=filesystem:src/main/resources/db/migration
flyway.baselineOnMigrate=true
```

---

## 8. API Development Tools

### 8.1 REST Client Configuration

Create `api-tests/http-client.env.json`:

```json
{
  "local": {
    "baseUrl": "http://localhost:8080",
    "token": "{{loginResponse.accessToken}}"
  },
  "staging": {
    "baseUrl": "https://staging-api.bookmyjuice.co.in",
    "token": ""
  },
  "production": {
    "baseUrl": "https://api.bookmyjuice.co.in",
    "token": ""
  }
}
```

Create `api-tests/auth.http`:

```http
### Login Request
# @name login
POST {{baseUrl}}/api/auth/signin
Content-Type: application/json

{
  "username": "test@test.com",
  "password": "Test123!"
}

> {%
  client.global.set("loginResponse", response.body);
  client.global.set("accessToken", response.body.accessToken);
%}

### Auto-Login Request
GET {{baseUrl}}/api/auth/autologin
Authorization: Bearer {{accessToken}}
Accept: application/json

### Signup Request
POST {{baseUrl}}/api/auth/signup
Content-Type: application/json

{
  "username": "newuser@test.com",
  "password": "Test123!",
  "email": "newuser@test.com",
  "firstName": "New",
  "lastName": "User",
  "phone": "9876543210"
}
```

### 8.2 Swagger/OpenAPI Setup

Already configured in pom.xml. Access at:
- Local: http://localhost:8080/swagger-ui.html
- OpenAPI JSON: http://localhost:8080/v3/api-docs

---

## 9. Code Quality Tools

### 9.1 Flutter Linting

Create `lush/analysis_options.yaml`:

```yaml
include: package:flutter_lints/flutter.yaml

linter:
  rules:
    - prefer_const_constructors
    - prefer_const_literals_to_create_immutables
    - prefer_final_fields
    - avoid_print
    - avoid_unnecessary_containers
    - prefer_single_quotes
    - require_trailing_commas
    - sort_child_properties_last
    - use_key_in_widget_constructors

analyzer:
  exclude:
    - "**/*.g.dart"
    - "**/*.freezed.dart"
  errors:
    invalid_annotation_target: ignore
  language:
    strict-casts: true
    strict-inference: true
    strict-raw-types: true
```

### 9.2 Backend Code Quality

Add to `bmjServer/pom.xml`:

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-checkstyle-plugin</artifactId>
    <version>3.3.1</version>
    <configuration>
        <configLocation>google_checks.xml</configLocation>
    </configuration>
</plugin>

<plugin>
    <groupId>com.github.spotbugs</groupId>
    <artifactId>spotbugs-maven-plugin</artifactId>
    <version>4.8.5.0</version>
</plugin>
```

---

## 10. Development Environment Checklist

### 10.1 Prerequisites Installation

- [ ] Java JDK 17+ installed
- [ ] Flutter SDK 3.24+ installed
- [ ] Maven 3.8+ installed
- [ ] Git installed
- [ ] VS Code installed
- [ ] MySQL 8.0 installed (or Docker)
- [ ] Android Studio (for Android SDK)

### 10.2 VS Code Setup

- [ ] All extensions installed (Section 1)
- [ ] MCP servers configured (Section 2)
- [ ] Settings.json updated with project config
- [ ] Keybindings configured (optional)

### 10.3 Backend Setup

- [ ] Maven dependencies downloaded
- [ ] .env file configured with credentials
- [ ] Database created and accessible
- [ ] Chargebee test site configured
- [ ] Backend runs without errors

### 10.4 Frontend Setup

- [ ] Flutter pub get completed
- [ ] Android emulator configured
- [ ] iOS simulator configured (if on Mac)
- [ ] Test framework dependencies installed
- [ ] Frontend runs without errors

### 10.5 Testing Setup

- [ ] Backend test framework configured
- [ ] Frontend test framework configured
- [ ] Test directories created
- [ ] Sample test files created
- [ ] CI/CD pipeline configured

### 10.6 Documentation Setup

- [ ] BRD document created ✅
- [ ] Test Cases document created ✅
- [ ] API documentation accessible
- [ ] README files updated
- [ ] Contributing guidelines written

---

## 11. Local Backend on the LAN (physical device testing)

An emulator reaches the host at `10.0.2.2`, but a **physical phone over Wi-Fi** can only reach the
backend's real LAN address. `ops/run_local_server.ps1` + `ops/build_flutter_for_phone.ps1` exist so
this needs no manual editing of `application-dev.properties`.

### 11.1 One-time environment facts (verified on this machine, 2026-10-18)

| Fact | Consequence |
| :--- | :--- |
| Port **8080** is held by an unrelated local service (`AgentService`) | host the backend on **8085** |
| Dev MySQL is the Docker container `bmj-smoke-mysql`, published on **127.0.0.1:3307** | override `spring.datasource.url` (the committed URL says `:3306`) |
| `spring-dotenv` does **not** populate the environment for `java -jar` | `WEBHOOK_USERNAME`, `WEBHOOK_PASSWORD`, `JWT_SECRET` must be exported before launch or startup fails in `webhookUserDetailsService` |
| `.env` ships `ADMIN_PASSWORD=` (empty) | the launcher substitutes a local-only value |
| Docker Desktop's Windows CLI broker can be down while the engine runs | start containers from `wsl -d Ubuntu-22.04 -e docker ...` |

### 11.2 Start the backend

```powershell
# 1. Dev database (skip if `Test-NetConnection 127.0.0.1 -Port 3307` already succeeds)
wsl -d Ubuntu-22.04 -e docker start bmj-smoke-mysql

# 2. Backend on the LAN, OTPs printed to the console instead of sent by SMS
.\ops\run_local_server.ps1 -Restart -Port 8085
```

The script loads `.env`, forces `--spring.datasource.url=jdbc:mysql://127.0.0.1:3307/bmj_db?...`,
builds `com.bookmyjuice.bmjServer-*.jar` when `src/` is newer than it, launches `java -jar`, polls
`/api/health`, and prints the LAN URL to hand to Flutter. `-Rebuild` forces the package step and
`-EnableSms` keeps Fast2SMS live (a real, paid SMS per request).

Stop it with `.\ops\stop_local_server.ps1 -Port 8085` (refuses to kill a non-Java process unless `-Force`).

### 11.3 Run the app against it

```powershell
cd X:\BMJ\lush
flutter run -d 192.168.1.5:5555 --dart-define=API_BASE_URL=http://192.168.1.10:8085
```

`ops\build_flutter_for_phone.ps1 -Port 8085` does the same with the IP auto-detected (it defaults to
8080, so pass `-Port 8085` here). For a detached run, build and install instead:

```powershell
flutter build apk --debug --dart-define=API_BASE_URL=http://192.168.1.10:8085
adb -s 192.168.1.5:5555 install -r build\app\outputs\flutter-apk\app-debug.apk
adb -s 192.168.1.5:5555 shell am start -n com.bookmyjuice.app/.MainActivity
```

Wireless ADB uses `adb -s <phone-ip>:5555`; `adb devices` lists both the USB and Wi-Fi transports.

### 11.4 Read the OTP without a phone

With `FAST2SMS_API_KEY` blanked the server logs the code and returns
`"Success: OTP sent! Check console for OTP (Dev mode)"`:

```powershell
Select-String -Path X:\BMJ\bmjServer\logs\local-run.log -Pattern '\[DEV\] OTP' | Select-Object -Last 1
```

### 11.5 Gotcha that costs an hour

PowerShell parses `"$DbName?allowPublicKeyRetrieval=..."` as a **single variable** named
`DbName?allowPublicKeyRetrieval`, so the URL silently degrades to
`jdbc:mysql://127.0.0.1:3307/=true&useSSL=false` and MySQL answers
`Access denied for user 'bmj'@'%' to database '=true&useSSL=false'`. Always brace it:
`"...:3307/${DbName}?allowPublicKeyRetrieval=true&useSSL=false"`. The launcher carries this note.

### 11.6 Read the email verification code (mandatory-email signup)

Signup now sends an email OTP after the phone OTP. The code is **always** written
to the server log, even when SMTP delivery fails (a failed send is logged as a
warning and only invalidates the inbox delivery, not the code, which stays valid
for 10 minutes):

```powershell
Select-String -Path X:\BMJ\bmjServer\logs\local-run.log -Pattern '\[DEV\] Email verification code' |
  Select-Object -Last 1
```

Delivery settings come from `.env` (`MAIL_HOST=smtp.zoho.in`, `MAIL_PORT=587`,
`MAIL_USERNAME`, `MAIL_PASSWORD`). If the password is blank or the sender
mailbox is not verified with the provider, expect
`WARN ... Could not deliver email verification code to <address>` next to the
`[DEV]` line - the app still accepts the logged code, so device runs do not need
a working SMTP relay. Resends are refused for **30 seconds** per address
(`429` + "Please wait N seconds"), so always take the newest log line.

A full phone-first signup is therefore four HTTP calls plus two log reads:

```
send-otp -> login-otp (signupToken) -> send-email-verification -> verify-email-code
         -> phone-signup (email + emailVerificationToken; address optional)
```

---


---

## Quick Setup Commands

### Complete Environment Setup (Windows)

```powershell
# 1. Install VS Code Extensions
code --install-extension Dart-Code.dart
code --install-extension Dart-Code.flutter
code --install-extension vscjava.vscode-java-pack
code --install-extension vmware.vscode-spring-boot
code --install-extension hbenl.vscode-test-explorer
code --install-extension hbenl.vscode-java-test
code --install-extension esbenp.prettier-vscode
code --install-extension streetsidesoftware.code-spell-checker
code --install-extension GitHub.vscode-pull-request-github
code --install-extension mtxr.sqltools
code --install-extension mtxr.sqltools-driver-mysql
code --install-extension humao.rest-client
code --install-extension 42Crunch.vscode-openapi
code --install-extension ms-azuretools.vscode-docker
code --install-extension bierner.markdown-mermaid

# 2. Setup Backend
cd x:\BMJ\bmjServer
.\mvnw.cmd clean install

# 3. Setup Frontend
cd x:\BMJ\lush
flutter clean
flutter pub get

# 4. Verify Setup
# Backend
cd x:\BMJ\bmjServer
.\mvnw.cmd spring-boot:run

# Frontend (new terminal)
cd x:\BMJ\lush
flutter run --dart-define=API_BASE_URL=http://localhost:8080
```

---

**Document Control:**
- **Created:** March 27, 2026
- **Last Updated:** March 27, 2026
- **Version:** 1.0
- **Status:** Ready for Implementation

---

## Next Steps

1. **Install all VS Code extensions** (15 mins)
2. **Configure MCP servers** (10 mins)
3. **Update pubspec.yaml with test dependencies** (5 mins)
4. **Update pom.xml with test dependencies** (5 mins)
5. **Create test directory structure** (10 mins)
6. **Create first test files for each module** (30 mins per module)
7. **Run initial test suite** (15 mins)
8. **Fix any failing tests** (as needed)
9. **Begin implementation following BRD requirements**

**Total Setup Time:** ~3-4 hours

**Implementation Time:** 4-6 weeks (following SDLC phases in BRD)
