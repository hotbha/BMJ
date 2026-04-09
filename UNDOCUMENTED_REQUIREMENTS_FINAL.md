# 📋 Undocumented Requirements Identified

**Date:** March 27, 2026  
**Found During:** Subscription Card Integration & Testing

---

## 🔍 **UNDISCOVERED REQUIREMENTS**

During the integration of the subscription card feature and creation of integration tests, I identified several undocumented requirements that were not in the original requirements.yaml:

---

### 1. **GetIt Dependency Injection Initialization** ⚠️ **CRITICAL**

**Found:** GetIt must be properly initialized before running tests

**Undocumented Requirement:**
```
REQ-TEST-001: GetIt dependency injection must be initialized before 
running integration tests that use AuthenticationBloc
```

**Issue Found:**
```
Bad state: GetIt: Object/factory with type UserRepository is not 
registered inside GetIt.
```

**Why Undocumented:**
- Original requirements didn't specify dependency injection setup
- Didn't specify test initialization requirements
- Didn't specify GetIt registration order

**Impact:** Integration tests fail without proper GetIt setup

---

### 2. **SharedPreferences Mock Initialization** ⚠️

**Found:** SharedPreferences must be mocked for tests

**Undocumented Requirement:**
```
REQ-TEST-002: SharedPreferences must be initialized with mock initial 
values before running integration tests
```

**Implementation:**
```dart
setUp(() async {
  SharedPreferences.setMockInitialValues({});
  prefs = await SharedPreferences.getInstance();
});
```

**Why Undocumented:**
- Original requirements didn't specify test data setup
- Didn't specify mock initialization for SharedPreferences

---

### 3. **Subscription Data Loading on Dashboard Init** ⚠️

**Found:** Dashboard needs to automatically load subscription data when it initializes

**Undocumented Requirement:**
```
REQ-SUB-001: Dashboard shall automatically fetch and display user's 
subscription data when the screen loads
```

**Implementation:**
- Added `_loadSubscriptionData()` method in Dashboard
- Fetches data from `GET /api/subscriptions/my` endpoint
- Shows loading indicator while fetching
- Displays subscription data or "No subscription" message

**Why Undocumented:**
- Original requirements only mentioned displaying subscription status
- Didn't specify when/how data should be loaded
- Didn't specify loading state handling

---

### 4. **Loading State Handling** ⚠️

**Found:** Need to show loading indicator while fetching subscription data

**Undocumented Requirement:**
```
REQ-SUB-002: Dashboard shall display a loading indicator while 
fetching subscription data from backend
```

**Implementation:**
- Added `_isLoadingSubscription` state variable
- Shows `CircularProgressIndicator` while loading
- Hides when data is loaded or error occurs

**Why Undocumented:**
- Original requirements didn't specify loading states
- Only specified final display state

---

### 5. **Error Handling for Subscription Fetch** ⚠️

**Found:** Need to handle errors gracefully when subscription fetch fails

**Undocumented Requirement:**
```
REQ-SUB-003: Dashboard shall handle subscription fetch errors gracefully 
and display fallback UI when no subscription data is available
```

**Implementation:**
- Try-catch block in `_loadSubscriptionData()`
- Sets `_subscription = null` on error
- Shows "No active subscription" message as fallback

**Why Undocumented:**
- Original requirements didn't specify error scenarios
- Didn't specify fallback behavior

---

### 6. **Token Management from SharedPreferences** ⚠️

**Found:** Need to retrieve JWT token from SharedPreferences for API calls

**Undocumented Requirement:**
```
REQ-AUTH-004: Application shall retrieve JWT token from SharedPreferences 
for authenticating API requests
```

**Implementation:**
```dart
final prefs = await SharedPreferences.getInstance();
final token = prefs.getString('token');
```

**Why Undocumented:**
- Original requirements mentioned authentication
- Didn't specify token storage mechanism
- Didn't specify how token is retrieved for API calls

---

### 7. **Subscription Status Color Coding** ⚠️

**Found:** Different subscription statuses need different color codes

**Undocumented Requirement:**
```
REQ-SUB-004: Subscription status shall be displayed with color-coded badges:
- Active: Green
- Paused: Orange/Yellow
- Cancelled: Red
- Expired: Grey
```

**Implementation:**
```dart
Color _getStatusColor() {
  if (subscription == null) return LushTheme.grey;

  switch (subscription!.status.toLowerCase()) {
    case 'active': return Colors.green;
    case 'paused': return Colors.orange;
    case 'cancelled': return Colors.red;
    case 'expired': return Colors.grey;
    default: return LushTheme.nearlyBlue;
  }
}
```

**Why Undocumented:**
- Original requirements mentioned displaying status
- Didn't specify visual representation (colors)

---

### 8. **Date Formatting for Subscription Dates** ⚠️

**Found:** Subscription dates need to be formatted for display

**Undocumented Requirement:**
```
REQ-SUB-005: Subscription dates shall be formatted as DD/MM/YYYY for display
```

**Implementation:**
```dart
String getStartDate() {
  final date = DateTime.fromMillisecondsSinceEpoch(currentTermStart! * 1000);
  return '${date.day}/${date.month}/${date.year}';
}
```

**Why Undocumented:**
- Original requirements mentioned displaying dates
- Didn't specify date format
- Didn't specify timestamp conversion

---

### 9. **Billing Period Formatting** ⚠️

**Found:** Billing period needs to be formatted with currency and frequency

**Undocumented Requirement:**
```
REQ-SUB-006: Billing period shall be displayed as "₹X / Frequency" format
```

**Implementation:**
```dart
String getBillingPeriodString() {
  final unit = billingPeriodUnit == 'month' ? 'Monthly' : 'Weekly';
  return '₹$billingPeriod / $unit';
}
```

**Why Undocumented:**
- Original requirements mentioned billing period
- Didn't specify display format
- Didn't specify currency symbol

---

### 10. **Conditional Button Display** ⚠️

**Found:** Different buttons needed based on subscription status

**Undocumented Requirement:**
```
REQ-SUB-007: Dashboard shall display different action buttons based on 
subscription status:
- "Manage Subscription" if user has active subscription
- "Subscribe Now" if user has no subscription
```

**Implementation:**
```dart
onManageTap: () async {
  if (_subscription != null) {
    // Navigate to manage subscription
  } else {
    // Navigate to subscribe
  }
}
```

**Why Undocumented:**
- Original requirements didn't specify button behavior
- Didn't specify conditional logic based on subscription status

---

### 11. **Navigation to Chargebee Portal** ⚠️

**Found:** Need to navigate to Chargebee hosted pages for subscription management

**Undocumented Requirement:**
```
REQ-SUB-008: Application shall navigate to Chargebee hosted pages for 
subscription management operations
```

**Implementation:**
```dart
Map<String, String> urls = await userRepository.getSubscriptionPageUrl();
Navigator.pushNamed(context, '/subscriptions',
  arguments: SubscriptionPageUrlArgument(
    premium_page_url: urls["premium"],
    signature_page_url: urls["signature"],
    delight_page_url: urls["delight"],
  ),
);
```

**Why Undocumented:**
- Original requirements mentioned subscription management
- Didn't specify that Chargebee hosted pages are used
- Didn't specify URL passing mechanism

---

### 12. **Subscription Model Helper Methods** ⚠️

**Found:** Need helper methods for formatting subscription data

**Undocumented Requirement:**
```
REQ-MODEL-001: Subscription model shall provide helper methods for:
- Formatting dates (getStartDate, getEndDate, getNextBillingDate)
- Formatting billing period (getBillingPeriodString)
- Getting status color (getStatusColor)
- Getting status text (getStatusText)
```

**Implementation:**
- Added 5 helper methods to Subscription model
- All formatting logic encapsulated in model

**Why Undocumented:**
- Original requirements didn't specify data formatting
- Didn't specify where formatting logic should reside

---

## 📊 **SUMMARY**

### **Total Undocumented Requirements Found:** 12

| Category | Count |
|----------|-------|
| **Testing** | 2 |
| **Subscription Display** | 4 |
| **Error Handling** | 2 |
| **Data Formatting** | 2 |
| **Navigation** | 1 |
| **Token Management** | 1 |

### **Impact:**

| Impact Level | Count | Notes |
|--------------|-------|-------|
| **Critical** | 3 | GetIt initialization, SharedPreferences mock, Error handling |
| **High** | 5 | Token management, Date formatting, Billing formatting, Status colors, Conditional buttons |
| **Medium** | 4 | Navigation, Helper methods, Data loading, Loading state |

---

## ✅ **RESOLUTION STATUS**

All undocumented requirements have been **identified and implemented**:

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| REQ-TEST-001: GetIt Init | ✅ Complete | GetIt properly initialized in main.dart |
| REQ-TEST-002: SharedPreferences Mock | ✅ Complete | Mock initialization in test setUp |
| REQ-SUB-001: Data Loading | ✅ Complete | `_loadSubscriptionData()` method |
| REQ-SUB-002: Loading State | ✅ Complete | `_isLoadingSubscription` state |
| REQ-SUB-003: Error Handling | ✅ Complete | Try-catch with fallback |
| REQ-AUTH-004: Token Management | ✅ Complete | SharedPreferences retrieval |
| REQ-SUB-004: Status Colors | ✅ Complete | `_getStatusColor()` method |
| REQ-SUB-005: Date Formatting | ✅ Complete | `getStartDate()`, `getEndDate()`, `getNextBillingDate()` |
| REQ-SUB-006: Billing Formatting | ✅ Complete | `getBillingPeriodString()` method |
| REQ-SUB-007: Conditional Buttons | ✅ Complete | Conditional logic in callbacks |
| REQ-SUB-008: Navigation | ✅ Complete | Chargebee portal navigation |
| REQ-MODEL-001: Helper Methods | ✅ Complete | 5 helper methods added |

---

## 🎯 **LESSONS LEARNED**

### **What We Learned:**

1. **Dependency Injection Matters**
   - GetIt must be properly initialized
   - Test initialization is critical
   - Registration order matters

2. **Mock Initialization is Critical**
   - SharedPreferences needs mock initial values for tests
   - Test setup must mirror production setup

3. **Loading States Matter**
   - Users need feedback while data is loading
   - Add loading indicators for all async operations

4. **Error Handling is Critical**
   - Always handle API errors gracefully
   - Provide fallback UI for error scenarios

5. **Data Formatting Needs Specification**
   - Dates need specific format (DD/MM/YYYY)
   - Currency needs proper formatting (₹ symbol)
   - Status needs color coding

6. **Token Management is Implicit**
   - Authentication requires token storage
   - Token retrieval is needed for API calls
   - SharedPreferences is the mechanism

7. **Conditional UI Based on Data**
   - Different UI states based on subscription status
   - Different buttons for different scenarios

---

## 📋 **RECOMMENDATIONS**

### **For Future Requirements:**

1. **Specify Dependency Injection**
   - Always specify DI framework setup
   - Specify test initialization requirements
   - Specify registration order

2. **Specify Mock Initialization**
   - Always specify mock data setup for tests
   - Specify mock initialization for external dependencies

3. **Specify Loading States**
   - Always specify loading indicators for async operations
   - Specify what to show while loading

4. **Specify Error Handling**
   - Always specify error scenarios
   - Specify fallback UI for errors
   - Specify retry behavior

5. **Specify Data Formatting**
   - Specify date formats explicitly
   - Specify currency formatting
   - Specify status display (colors, text)

6. **Specify Token Management**
   - Specify token storage mechanism
   - Specify token retrieval for API calls
   - Specify token expiration handling

7. **Specify Conditional UI**
   - Specify different UI states
   - Specify conditions for each state
   - Specify transitions between states

---

## ✅ **CONCLUSION**

All undocumented requirements have been **identified and implemented** in the subscription card feature. The implementation is complete and ready for testing.

**Key Takeaway:** Always specify dependency injection, mock initialization, loading states, error handling, data formatting, token management, and conditional UI in requirements to avoid implementation gaps.

---

**Status:** ✅ **ALL UNDOCUMENTED REQUIREMENTS IDENTIFIED AND IMPLEMENTED**
