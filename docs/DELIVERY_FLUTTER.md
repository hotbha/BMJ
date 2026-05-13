# Flutter Delivery Integration

## Overview
This document describes the Flutter-side delivery domain implementation for BookMyJuice. It covers the screens, API methods, and cart integration that enable users to select delivery addresses and time slots during checkout.

## Architecture
The delivery integration follows a three-layer approach:

1. **Repository Layer** (`UserRepository`) - API calls to backend endpoints
2. **Screen Layer** (StatefulWidget screens) - UI for address and slot selection
3. **Cart Integration** (`cart_screen.dart`) - Checkout flow with delivery validation

## API Methods (UserRepository)

All delivery API methods are defined in `lush/lib/UserRepository/user_repository.dart` (lines 1274-1488).

### Service Area Methods

| Method | API Endpoint | Description |
|--------|-------------|-------------|
| `checkServiceability(String pincode)` | `GET /api/v1/delivery/service-areas?pincode=` | Check if a pincode is serviceable |

### Slot Methods

| Method | API Endpoint | Description |
|--------|-------------|-------------|
| `getAvailableSlots(int serviceAreaId, String date)` | `GET /api/v1/delivery/slots?serviceAreaId=&date=` | Get available slots for a service area on a date (YYYY-MM-DD) |

### Address Methods

| Method | API Endpoint | Description |
|--------|-------------|-------------|
| `getUserAddresses()` | `GET /api/v1/delivery/addresses` | Get all addresses for logged-in user |
| `addUserAddress(Map<String, dynamic>)` | `POST /api/v1/delivery/addresses` | Add a new delivery address |
| `updateUserAddress(int id, Map)` | `PUT /api/v1/delivery/addresses/{id}` | Update an existing address |
| `deleteUserAddress(int id)` | `DELETE /api/v1/delivery/addresses/{id}` | Delete a delivery address |
| `setDefaultAddress(int id)` | `PATCH /api/v1/delivery/addresses/{id}/default` | Set an address as default |

All methods follow the existing `UserRepository` pattern:
- `ioc.badCertificateCallback` for self-signed SSL certificates
- `IOClient(ioc)` for HTTP client
- Auth token from `_secureStorage.getAuthToken()`
- JSON encode/decode for request/response
- Returns `Map<String, dynamic>` with `status`/`data` fields

## Screens

### AddressSelectionScreen (`/address-selection`)

**File:** `lush/lib/views/screens/address_selection_screen.dart`

A StatefulWidget that displays saved delivery addresses for the logged-in user.

**Features:**
- **FR-DEL-003**: Lists all saved addresses with full details (name, address lines, city, state, pincode, phone)
- **FR-DEL-004**: FAB button navigates to `/address-entry` to add a new address
- **FR-DEL-005**: PopupMenu option to set address as default (star icon)
- **FR-DEL-006**: PopupMenu option to delete address with confirmation dialog
- **FR-DEL-007**: Default address highlighted with orange border and "DEFAULT" badge
- Address label badges (Home/Work/Other) displayed in orange
- Pull-to-refresh via `RefreshIndicator`
- Loading spinner during data fetch
- Error state with retry button
- Empty state with icon and message
- Selecting an address returns it via `Navigator.pop(context, address)`
- Haptic feedback on all interactions

**State Management:**
- `_addresses` - List of address maps
- `_isLoading` - Loading state
- `_error` - Error message string

### DeliverySlotSelectionScreen (`/delivery-slot-selection`)

**File:** `lush/lib/views/screens/delivery_slot_selection_screen.dart`

A StatefulWidget implementing a two-step flow for delivery slot selection.

**Features:**

**Step 1 - Pincode Entry:**
- **FR-DEL-001**: Text field for 6-digit pincode entry with numeric keyboard
- "Check" button triggers `checkServiceability()` API call
- Validation: must be exactly 6 digits
- Loading spinner on button during check
- Success state: Green banner "Delivery Available!" with area name
- Error state: Red banner "Sorry, we do not deliver to this pincode yet."
- Custom error messages for API failures

**Step 2 - Slot Selection (shown after successful pincode check):**
- **FR-DEL-002**: Date navigation with left/right chevron arrows
- Shows selected date in `dd/MM/yyyy` format
- Cannot go before today's date
- Slot cards with:
  - Time range (e.g., "10:00 - 12:00")
  - Remaining capacity ("X slots remaining")
  - Green check icon for available, red cancel for fully booked
  - Disabled state for unavailable slots
- Success/error/empty states for slots
- Retry button on slot load failure
- Selecting a returns `{ slot, serviceAreaId }` via `Navigator.pop`
- Haptic feedback on all interactions

## Cart Integration

**File:** `lush/lib/views/screens/cart_screen.dart`

The cart screen was converted from `StatelessWidget` to `StatefulWidget` to manage delivery selection state.

**FR-DEL-008: Delivery Selection in Checkout**

### State
```dart
Map<String, dynamic>? _selectedAddress;
Map<String, dynamic>? _selectedSlot;
```

### UI Components
1. **Delivery Address Card** (top of checkout section):
   - InkWell that navigates to `/address-selection`
   - Shows selected address details (line1, city, state, pincode)
   - Green border and check icon when selected
   - Orange icon and dashed border when unselected

2. **Delivery Slot Card** (below address card):
   - InkWell that navigates to `/delivery-slot-selection`
   - Shows selected slot time range
   - Same visual pattern as address card

3. **Checkout Validation:**
   - Before proceeding to payment, validates both address and slot are selected
   - Shows error SnackBars if either is missing:
     - "Please select a delivery address"
     - "Please select a delivery slot"
   - Only proceeds to `/checkout` when both are selected

### Navigation
```dart
Navigator.pushNamed(context, '/address-selection');
Navigator.pushNamed(context, '/delivery-slot-selection');
```

### Route Registration
Routes are registered in `lush/lib/main.dart` via `onGenerateRoute`:

```dart
} else if (settings.name == '/address-selection') {
  return MaterialPageRoute(
    builder: (_) => const AddressSelectionScreen(),
  );
} else if (settings.name == '/delivery-slot-selection') {
  return MaterialPageRoute(
    builder: (_) => const DeliverySlotSelectionScreen(),
  );
}
```

## Requirements Coverage

| Requirement | Component | Status |
|-------------|-----------|--------|
| FR-DEL-001 | DeliverySlotSelectionScreen - Pincode check | ✅ Implemented |
| FR-DEL-002 | DeliverySlotSelectionScreen - Slot selection | ✅ Implemented |
| FR-DEL-003 | AddressSelectionScreen - View addresses | ✅ Implemented |
| FR-DEL-004 | AddressSelectionScreen + AddressEntryScreen - Add address | ✅ Implemented |
| FR-DEL-005 | AddressSelectionScreen - Set default | ✅ Implemented |
| FR-DEL-006 | AddressSelectionScreen - Delete address | ✅ Implemented |
| FR-DEL-007 | AddressSelectionScreen - Default badge/styling | ✅ Implemented |
| FR-DEL-008 | CartScreen - Delivery selection before checkout | ✅ Implemented |

## Error Handling
- All API calls wrapped in try-catch blocks
- Network errors shown via error state UI or SnackBars
- Backend validation errors (404, 400, 500) handled with specific messages
- Loading states with CircularProgressIndicator
- Empty states with appropriate messaging

## Security
- All authenticated endpoints use JWT Bearer token from `_secureStorage`
- Backend enforces `@PreAuthorize` for all address CRUD operations
- Ownership verification on address update/delete (backend)
