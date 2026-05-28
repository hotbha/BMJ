# GROUP E — Order History Implementation Report

## Models Created

| Model | File | Fields |
|-------|------|--------|
| `OrderSummary` | `lush/lib/models/order_summary.dart` | id, date, items, total, currency, status, formattedDate, itemCount |
| `OrderDetail` | `lush/lib/models/order_detail.dart` | id, date, status, lineItems, subtotal, deliveryFee, total, currency, deliveryAddress |
| `OrderLineItem` | `lush/lib/models/order_line_item.dart` | itemId, itemName, quantity, unitPrice, lineTotal |

### Model Enhancements

| Model | Changes |
|-------|---------|
| `Address` (`views/models/address.dart`) | Added `fromJson()`, `toJson()`, `formatted` getter |

## Screens Created

| Screen | Route | Keys Added |
|--------|-------|------------|
| `order/order_history_screen.dart` | `/order-history` | order_history_appbar, order_history_refresh, order_history_loading, empty_order_history, order_history_browse_products, order_history_error, order_history_list, order_tile_{id} |
| `order/order_detail_screen.dart` | `/order-detail` | order_detail_appbar, order_status_card, order_items_card, order_pricing_card, order_address_card, reorder_button |

## BLoC Created

| Event | Emitter | Endpoint |
|-------|---------|----------|
| `LoadOrderHistory` → `OrderHistoryLoading` → `OrderHistoryLoaded` / `OrderHistoryEmpty` / `OrderHistoryError` | OrderBloc._onLoadOrderHistory | GET /api/orders |
| `RefreshOrderHistory` → same | OrderBloc._onRefreshOrderHistory | GET /api/orders |
| `LoadOrderDetail` → `OrderDetailLoading` → `OrderDetailLoaded` / `OrderDetailError` | OrderBloc._onLoadOrderDetail | GET /api/orders/{id} |

## CartBloc Event Added

| Event | Handler | Action |
|-------|---------|--------|
| `ReorderItems` | CartBloc._onReorderItems | Clears cart, adds items from order, emits CartLoaded |

## Routes Added

| Route | Screen | File |
|-------|--------|------|
| `/order-history` | `OrderHistoryScreen` | `main.dart` (static routes) |
| `/order-detail` | `OrderDetailScreen` | `main.dart` (onGenerateRoute) |

## bmjServer Endpoints

| Endpoint | Was | Now |
|----------|-----|-----|
| `GET /api/orders` | ✅ Exists (JWT required) | Already returns list of orders via OrderController |
| `GET /api/orders/{id}` | ✅ Exists (JWT required) | Already returns order details via OrderController |
| `POST /api/orders` | ✅ Exists | Already handles order placement (from O1) |

No backend changes needed — all required endpoints already exist.

## Tests

| Suite | File | Tests |
|-------|------|-------|
| BLoC unit tests | `test/bloc/order_history_test.dart` | 7 |
| Widget tests | `test/widget/order_history_widget_test.dart` | 6 |

### BLoC test coverage:
- LoadOrderHistory: success (→Loaded), empty (→Empty), error (→Error)
- LoadOrderDetail: success (→Loaded), failure (→Error)
- isClosed guard: returns true after close, events after close not emitted

### Widget test coverage:
- OrderHistoryScreen: loading indicator, empty state, loaded list
- OrderDetailScreen: loading indicator, all 4 cards visible, reorder button visible

## Remaining Items

| Item | Status | Note |
|------|--------|------|
| Navigation link in Dashboard drawer | 🔴 | Needs manual addition — dashboard.dart has "Order History" drawer item at line ~1080, route `/order-history` is already wired |
| Navigation link in Profile screen | 🔴 | Profile `my_account_page.dart` — "Order History" button uses route `/order-history` which is already registered |
| Navigation link in order confirmation | 🔴 | Not applicable yet — order confirmation screen uses Chargebee self-serve page |

## Flutter Analyze: 0 new errors (3 pre-existing)
## bmjServer: BUILD SUCCESS (no changes needed)