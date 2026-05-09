import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:lush/bloc/AuthBloc/auth_bloc.dart';
import 'package:lush/theme/theme_cubit.dart';
import 'package:lush/views/models/user.dart';
import 'package:lush/views/screens/sign_up_screen.dart';

/// Widget Tests for SignUpScreen
///
/// TC-AUTH-001: Email-first signup with valid data
/// TC-AUTH-002: Email validation
/// TC-AUTH-003: Password validation
/// TC-AUTH-004: Phone validation
/// TC-AUTH-005: Form submission

void main() {
  group('SignUpScreen Widget Tests', () {

    // Helper to create a dummy User object for testing
    User createTestUser({
      String email = '',
      String firstName = '',
      String lastName = '',
      String phone = '',
    }) {
      return User(
        id: 'test-id',
        email: email,
        phone: phone,
        role: 'user',
        firstName: firstName,
        lastName: lastName,
        password: '',
        address: '',
        city: '',
        country: '',
        extendedAddr: '',
        extendedAddr2: '',
        state: '',
        zip: '',
      );
    }

    // Helper to build the SignUpScreen wrapped with required providers
    Widget buildSignUpScreen(User user) {
      return MultiBlocProvider(
        providers: [
          BlocProvider<AuthenticationBloc>(
            create: (_) => AuthenticationBloc(),
          ),
          BlocProvider<ThemeCubit>(
            create: (_) => ThemeCubit(),
          ),
        ],
        child: MaterialApp(
          home: SignUpScreen(user: user),
        ),
      );
    }

    // Helper to build SignUpScreen with custom routes for navigation tests
    Widget buildSignUpScreenWithRoutes(User user, Map<String, WidgetBuilder> routes) {
      return MultiBlocProvider(
        providers: [
          BlocProvider<AuthenticationBloc>(
            create: (_) => AuthenticationBloc(),
          ),
          BlocProvider<ThemeCubit>(
            create: (_) => ThemeCubit(),
          ),
        ],
        child: MaterialApp(
          home: SignUpScreen(user: user),
          routes: routes,
        ),
      );
    }

    // ============================================================
    // TC-AUTH-002: Email validation
    // ============================================================
    testWidgets('TC-AUTH-002: Email field validation',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        buildSignUpScreen(createTestUser()),
      );

      // Test empty email
      await tester.enterText(find.byType(TextFormField).at(0), '');
      await tester.pumpAndSettle();
      await tester.tap(find.text('Create Account'));
      await tester.pumpAndSettle();
      expect(find.text('Email is required'), findsOneWidget);

      // Test invalid email format
      await tester.enterText(find.byType(TextFormField).at(0), 'invalid-email');
      await tester.pumpAndSettle();
      await tester.tap(find.text('Create Account'));
      await tester.pumpAndSettle();
      expect(find.text('Enter a valid email'), findsOneWidget);

      // Test valid email
      await tester.enterText(find.byType(TextFormField).at(0), 'test@example.com');
      await tester.pumpAndSettle();
      await tester.tap(find.text('Create Account'));
      await tester.pumpAndSettle();
      expect(find.text('Email is required'), findsNothing);
      expect(find.text('Enter a valid email'), findsNothing);
    });

    // ============================================================
    // TC-AUTH-003: Password validation
    // ============================================================
    testWidgets('TC-AUTH-003: Password field validation',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        buildSignUpScreen(createTestUser()),
      );

      // Test empty password
      await tester.enterText(find.byType(TextFormField).at(4), '');
      await tester.pumpAndSettle();
      await tester.tap(find.text('Create Account'));
      await tester.pumpAndSettle();
      expect(find.text('Password is required'), findsOneWidget);

      // Test weak password (too short)
      await tester.enterText(find.byType(TextFormField).at(4), 'weak');
      await tester.pumpAndSettle();
      await tester.tap(find.text('Create Account'));
      await tester.pumpAndSettle();
      expect(find.text('Password does not meet requirements'), findsOneWidget);

      // Test password without special character
      await tester.enterText(find.byType(TextFormField).at(4), 'NoSpecial123');
      await tester.pumpAndSettle();
      await tester.tap(find.text('Create Account'));
      await tester.pumpAndSettle();
      expect(find.text('Password does not meet requirements'), findsOneWidget);

      // Test strong password
      await tester.enterText(find.byType(TextFormField).at(4), 'SecurePass123!');
      await tester.pumpAndSettle();

      // Verify password requirements are met (green checkmarks)
      expect(find.byIcon(Icons.check_circle), findsWidgets);
    });

    // ============================================================
    // TC-AUTH-004: Phone validation
    // ============================================================
    testWidgets('TC-AUTH-004: Phone field validation',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        buildSignUpScreen(createTestUser()),
      );

      // Test empty phone
      await tester.enterText(find.byType(TextFormField).at(3), '');
      await tester.pumpAndSettle();
      await tester.tap(find.text('Create Account'));
      await tester.pumpAndSettle();
      expect(find.text('Phone number is required'), findsOneWidget);

      // Test invalid phone (less than 10 digits)
      await tester.enterText(find.byType(TextFormField).at(3), '12345');
      await tester.pumpAndSettle();
      await tester.tap(find.text('Create Account'));
      await tester.pumpAndSettle();
      expect(find.text('Enter a valid 10-digit number'), findsOneWidget);

      // Test invalid phone (starts with wrong digit)
      await tester.enterText(find.byType(TextFormField).at(3), '1234567890');
      await tester.pumpAndSettle();
      await tester.tap(find.text('Create Account'));
      await tester.pumpAndSettle();
      expect(find.text('Enter a valid 10-digit number'), findsOneWidget);

      // Test valid phone
      await tester.enterText(find.byType(TextFormField).at(3), '9876543210');
      await tester.pumpAndSettle();
      expect(find.text('Phone number is required'), findsNothing);
      expect(find.text('Enter a valid 10-digit number'), findsNothing);
    });

    // ============================================================
    // TC-AUTH-005: Form submission validation
    // ============================================================
    testWidgets('TC-AUTH-005: Form submission with incomplete data',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        buildSignUpScreen(createTestUser()),
      );

      // Try to submit without filling any fields
      await tester.tap(find.text('Create Account'));
      await tester.pumpAndSettle();

      // Verify validation errors are shown
      expect(find.text('Email is required'), findsOneWidget);
      expect(find.text('First name is required'), findsOneWidget);
      expect(find.text('Last name is required'), findsOneWidget);
      expect(find.text('Phone number is required'), findsOneWidget);
      expect(find.text('Password is required'), findsOneWidget);
    });

    // ============================================================
    // Additional Tests
    // ============================================================
    testWidgets('Password visibility toggle works',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        buildSignUpScreen(createTestUser()),
      );

      // Password should be obscured initially
      expect(find.byIcon(Icons.visibility_off_outlined), findsNWidgets(2));

      // Tap visibility toggle for password field
      await tester.tap(find.byIcon(Icons.visibility_off_outlined).first);
      await tester.pumpAndSettle();

      // Password should now be visible
      expect(find.byIcon(Icons.visibility_outlined), findsOneWidget);
    });

    testWidgets('Password requirements update in real-time',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        buildSignUpScreen(createTestUser()),
      );

      // Initially all requirements should be unmet
      expect(find.byIcon(Icons.check_circle), findsNothing);

      // Enter strong password
      await tester.enterText(
        find.byType(TextFormField).at(4),
        'SecurePass123!',
      );
      await tester.pumpAndSettle();

      // All requirements should be met
      expect(find.byIcon(Icons.check_circle), findsNWidgets(5));
    });

    testWidgets('Password mismatch validation',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        buildSignUpScreen(createTestUser()),
      );

      // Enter password
      await tester.enterText(
        find.byType(TextFormField).at(4),
        'SecurePass123!',
      );
      // Enter different confirm password
      await tester.enterText(
        find.byType(TextFormField).at(5),
        'DifferentPass456!',
      );
      await tester.pumpAndSettle();

      // Try to submit
      await tester.tap(find.text('Create Account'));
      await tester.pumpAndSettle();

      // Verify mismatch error
      expect(find.text('Passwords do not match'), findsOneWidget);
    });

    testWidgets('Navigate to login screen',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        buildSignUpScreenWithRoutes(
          createTestUser(),
          {
            '/login': (context) => const Scaffold(body: Text('Login Screen')),
          },
        ),
      );

      // Tap login link
      await tester.tap(find.text('Login'));
      await tester.pumpAndSettle();

      // Verify navigation happened
      expect(find.text('Login Screen'), findsOneWidget);
    });

    testWidgets('All required fields are present',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        buildSignUpScreen(createTestUser()),
      );

      // Verify all required fields exist
      expect(find.text('Email'), findsOneWidget);
      expect(find.text('First Name'), findsOneWidget);
      expect(find.text('Last Name'), findsOneWidget);
      expect(find.text('Phone Number'), findsOneWidget);
      expect(find.text('Password'), findsOneWidget);
      expect(find.text('Confirm Password'), findsOneWidget);
      expect(find.text('Create Account'), findsOneWidget);
    });

    testWidgets('AppTextField widgets are used',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        buildSignUpScreen(createTestUser()),
      );

      // Verify AppTextField is used for all inputs
      expect(find.byType(TextFormField), findsNWidgets(6));
    });
  });
}
