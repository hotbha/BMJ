# Post-Login Black Screen — Root Cause

> **Date:** 2026-11-04 · **Class:** functional defect (navigation), not rendering/material
> **Status:** root cause proven from code + logs; fix not yet applied.

## 1. Observed behaviour

After a successful phone-OTP login the app shows a **black screen** with no content, no error
and no crash. Reproduced on every attempt (3/3) on the Android 14 emulator, debug build.

Measured on the stuck frame: overall luminance **16.3**, body band **0.0** (pure black),
photo share **0 %**, widget-tree dump **~70 KB** (a healthy dashboard dumps ~690 KB).

It is not a theme problem: the same build renders Home, PDP, Cart and Subscription normally
right before login.

## 2. Reproduction steps

1. Launch the app signed out (dashboard, guest).
2. Open the drawer → **Sign in** → **Continue with Phone**.
3. Enter `9999999911`, tap **Send OTP**.
4. Read the dev OTP from the backend: `docker logs bmj-backend-local | Select-String "DEV.OTP"`
   (e.g. `[DEV] OTP for 9999999911: 145866`).
5. Type the OTP, tap **Verify**.
6. `AuthenticationSuccess` is emitted → **screen goes black and stays black**.

Identical result when the OTP screen is reached directly from `/login` or via the drawer.
Restarting the app returns to the signed-out dashboard, so the black state does not persist.

## 3. Relevant logs

App (`flutter :` tag):

```
15:13:12.454  📱 Sending OTP to: 9999999911
15:13:14.468  ✅ OTP sent successfully
15:16:14.594  BLoC Transition: ... event: PhoneOtpLogin(9999999911, 117792),
              nextState: AuthenticationInProgress()
15:16:15.609  BLoC Transition: ... nextState: AuthenticationSuccess(I…
15:24:22.675  │ Exception: Unauthorized: Please login again      ← tab blocs being disposed
15:24:22.775  OrderBloc → OrderHistoryError(...)
```

Backend (`bmj-backend-local`):

```
[DEV] OTP for 9999999911: 145866 (SMS not sent - check Fast2SMS config)
POST "/api/auth/login-otp"  → 200
```

No exceptions are thrown: nothing logs `EXCEPTION`, `RenderFlex overflow`, or a null check.
That is the signature of a navigation dead end, not a build failure.

## 4. Exact failing component

`lib/views/screens/login_page.dart` lines 89–101:

```dart
body: BlocListener<AuthenticationBloc, AuthenticationState>(
  listenWhen: (previous, current) =>
      current is AuthenticationSuccess || ... ,
  listener: (context, state) async {
    if (state is AuthenticationSuccess) {
      _dialogShown = true;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        Navigator.of(context).pop();          // ← unconditional pop
      });
      return;
    }
```

`lib/views/screens/phone_otp_verification_screen.dart` lines 111–121:

```dart
void _onAuthState(AuthenticationState state) {
  if (state is AuthenticationSuccess) {
    ...
    Navigator.pushNamedAndRemoveUntil(context, '/dashboard', (route) => false);
    return;
  }
```

## 5. Root cause

**Two independent listeners handle the same `AuthenticationSuccess`, and the login page pops a
route it no longer owns.**

Sequence during a phone-OTP login:

| # | Stack (top → bottom) | Who acts |
| :-: | :--- | :--- |
| 1 | `/phone-otp-verification` → `/login` → dashboard | user taps Verify |
| 2 | same | `PhoneOtpVerificationScreen` listener → `pushNamedAndRemoveUntil('/dashboard', false)` ⇒ **stack becomes `/dashboard` only** |
| 3 | `/dashboard` | `LoginPage`'s listener (still mounted in the same frame, because its route was removed but the widget's `BlocListener` had already scheduled a post-frame callback) fires → `Navigator.pop()` ⇒ **pops `/dashboard`** |
| 4 | *empty* | Navigator has no routes left → **black screen** |

The `pop()` in `LoginPage` was written for the **Google** sign-in path, where the login page is
itself the top route and popping it reveals the dashboard that `AuthWrapper` (in `main.dart`)
has already swapped underneath. It is correct only in that one case; in the phone flow the OTP
screen has already replaced the whole stack, so the same pop destroys the destination.

The disappearing trees, the `Unauthorized` lines from the Orders tab and the successful API
calls are all consequences: the dashboard's blocs are created, then torn down as the route is
popped, while their in-flight requests are still returning.

## 6. Confidence

**High (≈95 %).** The failure is deterministic and the two listeners provably both run for one
event; the observed black page is exactly what an empty `Navigator` renders. Remaining 5 % is
the small chance the post-frame callback is cancelled by disposal in some builds — which would
only make the defect intermittent, not different.

## 7. Smallest possible fix (to be applied)

Guard the pop so it only happens when the login page is genuinely the route on top:

```dart
if (state is AuthenticationSuccess) {
  _dialogShown = true;
  final ModalRoute<dynamic>? route = ModalRoute.of(context);
  if (route?.isCurrent ?? false) {          // Google flow: login is on top
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Navigator.of(context).pop();
    });
  }
  return;
}
```

During the phone flow the login route is not current (the OTP screen is on top), so the pop is
skipped and `pushNamedAndRemoveUntil('/dashboard')` survives. No refactors, no style changes,
no new routes.

## 8. Secondary defect noticed while diagnosing (separate ticket)

`AutoLogIn` fails on restart:

```
15:20:43.020  event: AutoLogIn(), nextState: AuthenticationInProgress()
15:20:45.642  event: AutoLogIn(), nextState: AutoLoginFailed(AutoLogin Failed!…)
```

So either the JWT is not persisted by the login path, or `GET /api/auth/autologin` rejects it.
To be investigated **after** the black screen is fixed, because it is a different failure
(persistence/refresh) and does not cause the black screen.
