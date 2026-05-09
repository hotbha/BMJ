# Contributing to BookMyJuice

Thank you for contributing to BookMyJuice! This document provides guidelines and processes for developing our cold-pressed juice subscription and ordering platform.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Development Setup](#development-setup)
- [Git Workflow](#git-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Architecture Decisions](#architecture-decisions)
- [Chargebee Integration Guidelines](#chargebee-integration-guidelines)

---

## 🌟 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Prioritize user experience and security
- Document your changes

---

## 🚀 Development Setup

### Prerequisites

- **Java 17+** (Backend)
- **Flutter 3.x** (Frontend)
- **MySQL 8.x** (Database)
- **Maven 3.8+** (Backend build)
- **VS Code** (Recommended IDE)

### Required VS Code Extensions

```json
{
  "recommendations": [
    "redhat.java",
    "vmware.vscode-spring-boot",
    "Dart-Code.dart",
    "Dart-Code.flutter",
    "vscjava.vscode-java-pack",
    "ms-azuretools.vscode-docker",
    "mtxr.sqltools",
    "esbenp.prettier-vscode",
    "GitHub.copilot",
    "GitHub.vscode-pull-request-github"
  ]
}
```

### Chargebee MCP Setup (MANDATORY)

**Install Chargebee MCP in VSCode:**

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "Chargebee MCP"
4. Install the extension
5. Configure with your Chargebee API key:
   ```json
   {
     "chargebee.site": "bookmyjuice-test",
     "chargebee.apiKey": "test_your_api_key_here"
   }
   ```

**Why Chargebee MCP is Mandatory:**
- Most functionalities are managed by Chargebee, not custom-built
- MCP provides real-time access to Chargebee documentation
- Test API calls directly from VS Code
- Understand webhook payloads and events
- Debug Chargebee integration issues faster

**Using Chargebee MCP:**

```
# Example queries to Chargebee MCP:

"How does Chargebee hosted page checkout work?"
"What API endpoint to create a subscription?"
"What webhook events are triggered when payment fails?"
"Show me the Chargebee customer object structure"
"How to pause a subscription via API?"
```

---

## 🔄 Git Workflow

### Branch Naming Convention

```
<type>/<ticket-id>-<short-description>
```

**Types:**
- `feature/` - New features (e.g., `feature/BMJ-101-add-otp-auth`)
- `bugfix/` - Bug fixes (e.g., `bugfix/BMJ-102-fix-cart-total`)
- `hotfix/` - Critical production fixes
- `refactor/` - Code refactoring
- `docs/` - Documentation updates
- `test/` - Test additions/updates
- `chore/` - Maintenance tasks

**Examples:**
```bash
git checkout -b feature/BMJ-101-add-otp-authentication
git checkout -b bugfix/BMJ-102-fix-cart-calculation
git checkout -b docs/add-api-documentation
```

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting, missing semi-colons, etc
- `refactor:` Code restructuring
- `test:` Adding tests
- `chore:` Maintenance

**Examples:**
```bash
feat(auth): add Google Sign-In integration

Implemented Google Sign-In using flutter_google_sign_in package.
- Added GoogleAuthBloc for state management
- Integrated with backend Google auth endpoint
- Added unit tests for Google auth flow

Closes #101

---

fix(cart): resolve incorrect total calculation with tax

Tax was being applied twice when subscription discount existed.
- Fixed tax calculation in CartRepository
- Added test case for subscription + tax scenario

Fixes #102
```

### Pull Request Branch Flow

```
main (production)
  ↑
staging (pre-production)
  ↑
feature branches
```

1. Branch from `staging`
2. Develop feature
3. Create PR to `staging`
4. After testing, `staging` merges to `main`

---

## 📝 Coding Standards

### Backend (Java/Spring Boot)

#### Code Style

```java
// ✅ DO: Use descriptive names
public class SubscriptionService {
    private final SubscriptionRepository subscriptionRepository;
    
    public Subscription createSubscription(CreateSubscriptionRequest request) {
        // Implementation
    }
}

// ❌ DON'T: Use abbreviations or vague names
public class SubServ {
    private SubRepo repo;
    
    public Sub createSub(Map req) {
        // Implementation
    }
}
```

#### Class Structure

```java
@RestController
@RequestMapping("/api/v1/subscription")
@RequiredArgsConstructor
@Transactional
public class SubscriptionController {
    
    // 1. Dependencies (final, private)
    private final SubscriptionService subscriptionService;
    private final ChargebeeService chargebeeService;
    
    // 2. Constants
    private static final String SUCCESS = "success";
    
    // 3. Public methods (controllers, services)
    @PostMapping
    public ResponseEntity<ApiResponse<Subscription>> createSubscription(
            @Valid @RequestBody CreateSubscriptionRequest request) {
        // Implementation
    }
    
    // 4. Private helper methods
    private void validateSubscription(CreateSubscriptionRequest request) {
        // Implementation
    }
}
```

#### Exception Handling

```java
// ✅ DO: Use global exception handler
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleResourceNotFound(
            ResourceNotFoundException ex) {
        return ResponseEntity
            .status(HttpStatus.NOT_FOUND)
            .body(new ErrorResponse(ex.getMessage()));
    }
}

// ❌ DON'T: Catch generic exceptions
try {
    // code
} catch (Exception e) {
    e.printStackTrace();  // Never do this
}
```

#### API Response Format

```java
// Standard response structure
{
    "timestamp": "2026-03-27T10:30:00Z",
    "status": 200,
    "message": "Subscription created successfully",
    "data": { ... },
    "errors": []
}

// Error response
{
    "timestamp": "2026-03-27T10:30:00Z",
    "status": 400,
    "message": "Validation failed",
    "errors": [
        {
            "field": "email",
            "message": "Invalid email format"
        }
    ]
}
```

### Frontend (Flutter/Dart)

#### Code Style

```dart
// ✅ DO: Use meaningful names
class SubscriptionBloc extends Bloc<SubscriptionEvent, SubscriptionState> {
  final SubscriptionRepository _repository;
  
  SubscriptionBloc({required SubscriptionRepository repository})
      : _repository = repository,
        super(SubscriptionInitial());
}

// ❌ DON'T: Use abbreviations
class SubBloc extends Bloc<SubEvent, SubState> {
  final SubRepo _repo;
}
```

#### BLoC Pattern

```dart
// Events
abstract class SubscriptionEvent extends Equatable {
  const SubscriptionEvent();
  
  @override
  List<Object?> get props => [];
}

class LoadSubscription extends SubscriptionEvent {
  final String subscriptionId;
  
  const LoadSubscription({required this.subscriptionId});
  
  @override
  List<Object?> get props => [subscriptionId];
}

// States
abstract class SubscriptionState extends Equatable {
  const SubscriptionState();
  
  @override
  List<Object?> get props => [];
}

class SubscriptionLoading extends SubscriptionState {}

class SubscriptionLoaded extends SubscriptionState {
  final Subscription subscription;
  
  const SubscriptionLoaded({required this.subscription});
  
  @override
  List<Object?> get props => [subscription];
}

class SubscriptionError extends SubscriptionState {
  final String message;
  
  const SubscriptionError({required this.message});
  
  @override
  List<Object?> get props => [message];
}
```

#### Widget Structure

```dart
class SubscriptionScreen extends StatelessWidget {
  const SubscriptionScreen({super.key});
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: _buildAppBar(context),
      body: BlocBuilder<SubscriptionBloc, SubscriptionState>(
        builder: (context, state) {
          if (state is SubscriptionLoading) {
            return const LoadingIndicator();
          }
          if (state is SubscriptionLoaded) {
            return _buildSubscriptionList(state.subscriptions);
          }
          if (state is SubscriptionError) {
            return ErrorWidget(message: state.message);
          }
          return const EmptyState();
        },
      ),
    );
  }
  
  PreferredSizeWidget _buildAppBar(BuildContext context) {
    return AppBar(
      title: const Text('Subscriptions'),
      actions: [
        IconButton(
          icon: const Icon(Icons.add),
          onPressed: () => _navigateToCreate(context),
        ),
      ],
    );
  }
}
```

#### Error Handling

```dart
// ✅ DO: Handle errors gracefully
try {
  await _repository.createSubscription(request);
  emit(SubscriptionCreated());
} on ApiException catch (e) {
  emit(SubscriptionError(message: e.message));
} on SocketException catch (_) {
  emit(SubscriptionError(message: 'No internet connection'));
} catch (e) {
  emit(SubscriptionError(message: 'An unexpected error occurred'));
}
```

---

## 🧪 Testing Guidelines

### Backend Testing

```java
@SpringBootTest
@AutoConfigureMockMvc
class SubscriptionControllerTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @MockBean
    private SubscriptionService subscriptionService;
    
    @Test
    @DisplayName("Should create subscription successfully")
    void shouldCreateSubscription() throws Exception {
        // Given
        CreateSubscriptionRequest request = new CreateSubscriptionRequest();
        request.setPlanId("plan_123");
        request.setCustomerId("cust_456");
        
        Subscription subscription = new Subscription();
        subscription.setId("sub_789");
        
        when(subscriptionService.create(request)).thenReturn(subscription);
        
        // When & Then
        mockMvc.perform(post("/api/v1/subscriptions")
                .contentType(MediaType.APPLICATION_JSON)
                .content(asJsonString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.id").value("sub_789"));
    }
}
```

### Frontend Testing

```dart
// Widget Test
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('SubscriptionCard Widget Tests', () {
    testWidgets('displays subscription details correctly', (tester) async {
      // Arrange
      final subscription = Subscription(
        id: 'sub_123',
        planName: 'Monthly Plan',
        status: SubscriptionStatus.active,
      );
      
      // Act
      await tester.pumpWidget(
        MaterialApp(
          home: SubscriptionCard(subscription: subscription),
        ),
      );
      
      // Assert
      expect(find.text('Monthly Plan'), findsOneWidget);
      expect(find.text('Active'), findsOneWidget);
    });
  });
}

// BLoC Test
import 'package:bloc_test/bloc_test.dart';

void main() {
  group('SubscriptionBloc Tests', () {
    late SubscriptionBloc bloc;
    late MockSubscriptionRepository mockRepository;
    
    setUp(() {
      mockRepository = MockSubscriptionRepository();
      bloc = SubscriptionBloc(repository: mockRepository);
    });
    
    tearDown(() => bloc.close());
    
    blocTest<SubscriptionBloc, SubscriptionState>(
      'emits [Loading, Loaded] when LoadSubscription is added',
      build: () {
        when(() => mockRepository.getSubscription('sub_123'))
            .thenAnswer((_) async => testSubscription);
        return bloc;
      },
      act: (bloc) => bloc.add(const LoadSubscription(subscriptionId: 'sub_123')),
      expect: () => [
        SubscriptionLoading(),
        SubscriptionLoaded(subscription: testSubscription),
      ],
    );
  });
}
```

### Test Coverage Requirements

- **Unit Tests:** Minimum 80% coverage
- **Integration Tests:** All critical user flows
- **E2E Tests:** Core features (auth, subscription, orders)

---

## 📤 Pull Request Process

### PR Checklist

Before submitting a PR, ensure:

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests added/updated (unit, integration, E2E)
- [ ] Documentation updated (README, API docs, comments)
- [ ] No new warnings introduced
- [ ] CHANGELOG.md updated (if applicable)
- [ ] All tests pass locally

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix/feature affecting existing functionality)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Manual testing completed

## Screenshots (if UI changes)
Before: 
After:

## Related Issues
Closes #<issue-number>

## Deployment Notes
Any special deployment considerations?
```

### Code Review Guidelines

**Reviewers will check:**
- Code quality and readability
- Test coverage
- Security implications
- Performance impact
- Documentation completeness

**Review response time:** 24-48 hours

---

## 🏛️ Architecture Decisions

### Decision Records (ADR)

All significant architecture decisions documented in `docs/architecture/`:

```
docs/
└── architecture/
    ├── ADR-001-database-selection.md
    ├── ADR-002-state-management-pattern.md
    ├── ADR-003-chargebee-integration.md
    └── ADR-004-offline-support-strategy.md
```

### ADR Template

```markdown
# ADR-<Number>: <Title>

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
What is the issue that we're seeing?

## Decision
What is the change that we're proposing?

## Consequences
- Positive outcomes
- Negative outcomes
- Risks

## References
- Links to related documents
```

---

## 📚 Additional Resources

- [Spring Boot Documentation](https://spring.io/projects/spring-boot)
- [Flutter Documentation](https://docs.flutter.dev/)
- [Chargebee API Reference](https://www.chargebee.com/docs/2.0/api.html)

---

## 🤖 AI Development Guidelines (Qwen)

### Qwen Project Guardrails

**ALL AI-assisted development MUST follow `docs/QWEN_PROJECT_GUARDRAILS.md`**

#### Mandatory Pre-Code Checklist

Before generating any code, Qwen MUST:

1. **Code Audit** - Run grep/ls commands to verify current state
2. **Requirement Mapping** - Quote exact FR/TC from BRD [file:182]
3. **UI Mapping** - Use only DESIGN_SYSTEM [file:183] components
4. **Test First** - Write test → run → pass → then code
5. **Architecture Check** - Verify against ADRs [file:173,175]

#### Forbidden Actions

- ❌ Assuming fields exist without audit proof
- ❌ Inventing endpoints without grep verification
- ❌ Using custom UI components instead of DESIGN_SYSTEM
- ❌ Skipping tests
- ❌ Using print/debugPrint (use logger only)

#### Code Generation Contract

1. **AUDIT** → Paste grep/ls output
2. **MAP** → Quote exact FR/TC/UI spec
3. **TEST** → Write test → `flutter test` ✅
4. **CODE** → Modify ONLY audited files
5. **VALIDATE** → `flutter analyze` + hot reload
6. **PROVE** → "Fields present, test passes, UI updates"

#### Example Valid Prompt

```markdown
## QWEN GUARDRAILS v1.0 [file:182][file:183]

**AUDIT**:
$ grep -r "SignUpScreen" lush/lib/
→ lush/lib/views/screens/SignUpScreen.dart:10 (no email field found)

**REQ MAPPING**:
FR-AUTH-001: email/password/name/phone required

**TASK**: Fix SignUpScreen.dart missing fields.
```

**See:** `docs/QWEN_PROJECT_GUARDRAILS.md` for complete guidelines.
- [BLoC Library](https://bloclibrary.dev/)

---

## 🤔 Questions?

Reach out to the team via:
- Slack: #bookmyjuice-dev
- Email: dev@bookmyjuice.co.in
