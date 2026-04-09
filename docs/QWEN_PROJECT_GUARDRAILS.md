# BookMyJuice Qwen Anti-Hallucination Guardrails v2.0

**Date:** April 1, 2026  
**Status:** LIVE (Updated after duplicate endpoint incident)  
**Version:** 2.0 (Added Spring context validation)

---

## 🎯 Purpose

Qwen **MUST** follow these rules before generating any code. Violations = immediate rejection.

**CRITICAL LESSON LEARNED:** Unit tests alone don't catch Spring mapping errors. Integration tests and application startup verification are MANDATORY.

---

## 📋 Source of Truth Hierarchy

1. **BRD** [file:182] = BEHAVIOR (FR-XXXX, UC-XXX, TC-XXXX)
2. **ADRs** [file:173,175] = ARCHITECTURE (boundaries, patterns)
3. **DESIGN_SYSTEM** [file:183] = UI (AppTextField, AppButton, colors)
4. **IMPLEMENTATION_PROGRESS** [file:167] = CURRENT STATE
5. **SDLC_PLAN** [file:15] = TASK ORDER (Phase 1→9)

---

## 🚨 MANDATORY Pre-Code Checklist

Qwen MUST complete ALL steps and paste results BEFORE coding.

### **STEP 1: CODE AUDIT** (2 mins)
```bash
$ grep -r "SignUpScreen|FR-AUTH-001|email field" lush/lib/
$ ls -la lush/lib/views/screens/
```
**FILES FOUND:** [list exact files + line numbers]  
**EXISTING UI FIELDS:** [screenshot or grep output]

### **STEP 2: REQ MAPPING**
```
FR-AUTH-001 [file:182]: "email valid format, password min 8 chars, first/last name, phone 10 digits"
UC-001: "User enters email, password, name, phone → taps Sign Up"
TC-AUTH-001: "Valid signup → HTTP 200"
```

### **STEP 3: UI MAPPING** [file:183]
- ✅ AppTextField(label: 'Email', prefixIcon: Icons.email)
- ✅ AppTextField(obscureText: true) for password
- ✅ Form validation before submit
- ✅ Google signup: Email/Name/Photo pre-filled from Google (READ-ONLY)
- ✅ Google signup: User enters phone, address, password (EDITABLE)
- ❌ Custom TextField → REJECT
- ❌ Allowing edit of Google-fetched fields → REJECT

### **STEP 4: TEST FIRST** ⚠️ UPDATED
```bash
# Unit tests (REQUIRED but NOT SUFFICIENT)
flutter test test/widget/signup_screen_test.dart

# Backend unit tests (REQUIRED but NOT SUFFICIENT)
cd bmjServer && mvn test -Dtest=AuthControllerTest

# Integration tests (REQUIRED - catches Spring errors)
cd bmjServer && mvn test -Dtest=*IntegrationTest

# ALL must pass before coding continues
```

### **STEP 5: ARCHITECTURE CHECK** [file:173]
- ✅ Flutter → bmjServer API → Chargebee (NO direct Chargebee)
- ✅ BLoC: Event → emit(state) → BlocBuilder rebuilds
- ✅ Spring: No duplicate @PostMapping mappings
- ✅ Spring: Application context loads successfully

**IF ANY STEP FAILS** → STOP. Report: "Missing [X] in [file]. Cannot proceed."

### **STEP 6: SPRING CONTEXT VALIDATION** ⚠️ NEW - MANDATORY
```bash
# This catches duplicate mappings, bean conflicts, etc.
cd bmjServer
mvn clean test  # Unit tests must pass
mvn spring-boot:run &  # Start actual application
sleep 30  # Wait for full startup
curl http://localhost:8080/api/health  # Verify app is running
curl http://localhost:8080/api/auth/signin  # Verify endpoints work
```

**MUST PASS:**
- ✅ Application starts without "Ambiguous mapping" errors
- ✅ All endpoints respond (200/400/401 as appropriate)
- ✅ No bean creation exceptions

---

## ❌ Forbidden Hallucinations

- ❌ "Signup works" without UI fields present
- ❌ Invent endpoints without grep proof
- ❌ Custom UI without DESIGN_SYSTEM
- ❌ Backend success without Flutter form validation
- ❌ Assume fields exist → **MUST audit first**
- ❌ Skip tests → **NO CODE**
- ❌ print/debugPrint spam → logger only
- ❌ **"All tests pass" with only unit tests** → **MUST RUN INTEGRATION TESTS** ⚠️
- ❌ **"Application ready" without starting it** → **MUST VERIFY STARTUP** ⚠️

---

## ✅ Code Generation Contract

1. **AUDIT** → paste grep/ls output
2. **MAP** → quote exact FR/TC/UI spec
3. **TEST** → write test → `flutter test` ✅ + `mvn test` ✅
4. **CODE** → modify ONLY audited files
5. **VALIDATE** → `flutter analyze` + hot reload check
6. **PROVE** → "Fields present, test passes, UI updates"
7. **STARTUP** → `mvn spring-boot:run` ✅ **NO ERRORS** ⚠️ NEW

---

## 🛠️ Validation Commands (Run After)

```bash
# Lint
flutter analyze --fatal-infos

# Tests  
flutter test test/widget/signup_screen_test.dart  # TC-AUTH-001
cd bmjServer && mvn test  # All unit tests
cd bmjServer && mvn test -Dtest=*IntegrationTest  # Integration tests

# CRITICAL: Application Startup (catches duplicate mappings)
cd bmjServer && mvn spring-boot:run &
sleep 30
curl http://localhost:8080/api/health

# UI Check
flutter run --hot  # Add item → cart updates?

# Backend
curl -X POST http://localhost:8080/api/auth/signup -d '{"email":"test@test.com"}'
```

---

## 📂 File Inventory (50 Files)

| File | Type | Purpose |
|------|------|---------|
| `requirements.yaml` | BRD | Business requirements (FR-XXXX) |
| `docs/DESIGN_SYSTEM.md` | UI | Component specs (AppTextField, etc.) |
| `docs/SDLC_Implementation_Plan.md` | Plan | Task order (Phase 1-9) |
| `docs/IMPLEMENTATION_PROGRESS.md` | Status | Current state |
| `docs/architecture/ADR-003-chargebee-integration-strategy.md` | Arch | System boundaries |
| `docs/architecture/ADR-004-unified-signup-flow.md` | Arch | Signup architecture |
| `docs/Test_Cases_Detailed.md` | Test | 30+ test cases |
| `docs/API.md` | API | Endpoint specs |
| `docs/DEVELOPMENT_TOOLS_Configuration.md` | Setup | IDE/tools config |
| `docs/QWEN_PROJECT_GUARDRAILS.md` | Guardrails | **AI development rules** |

---

## 💡 Example Good Prompt

```markdown
/clear
## QWEN GUARDRAILS v2.0 [file:182][file:183]

**AUDIT**:
$ grep -r "SignUpScreen" lush/lib/
→ lush/lib/views/screens/SignUpScreen.dart:10 (no email field found)

**REQ MAPPING**:
FR-AUTH-001: email/password/name/phone required

**UNIT TESTS**:
$ flutter test test/widgets/signup_screen_test.dart
→ 00:00 +6: All tests passed!

**BACKEND TESTS**:
$ cd bmjServer && mvn test
→ Tests run: 26, Failures: 0, Errors: 0

**SPRING CONTEXT**:
$ cd bmjServer && mvn spring-boot:run &
→ ChargeBee configured successfully
→ Tomcat started on port(s): 8080 (http)
→ Application run successfully (NO "Ambiguous mapping" errors)

**TASK**: Fix SignUpScreen.dart missing fields.
```

---

## ❌ Example Bad Prompt (Will Fail)

```markdown
Fix signup flow.

$ mvn test
→ Tests run: 26, Failures: 0

✅ Done!
```

**Why it fails:**
- ❌ No code audit
- ❌ No requirement mapping
- ❌ No Spring context validation
- ❌ Didn't catch duplicate @PostMapping mappings
- ❌ Didn't verify application startup

---

## 🎖️ Success Criteria

- ✅ Code audit shows current state
- ✅ Exact FR/TC quoted
- ✅ DESIGN_SYSTEM components used
- ✅ Tests written first + pass (unit AND integration)
- ✅ No print/debugPrint
- ✅ Hot reload UI updates work
- ✅ **Spring application starts without errors** ⚠️ NEW
- ✅ **No duplicate endpoint mappings** ⚠️ NEW
- ✅ **All endpoints respond to HTTP calls** ⚠️ NEW

---

## 📝 Lessons Learned (April 1, 2026)

### Incident: Duplicate @PostMapping("/signin")

**What happened:**
- Two methods mapped to same endpoint
- Unit tests passed (Mockito doesn't load Spring context)
- Application failed to start (Spring caught duplicate mapping)

**Why guardrails failed:**
- No requirement to run `mvn spring-boot:run`
- No integration tests with `@SpringBootTest`
- No endpoint mapping validation

**Fixes applied:**
- ✅ Added STEP 6: Spring Context Validation
- ✅ Updated "Forbidden Hallucinations" to include "All tests pass" without integration tests
- ✅ Updated "Success Criteria" to include application startup verification
- ✅ Updated validation commands to include `mvn spring-boot:run`

---

## Document Control

**Created:** March 31, 2026  
**Updated:** April 1, 2026 (after duplicate endpoint incident)  
**Version:** 2.0  
**Next Review:** April 7, 2026

**Enforcement:** ALL Qwen prompts MUST use this template. Violations = immediate rejection.
