# Delivery Domain

> **Purpose:** Complete delivery domain reference — database schema, API endpoints, Flutter screens, and cart integration for BookMyJuice.

## Architecture

The delivery integration follows a three-layer approach:

1. **Repository Layer** (`UserRepository`) — API calls to backend endpoints
2. **Screen Layer** (StatefulWidget screens) — UI for address and slot selection
3. **Cart Integration** (`cart_screen.dart`) — Checkout flow with delivery validation

## Database Tables

### service_areas
Pincode-based serviceability configuration.

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT (PK) | Auto-increment primary key |
| pincode | VARCHAR(10) | Serviceable pincode (unique) |
| city | VARCHAR(100) | City name |
| state | VARCHAR(100) | State name |
| is_serviced | BOOLEAN | Whether this pincode is active for delivery |
| cutoff_time | TIME | Order cutoff time for same-day delivery |
| min_lead_hours | INT | Minimum lead time in hours |
| created_at | TIMESTAMP | Record creation timestamp |
| updated_at | TIMESTAMP | Record update timestamp |

### delivery_slots
Available delivery time windows for each service area.

The `delivery_slots` table provides granular time-window selection (pre-booking specific 2-hour delivery windows) for each service area. The table schema and APIs are fully operational for time-window based delivery scheduling.

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT (PK) | Auto-increment primary key |
| service_area_id | BIGINT (FK) | References service_areas.id |
| slot_date | DATE | Delivery date |
| start_time | TIME | Slot start time |
| end_time | TIME | Slot end time |
| max_orders | INT | Maximum orders allowed |
| current_orders | INT | Current booked orders |
| is_active | BOOLEAN | Whether the slot is active |
| created_at | TIMESTAMP | Record creation timestamp |
| updated_at | TIMESTAMP | Record update timestamp |

### user_addresses
Multi-address management for users.

The `user_addresses` table supports multiple delivery addresses per user. Users can add, edit, delete, and set default addresses. The "Add Address" button is always available for adding new addresses. Address is captured during signup as part of the registration flow.

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT (PK) | Auto-increment primary key |
| user_id | BIGINT (FK) | References users.id |
| label | VARCHAR(50) | Address label (Home, Work, Other) |
| full_name | VARCHAR(100) | Recipient full name |
| phone | VARCHAR(20) | Recipient phone number |
| address_line1 | VARCHAR(255) | Primary address |
| address_line2 | VARCHAR(255) | Secondary address (optional) |
| landmark | VARCHAR(255) | Nearby landmark (optional) |
| city | VARCHAR(100) | City |
| state | VARCHAR(100) | State |
| pincode | VARCHAR(10) | Pincode/ZIP |
| latitude | DECIMAL(10,8) | Latitude coordinate (optional) |
| longitude | DECIMAL(11,8) | Longitude coordinate (optional) |
| is_default | BOOLEAN | Whether this is the default address |
| delivery_instructions | TEXT | Special delivery instructions (optional) |
| created_at | TIMESTAMP | Record creation timestamp |
| updated_at | TIMESTAMP | Record update timestamp |

## Entities

- **ServiceAreaEntity** (service_areas) — Pincode serviceability configuration
- **DeliverySlotEntity** (delivery_slots) — Delivery time slot management
- **UserAddressEntity** (user_addresses) — User delivery addresses

## Repositories

| Repository | Methods |
|------------|---------|
| ServiceAreaRepository | findByPincode, findByCity, findByIsServicedTrue |
| DeliverySlotRepository | findByServiceAreaIdAndSlotDateAndIsActiveTrue, findByServiceAreaIdAndSlotDateBetweenAndIsActiveTrue, findBySlotDateAfterAndIsActiveTrue |
| UserAddressRepository | findByUserId, findByUserIdAndIsDefaultTrue, setDefaultFalseForUser (custom JPQL) |

## DTOs

- **AddressRequest** — Input DTO for creating/updating addresses
- **AddressResponse** — Output DTO with address data (includes fromEntity factory)
- **DeliverySlotResponse** — Output DTO with slot data including computed `available` field (available = currentOrders < maxOrders && isActive)

## API Endpoints

### Public Endpoints

#### Service Areas
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/delivery/service-areas?pincode= | Check serviceability by pincode (returns 404 if not found) |
| GET | /api/v1/delivery/service-areas/city/{city} | Find service areas by city |

#### Delivery Slots
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/delivery/slots?serviceAreaId=&date= | Get available slots for area on date (YYYY-MM-DD) |
| GET | /api/v1/delivery/slots/range?serviceAreaId=&startDate=&endDate= | Get slots for a date range |

### Authenticated Endpoints (USER/MODERATOR/ADMIN)

#### Addresses
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/delivery/addresses | Get current user addresses |
| POST | /api/v1/delivery/addresses | Add a new address |
| PUT | /api/v1/delivery/addresses/{id} | Update an existing address |
| DELETE | /api/v1/delivery/addresses/{id} | Delete an address |
| PATCH | /api/v1/delivery/addresses/{id}/default | Set address as default |

## Flutter API Methods (UserRepository)

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

## Relationships

```
service_areas 1---* delivery_slots
users 1---* user_addresses
```

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
- `_addresses` — List of address maps
- `_isLoading` — Loading state
- `_error` — Error message string

### DeliverySlotSelectionScreen (`/delivery-slot-selection`)

**File:** `lush/lib/views/screens/delivery_slot_selection_screen.dart`

A StatefulWidget implementing a two-step flow for delivery slot selection.

**Features:**

**Step 1 — Pincode Entry:**
- **FR-DEL-001**: Text field for 6-digit pincode entry with numeric keyboard
- "Check" button triggers `checkServiceability()` API call
- Validation: must be exactly 6 digits
- Loading spinner on button during check
- Success state: Green banner "Delivery Available!" with area name
- Error state: Red banner "Sorry, we do not deliver to this pincode yet."
- Custom error messages for API failures

**Step 2 — Slot Selection (shown after successful pincode check):**
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
| FR-DEL-001 | DeliverySlotSelectionScreen — Pincode check | ✅ Implemented |
| FR-DEL-002 | DeliverySlotSelectionScreen — Slot selection | ✅ Implemented |
| FR-DEL-003 | AddressSelectionScreen — View addresses | ✅ Implemented |
| FR-DEL-004 | AddressSelectionScreen + AddressEntryScreen — Add address | ✅ Implemented |
| FR-DEL-005 | AddressSelectionScreen — Set default | ✅ Implemented |
| FR-DEL-006 | AddressSelectionScreen — Delete address | ✅ Implemented |
| FR-DEL-007 | AddressSelectionScreen — Default badge/styling | ✅ Implemented |
| FR-DEL-008 | CartScreen — Delivery selection before checkout | ✅ Implemented |

## Bottle Cap & Limit Behavior

### Current Behavior (No Hard Cap)
| Property | Value |
|----------|-------|
| **Bottle cap** | No hard cap in current version. Users can accumulate bottles indefinitely. |
| **UI state when hypothetical cap exceeded** | N/A presently. If implemented in future, the cart screen's "Proceed to Checkout" button should be disabled with a warning toast: "You've reached the bottle return limit. Please return some bottles before ordering more." |
| **Enforcement point** | bmjServer at checkout time (enforced in `CartController` / `CheckoutController`), not in Flutter UI. |
| **Bottle tracking auto-dispatch** | On `INVOICE_PAID` webhook, `bottleTrackingService.autoDispatchBottles()` creates `bottle_transactions` entries. This is best-effort and non-blocking — order completes even if auto-dispatch fails. |

### Future Bottle Cap Implementation Plan
If a bottle cap is introduced later, the following changes would be needed:
1. **bmjServer**: Add a `bottle_cap` column to `service_areas` or a global config table
2. **Flutter**: Cart screen checks `GET /api/bottles/ledger` and compares against the cap
3. **UI**: Warning when approaching 80% of cap, block at or above 100%

## Testable Pincodes for QA

| Pincode | City | State | Serviceable | Cutoff Time | Min Lead Hours | Notes |
|---------|------|-------|-------------|-------------|----------------|-------|
| 400001 | Mumbai | Maharashtra | ✅ Yes | 18:00 IST | 4 | Default test pincode — use for all happy-path delivery tests |
| 110001 | New Delhi | Delhi | ✅ Yes | 16:00 IST | 6 | Capital city — test with different cutoff |
| 700001 | Kolkata | West Bengal | ✅ Yes | 15:00 IST | 6 | Eastern zone, different timezone offset |
| 600001 | Chennai | Tamil Nadu | ✅ Yes | 17:00 IST | 5 | Southern metro |
| 500001 | Hyderabad | Telangana | ✅ Yes | 17:00 IST | 5 | South-central metro |
| 560001 | Bangalore | Karnataka | ✅ Yes | 18:00 IST | 4 | Major tech hub — same cutoff as Mumbai |
| 380001 | Ahmedabad | Gujarat | ✅ Yes | 16:00 IST | 6 | Western metro |
| 226001 | Lucknow | Uttar Pradesh | ✅ Yes | 15:30 IST | 6 | Tier-2 city test |
| 302001 | Jaipur | Rajasthan | ✅ Yes | 16:00 IST | 6 | Tier-2 city test |
| 999999 | Nowhere | Testland | ❌ No | — | — | Invalid/unsupported pincode for negative testing |
| 123456 | — | — | ❌ No (not found) | — | — | Non-existent pincode (returns 404) |
| 000000 | — | — | ❌ No (invalid format) | — | — | Boundary test — all zeros |
| 99999 | — | — | ❌ No (too short) | — | — | 5-digit pincode (invalid format) |
| 1000000 | — | — | ❌ No (too long) | — | — | 7-digit pincode (invalid format) |

### Test Scenarios for Pincode Serviceability
1. **Happy path**: Enter 400001 → "Delivery Available!" with "Mumbai, Maharashtra" + slot selection shown
2. **Unserviced pincode**: Enter 999999 → "Sorry, we do not deliver to this pincode yet."
3. **Non-existent pincode**: Enter 123456 → 404 response → "Could not verify serviceability. Please try again."
4. **Invalid format (too short)**: Enter 99999 → Inline validation error before API call
5. **Invalid format (too long)**: Enter 1000000 → Inline validation error before API call
6. **Boundary (all zeros)**: Enter 000000 → API returns 404 → error state UI
7. **Empty field**: Leave pincode empty → "Check" button disabled until 6 digits entered
8. **Network error during check**: Turn off Wi-Fi → "Check" shows error state with retry button
9. **Server error (500)**: If backend is down → error state with "Something went wrong" + retry

## Lead Time Cutoffs Per Service Area

The `service_areas` table defines lead time requirements through two columns:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `cutoff_time` | TIME | Order cutoff time for same-day / next-period delivery | `18:00:00` = orders before 6 PM qualify for next scheduled delivery |
| `min_lead_hours` | INT | Minimum lead time in hours between order placement and earliest possible delivery | `4` = at least 4 hours needed |

### How Lead Time Affects Slot Availability

```
Current time: 14:30 IST
Cutoff: 18:00 IST
Min lead: 4 hours
─────────────────────────────────────
If user orders at 14:30:
  Today's slots: NOT available (need 4h lead = earliest at 18:30, but cutoff is 18:00)
  Tomorrow's morning slot (08:00-10:00): Available if > 4h away (14:30+4 = 18:30, next day 08:00 works)
  Tomorrow's afternoon slot (14:00-16:00): Available

If user orders at 10:00:
  Today's afternoon slot (14:00-16:00): Available (10:00+4h = 14:00, before cutoff 18:00)
  Today's evening slot (17:00-19:00): NOT fully available (10:00+4h=14:00, slot at 17:00 is 7h away, meets lead time but need to check if it's before cutoff)

If user orders at 19:00 (after cutoff):
  Tomorrow's slots: Available (it's next day for the system)
  Today's slots: ALL unavailable (past cutoff)
```

### Rule Summary
1. slot.start_time must be ≥ (current_time + min_lead_hours)
2. slot must be before or same as the cutoff_time of the service area's "same-day" definition
3. If current_time > cutoff_time of service area, only slots from tomorrow onwards are offered
4. slot.current_orders must be < slot.max_orders (available capacity)

## Error Handling
- All API calls wrapped in try-catch blocks
- Network errors shown via error state UI or SnackBars
- Backend validation errors (404, 400, 500) handled with specific messages
- Loading states with CircularProgressIndicator
- Empty states with appropriate messaging

## Security
- All authenticated endpoints use JWT Bearer token from `_secureStorage`
- Backend enforces `@PreAuthorize` for all address CRUD operations
