# ADR-002: State Management Pattern - BLoC

## Status

ACCEPTED

## Context

The BookMyJuice Flutter application requires a state management solution that:
- Scales well for a growing codebase
- Supports testability
- Provides clear separation of concerns
- Handles complex async operations (API calls, Chargebee integration)
- Enables team collaboration with clear patterns
- Supports both simple and complex UI states

Key requirements:
- Predictable state transitions
- Easy to test and debug
- Separation of business logic from UI
- Support for dependency injection
- Good tooling and IDE support

## Decision

We selected the **BLoC (Business Logic Component)** pattern with the `flutter_bloc` library.

### Rationale

1. **Separation of Concerns**: Clear separation between UI, business logic, and data
2. **Testability**: BLoCs can be tested independently of UI
3. **Predictability**: Unidirectional data flow (Event → BLoC → State → UI)
4. **Scalability**: Works well for large applications with complex state
5. **Debugging**: Excellent dev tools for tracing state changes
6. **Team Familiarity**: Team has experience with reactive patterns
7. **Reusability**: BLoCs can be reused across multiple screens

### Alternatives Considered

**Provider:**
- Pros: Simple, built-in, good for small apps
- Cons: Less structure, harder to test, can become spaghetti code
- Verdict: Too simple for our complex subscription/order flows

**Riverpod:**
- Pros: Compile-time safety, no context dependency, excellent architecture
- Cons: Steeper learning curve, newer ecosystem
- Verdict: Strong contender, but BLoC more mature for our needs

**GetX:**
- Pros: Very simple, many features bundled
- Cons: Too magical, hard to debug, not recommended for large teams
- Verdict: Rejected due to lack of structure

**Cubit:**
- Pros: Simpler than BLoC, same library
- Cons: Less explicit event tracking
- Verdict: Using BLoC for complex flows, may use Cubit for simple states

## Consequences

### Positive

- Clear architecture that scales
- Easy to onboard new developers (well-documented pattern)
- Excellent testability with `bloc_test` package
- Great debugging with Flutter DevTools
- Reusable business logic across screens

### Negative

- More boilerplate code (Events, States, BLoC classes)
- Steeper learning curve for developers new to reactive programming
- Can be overkill for simple screens

### Risks

- **Over-engineering**: May create BLoCs for simple state
  - Mitigation: Use Cubit or simple StatefulWidgets for trivial cases
- **Boilerplate**: Lots of files for each feature
  - Mitigation: Use code generation templates
- **Stream Complexity**: Debugging stream issues can be hard
  - Mitigation: Team training, clear documentation

## Implementation

### BLoC Structure

```dart
// Events
abstract class SubscriptionEvent extends Equatable {}

class LoadSubscription extends SubscriptionEvent {
  final String subscriptionId;
  const LoadSubscription({required this.subscriptionId});
  
  @override
  List<Object?> get props => [subscriptionId];
}

// States
abstract class SubscriptionState extends Equatable {}

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

// BLoC
class SubscriptionBloc extends Bloc<SubscriptionEvent, SubscriptionState> {
  final SubscriptionRepository repository;
  
  SubscriptionBloc({required this.repository})
      : super(SubscriptionInitial()) {
    on<LoadSubscription>(_onLoadSubscription);
  }
  
  Future<void> _onLoadSubscription(
    LoadSubscription event,
    Emitter<SubscriptionState> emit,
  ) async {
    emit(SubscriptionLoading());
    try {
      final subscription = await repository.getSubscription(event.subscriptionId);
      emit(SubscriptionLoaded(subscription: subscription));
    } catch (e) {
      emit(SubscriptionError(message: e.toString()));
    }
  }
}
```

### Usage in Screens

```dart
class SubscriptionScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => SubscriptionBloc(
        repository: context.read<SubscriptionRepository>(),
      )..add(LoadSubscription(subscriptionId: 'sub_123')),
      child: BlocBuilder<SubscriptionBloc, SubscriptionState>(
        builder: (context, state) {
          if (state is SubscriptionLoading) {
            return LoadingIndicator();
          }
          if (state is SubscriptionLoaded) {
            return SubscriptionView(subscription: state.subscription);
          }
          if (state is SubscriptionError) {
            return ErrorWidget(message: state.message);
          }
          return EmptyState();
        },
      ),
    );
  }
}
```

## References

- [flutter_bloc package](https://pub.dev/packages/flutter_bloc)
- [BLoC Library Documentation](https://bloclibrary.dev/)
- [Flutter BLoC Tutorials](https://www.youtube.com/c/ResoCoder)

---

*Date: 2026-03-27*
*Authors: BookMyJuice Engineering Team*
