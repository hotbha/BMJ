# Data Models Map — Model-by-Model Field Analysis

> **Audit Date:** 2026-05-27  
> **Scope:** `lush/lib/views/models/*.dart` (all .dart files), `lush/lib/CartRepository/cart_repository.dart`  
> **Cross-Reference:** `chargebee_catalog.json`, `docs/API.md` (bottle tracking), `docs/architecture/ADR-*`  
> **Requested Reference Doc:** `docs/chargebee_final_state.md` — ⚠️ **PHANTOM-002: File does not exist in codebase.** Used `chargebee_catalog.json` (actual Chargebee catalog data) as fallback.

---

## ⚠️ Cleanup Required

| # | Severity | File | Issue |
|---|----------|------|-------|
| **FLAG-001** | 🟡 Medium | `contact.dart` | Getter `sendaccountEmail` (lowercase 'a') wraps field `sendAccountEmail` (capital 'A'). **Zero usages** of `sendaccount_email` or `send_account_email` found anywhere in codebase. |
| **FLAG-002** | 🔴 **HIGH** | `dynamic_item.dart` | `fromApiResponse()` reads **camelCase** JSON keys (`enabledInPortal`, `enabledForCheckout`, etc.) but Chargebee returns **snake_case** (`enabled_in_portal`, `enabled_for_checkout`). All camelCase fields silently default. Lines 136–182 effectively dead code for Chargebee data. |
| **FLAG-003** | 🔴 **HIGH** | `dynamic_item.dart` | Lines 150–154: `json['enabledInPortal'] as bool? ?? false` — the `as bool?` cast is dead code. Since the camelCase key never matches Chargebee's snake_case, the value is always `null` → `as bool?` returns `null` → `?? false` always fires. `as bool?` is a no-op. Same pattern lines 155–156, 167–170. |
| **FLAG-004** | 🟡 Medium | `contact.dart` | **No `fromJson()` / `toJson()` methods.** Model cannot be serialized or deserialized. |
| **FLAG-005** | 🟡 Medium | `address.dart` | Inconsistent getter naming conventions in single file: `getFirstName` (camelCase via `get`), `extendedaddr` (lowercase no prefix), `statecode` (lowercase). Three styles conflict. |
| **FLAG-006** | 🟡 Medium | `item.dart` | `Item.toJson()` mixes **snake_case** Chargebee keys (`enabled_for_checkout`, `item_family_id`) with **camelCase** JuiceItem keys (`imagePath`, `titleTxt`, `startColor`). If Chargebee sync reads item.toJson() output, snake_case fields are correct but camelCase JuiceItem fields won't match Chargebee's expectations. |
| **FLAG-007** | 🟡 Medium | `dynamic_juice.dart` | Has `toOldJuiceFormat()` (legacy) but **no standard `toJson()`**. Cannot serialize to current API format. |
| **FLAG-008** | 🔍 Low | `user.dart`, `signup_request.dart` | Both have `toJson()` → camelCase keys. **Neither has `fromJson()`.** ADR-004's user table SQL (`first_name`, `last_name`, `extended_addr`) uses snake_case — conflicting convention. |
| **FLAG-009** | 🟡 Medium | `item.dart` | **MISSING** Chargebee field: `metered` (boolean in Chargebee catalog). Has extra JuiceItem UI fields (`imagePath`, `titleTxt`, `startColor`, `endColor`, `meals`, `kacl`, `price`, `rating`, `servingSize`) that are presentation-layer, not Chargebee catalog. |
| **FLAG-010** | 🔍 Low | Docs Contradiction | **JWT lifetime mismatch:** ADR-004 §6 says "15 minutes (900000ms)", API.md §Token says "30 days (2592000000ms)". Code (`user_repository.dart` autoLogin) confirms **30 days** — ADR-004 is outdated/wrong. |
| **FLAG-011** | 🟡 Medium | `plan.dart` | **Empty file** (1 blank line, no code). Plan model is a skeleton/no-op. |
| **FLAG-012** | 🔴 **HIGH** | `chargebee_final_state.md` | **Reference doc does not exist.** User's requested cross-reference document is not in codebase. Used `chargebee_catalog.json` (1873 lines of actual Chargebee data) instead. |
| **FLAG-013** | 🟢 Info | `item.dart` — `ItemPrice` | `ItemPrice.fromJson()` handles **both** snake_case AND camelCase with `??` fallback: `json['accounting_category1'] ?? json['accountingCategory1'`. Most robust dual-format serialization in codebase. |
| **FLAG-014** | 🟡 Medium | `address.dart` | **No `fromJson()` / `toJson()` methods.** Cannot be serialized. |
| **FLAG-015** | 🔍 Low | `user.dart` | Has `roles` field (singular, `String`) initialized as `"user"` — but also has `role` field. Duplicate-like role fields (`role` + `roles`). |
| **FLAG-016** | 🔍 Low | `order.dart` | `fromJson()` reads camelCase keys (`documentNumber`, `paymentStatus`, `createdAt`) — consistent with other Flutter models but **the backend Java entity (`Order.java`) likely uses snake_case columns**. Check sync path. |

---

## Model-by-Model Field Tables

### 1. `contact.dart` — Contact

| Field (Dart) | Type | Case Style | Chargebee Key | fromJson | toJson | Status |
|---|---|---|---|---|---|---|
| `firstName` | `String` | camelCase | N/A (local only) | ❌ None | ❌ None | INCOMPLETE MODEL |
| `lastName` | `String` | camelCase | N/A | ❌ | ❌ | ⚠️ No serialization |
| `email` | `String` | camelCase | N/A | ❌ | ❌ | ⚠️ |
| `phone` | `String` | camelCase | N/A | ❌ | ❌ | ⚠️ |
| `enabled` | `bool` | camelCase | N/A | ❌ | ❌ | ⚠️ |
| `sendAccountEmail` | `bool` | camelCase | N/A | ❌ | ❌ | ⚠️ See FLAG-001 |
| `sendBillingEmail` | `bool` | camelCase | N/A | ❌ | ❌ | ⚠️ |

**Getter naming issues** (FLAG-005 variant):
- `get firstname` (lowercase) → wraps `firstName`
- `get lastname` (lowercase) → wraps `lastName`
- `get getEmail` → wraps `email` (redundant `get` prefix)
- `get getPhone` → wraps `phone` (redundant `get` prefix)
- `get sendaccountEmail` (lowercase 'a') → wraps `sendAccountEmail` (capital A)
- `get sendbillingEmail` (lowercase 'b') → wraps `sendBillingEmail` (capital B)

---

### 2. `dynamic_item.dart` — DynamicItem

| Field (Dart) | Type | Case Style | Chargebee Key | fromJson Key | toJson Key | Status |
|---|---|---|---|---|---|---|
| `itemID` | `String` | camelCase | `id` | `json['id']` 🟢 match | `'itemID'` | ⚠️ |
| `name` | `String` | camelCase | `name` | `json['name']` 🟢 | `'name'` | ✅ |
| `externalName` | `String` | camelCase | `external_name` | `json['externalName']` ❌ should be `external_name` | `'externalName'` | FLAG-002 |
| `description` | `String` | camelCase | `description` | `json['description']` 🟢 | `'description'` | ✅ |
| `imagePath` | `String` | camelCase | absent (metadata) | metadata extraction | `'imagePath'` | JuiceItem UI field |
| `startColor` | `String` | camelCase | absent (metadata) | metadata extraction | `'startColor'` | JuiceItem UI field |
| `endColor` | `String` | camelCase | absent (metadata) | metadata extraction | `'endColor'` | JuiceItem UI field |
| `meals` | `List<String>` | camelCase | absent | `json['ingredients']` fallback | `'meals'` | UI field |
| `kacl` | `int` | camelCase | absent | `json['calories']` fallback | `'kacl'` | UI field |
| `type` | `String` | camelCase | `type` | `json['type']` 🟢 | `'type'` | ✅ |
| `status` | `String` | camelCase | `status` | `json['status']` 🟢 | `'status'` | ✅ |
| `unit` | `String` | camelCase | `unit` | `json['unit']` 🟢 | `'unit'` | ✅ |
| `itemFamilyId` | `String` | camelCase | `item_family_id` | `json['itemFamilyId']` ❌ | `'itemFamilyId'` | FLAG-002 |
| `enabledInPortal` | `bool` | camelCase | `enabled_in_portal` | `json['enabledInPortal']` ❌ | `'enabledInPortal'` | **FLAG-002 🔴** |
| `enabledForCheckout` | `bool` | camelCase | `enabled_for_checkout` | `json['enabledForCheckout']` ❌ | `'enabledForCheckout'` | **FLAG-002 🔴** |
| `isGiftable` | `bool` | camelCase | `giftable` | `json['isGiftable']` ❌ | `'isGiftable'` | FLAG-002 + name mismatch |
| `isShippable` | `bool` | camelCase | `shippable` | `json['isShippable']` ❌ | `'isShippable'` | FLAG-002 + name mismatch |
| `deleted` | `bool` | camelCase | `deleted` | `json['deleted']` 🟢 | `'deleted'` | ✅ |
| `category` | `String` | camelCase | absent (metadata) | `json['category']` ❌ (Chargebee: absent) | `'category'` | Undocumented |
| `subcategory` | `String` | camelCase | absent (metadata) | `json['subcategory']` ❌ | `'subcategory'` | Undocumented |
| `benefits` | `List<String>` | camelCase | absent (metadata) | `json['benefits']` ❌ | `'benefits'` | Undocumented |
| `allergies` | `List<String>` | camelCase | absent (metadata) | `json['allergies']` ❌ | `'allergies'` | Undocumented |
| `tags` | `List<String>` | camelCase | absent (metadata) | `json['tags']` ❌ | `'tags'` | Undocumented |
| `servingSize` | `String` | camelCase | absent (metadata) | metadata fallback | `'servingSize'` | From metadata |
| `shelfLife` | `String` | camelCase | absent (metadata) | `json['shelfLife']` ❌ | `'shelfLife'` | FLAG-003 |
| `preparationTime` | `String` | camelCase | absent (metadata) | `json['preparationTime']` ❌ | `'preparationTime'` | FLAG-003 |
| `temperature` | `String` | camelCase | absent (metadata) | `json['temperature']` ❌ | `'temperature'` | FLAG-003 |
| `popularity` | `int` | camelCase | absent (metadata) | `json['popularity']` ❌ | `'popularity'` | FLAG-003 |
| `itemPrices` | `List<dynamic>` | camelCase | `item_prices` | `json['itemPrices']` ❌ | `'itemPrices'` | FLAG-002 |
| `metaData` | `Map<String, dynamic>` | camelCase | `metadata` | `json['metaData']` ❌ | `'metaData'` | FLAG-002 + name mismatch |

**Chargebee fields MISSING from DynamicItem:**
- `metered` (boolean in Chargebee catalog)
- `item_family_id` is processed but only via wrong key `itemFamilyId`
- `metadata` (Chargebee key) vs `metaData` (Dart field/method key)

---

### 3. `dynamic_juice.dart` — DynamicJuice

| Field (Dart) | Type | Case Style | Chargebee Key | fromApiResponse Key | toJson | Status |
|---|---|---|---|---|---|---|
| `juiceID` | `String` | camelCase | `id` | `json['id']` 🟢 | ❌ (only `toOldJuiceFormat`) | FLAG-007 |
| `name` | `String` | camelCase | `name` | `json['name']` 🟢 | ❌ | FLAG-007 |
| `externalName` | `String` | camelCase | `external_name` | `json['externalName']` ❌ (should be `external_name`) | ❌ | FLAG-002/007 |
| `description` | `String` | camelCase | `description` | `json['description']` 🟢 | ❌ | FLAG-007 |
| `imagePath` | `String` | camelCase | absent (metadata) | `metaData['imagePath']` | ❌ | From metadata |
| `startColor` | `String` | camelCase | absent (metadata) | `metaData['startColor']` | ❌ | From metadata |
| `endColor` | `String` | camelCase | absent (metadata) | `metaData['endColor']` | ❌ | From metadata |
| `meals` | `List<String>` | camelCase | absent | `metaData['meals']` | ❌ | From metadata |
| `kacl` | `int` | camelCase | absent | `metaData['calories']` | ❌ | From metadata |
| `type` | `String` | camelCase | `type` | `json['type']` 🟢 | ❌ | FLAG-007 |
| `status` | `String` | camelCase | `status` | `json['status']` 🟢 | ❌ | FLAG-007 |
| `unit` | `String` | camelCase | `unit` | `json['unit']` 🟢 | ❌ | FLAG-007 |
| `itemFamilyId` | `String` | camelCase | `item_family_id` | `json['itemFamilyId']` ❌ | ❌ | FLAG-002/007 |
| `enabledInPortal` | `bool` | camelCase | `enabled_in_portal` | `json['enabledInPortal']` ❌ | ❌ | FLAG-002/007 |
| `enabledForCheckout` | `bool` | camelCase | `enabled_for_checkout` | `json['enabledForCheckout']` ❌ | ❌ | FLAG-002/007 |
| `isGiftable` | `bool` | camelCase | `giftable` | `json['isGiftable']` ❌ name mismatch | ❌ | FLAG-002/007 |
| `isShippable` | `bool` | camelCase | `shippable` | `json['isShippable']` ❌ | ❌ | FLAG-002/007 |
| `deleted` | `bool` | camelCase | `deleted` | `json['deleted']` 🟢 | ❌ | FLAG-007 |
| `category` | `String` | camelCase | absent | `metaData['category']` | ❌ | From metadata |
| `subcategory` | `String` | camelCase | absent | `metaData['subcategory']` | ❌ | From metadata |
| `benefits` | `List<String>` | camelCase | absent | `metaData['benefits']` | ❌ | From metadata |
| `allergies` | `List<String>` | camelCase | absent | `metaData['allergies']` | ❌ | From metadata |
| `tags` | `List<String>` | camelCase | absent | `metaData['tags']` | ❌ | From metadata |
| `servingSize` | `String` | camelCase | absent | `metaData['servingSize']` | ❌ | From metadata |
| `shelfLife` | `String` | camelCase | absent | `metaData['shelfLife']` | ❌ | From metadata |
| `preparationTime` | `String` | camelCase | absent | `metaData['preparationTime']` | ❌ | From metadata |
| `temperature` | `String` | camelCase | absent | `metaData['temperature']` | ❌ | From metadata |
| `popularity` | `int` | camelCase | absent | `metaData['popularity']` | ❌ | From metadata |
| `seasonal` | `bool` | camelCase | absent | `metaData['seasonal']` | ❌ | Extra field |
| `nutritionalInfo` | `Map<String, dynamic>` | camelCase | absent | `metaData['nutritionalInfo']` | ❌ | Extra field |
| `customization` | `Map<String, dynamic>` | camelCase | absent | `metaData['customization']` | ❌ | Extra field |

**CRITICAL PATTERN:** DynamicJuice reads `json['metaData']` directly (line 71), NOT from metadata within the Chargebee response. The actual Chargebee metadata key is `metadata` (snake_case in `chargebee_catalog.json`). This means `metaData` extraction on line 71 always returns empty for Chargebee data → all metadata-dependent fields get defaults.

**Chargebee fields MISSING from DynamicJuice:**
- `metered` (absent from model, present in Chargebee catalog)
- `item_family_id` wrong key (`itemFamilyId` instead)
- `metadata` wrong key (`metaData` instead)

---

### 4. `item.dart` — Item

| Field (Dart) | Type | Case Style | Chargebee Key | fromJson Key | toJson Key | Status |
|---|---|---|---|---|---|---|
| `id` | `String?` | camelCase | `id` | `json['id']` 🟢 | `data['id']` | ✅ |
| `description` | `String?` | camelCase | `description` | `json['description']` 🟢 | `data['description']` | ✅ |
| `enabledForCheckout` | `bool?` | camelCase | `enabled_for_checkout` | `json['enabled_for_checkout']` 🟢 | `data['enabled_for_checkout']` | ✅ uses snake_case in JSON |
| `enabledInPortal` | `bool?` | camelCase | `enabled_in_portal` | `json['enabled_in_portal']` 🟢 | `data['enabled_in_portal']` | ✅ |
| `externalName` | `String?` | camelCase | `external_name` | `json['external_name']` 🟢 | `data['external_name']` | ✅ |
| `giftable` | `bool?` | camelCase | `giftable` | `json['giftable']` 🟢 | `data['giftable']` | ✅ |
| `itemFamilyId` | `String?` | camelCase | `item_family_id` | `json['item_family_id']` 🟢 | `data['item_family_id']` | ✅ |
| `jsonObject` | `String?` | camelCase | absent | `json['json_object']` | `data['json_object']` | Undocumented |
| `metaData` | `Map<String, dynamic>?` | camelCase | `metadata` | `json['meta_data']` 🟢 | `data['meta_data']` | ✅ JSON key matches Chargebee |
| `name` | `String?` | camelCase | `name` | `json['name']` 🟢 | `data['name']` | ✅ |
| `shippable` | `bool?` | camelCase | `shippable` | `json['shippable']` 🟢 | `data['shippable']` | ✅ |
| `status` | `String?` | camelCase | `status` | `json['status']` 🟢 | `data['status']` | ✅ |
| `type` | `String?` | camelCase | `type` | `json['type']` 🟢 | `data['type']` | ✅ |
| `unit` | `String?` | camelCase | `unit` | `json['unit']` 🟢 | `data['unit']` | ✅ |
| `subscriptionId` | `String?` | camelCase | absent | `json['subscription_id']` | `data['subscription_id']` | App-level, not Chargebee item |
| `archived` | `bool?` | camelCase | `archived` (CB: doesn't exist in catalog but API has it) | `json['archived']` 🟢 | `data['archived']` | ✅ |
| `deleted` | `bool?` | camelCase | `deleted` (CB: not in catalog JSON) | `json['deleted']` 🟢 | `data['deleted']` | ✅ |

**JuiceItem / UI Fields (NOT in Chargebee catalog):**

| Field (Dart) | Type | Case Style | fromJson Key | toJson Key | Status |
|---|---|---|---|---|---|
| `imagePath` | `String?` | camelCase | `json['imagePath']` | `data['imagePath']` | JuiceItem field (FLAG-006: camelCase in snake_case section) |
| `titleTxt` | `String?` | camelCase | `json['titleTxt']` | `data['titleTxt']` | JuiceItem field (FLAG-006) |
| `startColor` | `String?` | camelCase | `json['startColor']` | `data['startColor']` | JuiceItem field (FLAG-006) |
| `endColor` | `String?` | camelCase | `json['endColor']` | `data['endColor']` | JuiceItem field (FLAG-006) |
| `meals` | `List<String>?` | camelCase | `json['meals']` | `data['meals']` | JuiceItem field (FLAG-006) |
| `kacl` | `int?` | camelCase | `json['kacl']` | `data['kacl']` | JuiceItem field (FLAG-006) |
| `price` | `double?` | camelCase | `json['price']` | `data['price']` | JuiceItem field (FLAG-006) |
| `rating` | `double?` | camelCase | `json['rating']` | `data['rating']` | JuiceItem field (FLAG-006) |
| `servingSize` | `String` (non-null) | camelCase | `json['servingSize']` 🟢 | not in toJson | ⚠️ not serialized |

**MISSING from Item** (present in Chargebee catalog JSON):
- `metered` (`bool`, present in `chargebee_catalog.json` line 26: `"metered": false`) — **FLAG-009**

---

### 5. `item.dart` — ItemPrice

| Field (Dart) | Type | Case Style | Chargebee Key | fromJson (dual fallback) | toJson Key | Status |
|---|---|---|---|---|---|---|
| `id` | `String?` | camelCase | `id` | `json['id']` 🟢 | `data['id']` | ✅ |
| `accountingCategory1` | `String?` | camelCase | `accounting_category1` | `accounting_category1` ?? `accountingCategory1` 🟢 | `data['accounting_category1']` | **FLAG-013: Best practice** |
| `accountingCategory2` | `String?` | camelCase | `accounting_category2` | same fallback pattern 🟢 | snake_case | ✅ |
| `accountingCategory3` | `String?` | camelCase | `accounting_category3` | same 🟢 | snake_case | ✅ |
| `accountingCategory4` | `String?` | camelCase | `accounting_category4` | same 🟢 | snake_case | ✅ |
| `accountingCode` | `String?` | camelCase | `accounting_code` | `accounting_code` ?? `accountingCode` 🟢 | snake_case | ✅ |
| `createdAt` | `int?` | camelCase | `created_at` | `created_at` ?? `createdAt` 🟢 | snake_case | ✅ |
| `currencyCode` | `String?` | camelCase | `currency_code` | `currency_code` ?? `currencyCode` 🟢 | snake_case | ✅ |
| `description` | `String?` | camelCase | `description` | `json['description']` 🟢 | `data['description']` | ✅ |
| `externalName` | `String?` | camelCase | `external_name` | `external_name` ?? `externalName` 🟢 | snake_case | ✅ |
| `freeQuantityInDecimal` | `String?` | camelCase | `free_quantity_in_decimal` | fallback 🟢 | snake_case | ✅ |
| `invoiceNotes` | `String?` | camelCase | `invoice_notes` | fallback 🟢 | snake_case | ✅ |
| `metadata` | `Map<String, dynamic>?` | camelCase | `metadata` | `metadata` ?? `metaData` 🟢 | `data['metadata']` | ✅ |
| `name` | `String?` | camelCase | `name` | `json['name']` 🟢 | `data['name']` | ✅ |
| `period` | `int?` | camelCase | `period` | `json['period']` 🟢 | `data['period']` | ✅ |
| `periodUnit` | `String?` | camelCase | `period_unit` | fallback 🟢 | snake_case | ✅ |
| `price` | `double?` | camelCase | `price` | number parsing 🟢 | `data['price']` | ✅ |
| `pricingModel` | `String?` | camelCase | `pricing_model` | fallback 🟢 | snake_case | ✅ |
| `status` | `String?` | camelCase | `status` | `json['status']` 🟢 | `data['status']` | ✅ |
| `taxProfileId` | `String?` | camelCase | `tax_profile_id` | fallback 🟢 | snake_case | ✅ |
| `taxProfileName` | `String?` | camelCase | `tax_profile_name` | fallback 🟢 | snake_case | ✅ |
| `taxProfileType` | `String?` | camelCase | `tax_profile_type` | fallback 🟢 | snake_case | ✅ |
| `trialAvailable` | `bool?` | camelCase | `trial_available` | fallback 🟢 | snake_case | ✅ |
| `trialPeriod` | `int?` | camelCase | `trial_period` | fallback 🟢 | snake_case | ✅ |
| `trialPeriodUnit` | `String?` | camelCase | `trial_period_unit` | fallback 🟢 | snake_case | ✅ |
| `updatedAt` | `int?` | camelCase | `updated_at` | fallback 🟢 | snake_case | ✅ |
| `itemId` | `String?` | camelCase | `item_id` | fallback 🟢 | snake_case | ✅ |

**ItemPrice is the most robust model** in the codebase. Dual-format fromJson handles both snake_case (from Chargebee) and camelCase (from local cache/different API response). toJson() consistently uses snake_case for Chargebee compatibility.

---

### 6. `bottle_ledger.dart` — BottleLedgerEntry

| Field (Dart) | Type | Case Style | API.md Key | fromJson Key | toJson Key | Status |
|---|---|---|---|---|---|---|
| `customerId` | `String` | camelCase | `customerId` ✅ | `json['customerId']` 🟢 | `'customerId'` | ✅ Consistent |
| `bottleType` | `String` | camelCase | `bottleType` ✅ | `json['bottleType']` 🟢 | `'bottleType'` | ✅ |
| `totalIssued` | `int` | camelCase | `totalIssued` ✅ | `json['totalIssued']` 🟢 | `'totalIssued'` | ✅ |
| `totalReturned` | `int` | camelCase | `totalReturned` ✅ | `json['totalReturned']` 🟢 | `'totalReturned'` | ✅ |
| `totalBroken` | `int` | camelCase | `totalBroken` ✅ | `json['totalBroken']` 🟢 | `'totalBroken'` | ✅ |
| `outstanding` | `int` | camelCase | `outstanding` ✅ | `json['outstanding']` 🟢 | `'outstanding'` | ✅ |
| `lastTransactionAt` | `String?` | camelCase | `lastTransactionAt` ✅ | `json['lastTransactionAt']` 🟢 | `'lastTransactionAt'` | ✅ |

**BottleLedgerEntry fields match API.md exactly.** ✅ Consistent, well-aligned.

---

### 7. `bottle_ledger.dart` — BottleTransaction

| Field (Dart) | Type | Case Style | API.md Key | fromJson Key | toJson Key | Status |
|---|---|---|---|---|---|---|
| `id` | `int?` | camelCase | `id` ✅ | `json['id']` 🟢 | `'id'` | ✅ |
| `orderId` | `String` | camelCase | `orderId` ✅ | `json['orderId']` 🟢 | `'orderId'` | ✅ |
| `customerId` | `String` | camelCase | `customerId` ✅ | `json['customerId']` 🟢 | `'customerId'` | ✅ |
| `bottleType` | `String` | camelCase | `bottleType` ✅ | `json['bottleType']` 🟢 | `'bottleType'` | ✅ |
| `quantity` | `int` | camelCase | `quantity` ✅ | `json['quantity']` 🟢 | `'quantity'` | ✅ |
| `action` | `String` | camelCase | `action` ✅ | `json['action']` 🟢 | `'action'` | ✅ |
| `referenceId` | `String?` | camelCase | `referenceId` ✅ | `json['referenceId']` 🟢 | `'referenceId'` | ✅ |
| `notes` | `String?` | camelCase | `notes` ✅ | `json['notes']` 🟢 | `'notes'` | ✅ |
| `createdAt` | `String?` | camelCase | `createdAt` ✅ | `json['createdAt']` 🟢 | `'createdAt'` | ✅ |
| `updatedAt` | `String?` | camelCase | `updatedAt` ✅ | `json['updatedAt']` 🟢 | `'updatedAt'` | ✅ |

**BottleTransaction matches API.md exactly.** ✅ Well-aligned, consistent with backend.

---

### 8. `user.dart` — User

| Field (Dart) | Type | Case Style | ADR-004 SQL Column | toJson Key | fromJson | Status |
|---|---|---|---|---|---|---|
| `id` | `String` | camelCase | `id` 🟢 | `'id'` | ❌ None | ✅ |
| `email` | `String` | camelCase | `email` 🟢 | `'email'` | ❌ | ✅ |
| `phone` | `String` | camelCase | `phone` 🟢 | `'phone'` | ❌ | ✅ |
| `role` | `String` | camelCase | N/A | `'role'` | ❌ | ✅ |
| `firstName` | `String` | camelCase | `first_name` ❌ | `'firstName'` | ❌ | FLAG-008: SQL snake vs Dart camel |
| `lastName` | `String` | camelCase | `last_name` ❌ | `'lastName'` | ❌ | FLAG-008 |
| `password` | `String` | camelCase | `password` 🟢 | `'password'` | ❌ | ✅ |
| `address` | `String` | camelCase | `address` 🟢 | `'address'` | ❌ | ✅ |
| `extendedAddr` | `String` | camelCase | `extended_addr` ❌ | `'extendedAddr'` | ❌ | FLAG-008 |
| `extendedAddr2` | `String` | camelCase | `extended_addr2` ❌ | `'extendedAddr2'` | ❌ | FLAG-008 |
| `city` | `String` | camelCase | `city` 🟢 | `'city'` | ❌ | ✅ |
| `state` | `String` | camelCase | `state` 🟢 | `'state'` | ❌ | ✅ |
| `country` | `String` | camelCase | `country` 🟢 | `'country'` | ❌ | ✅ |
| `zip` | `String` | camelCase | `zip` 🟢 | `'zip'` | ❌ | ✅ |
| `roles` | `String` | camelCase | absent | not in toJson | ❌ | FLAG-015: duplicate-like role field |

**NOTE:** `roles` is initialized as `String roles = "user"` (line 46) while `role` is also a `String` (line 35). Only `role` is serialized in toJson(). The `roles` field appears to be a leftover/confusion.

---

### 9. `signup_request.dart` — SignupRequest

| Field (Dart) | Type | Case Style | ADR-004 Schema Key | toJson Key | fromJson | Status |
|---|---|---|---|---|---|---|
| `username` | `String` | camelCase | absent | `'username'` | ❌ | Extra field vs ADR-004 schema |
| `email` | `String` | camelCase | `email` 🟢 | `'email'` | ❌ | ✅ |
| `password` | `String` | camelCase | `password` 🟢 | `'password'` | ❌ | ✅ |
| `address` | `String` | camelCase | `address` 🟢 | `'address'` | ❌ | ✅ |
| `extendedAddr` | `String` | camelCase | `extendedAddr` 🟢 | `'extendedAddr'` | ❌ | ✅ (matches ADR camelCase schema) |
| `extendedAddr2` | `String` | camelCase | `extendedAddr2` 🟢 | `'extendedAddr2'` | ❌ | ✅ (matches ADR camelCase schema) |
| `firstName` | `String` | camelCase | `firstName` 🟢 | `'firstName'` | ❌ | ✅ |
| `lastName` | `String` | camelCase | `lastName` 🟢 | `'lastName'` | ❌ | ✅ |
| `city` | `String` | camelCase | `city` 🟢 | `'city'` | ❌ | ✅ |
| `state` | `String` | camelCase | `state` 🟢 | `'state'` | ❌ | ✅ |
| `country` | `String` | camelCase | `country` 🟢 | `'country'` | ❌ | ✅ |
| `zip` | `String` | camelCase | `zip` 🟢 | `'zip'` | ❌ | ✅ |
| `role` | `Set<String>` | camelCase | absent | `'role'` (toList()) | ❌ | Extra field |

**Pattern:** ADR-004's unified signup request JSON schema uses camelCase (matches SignupRequest.toJson()). But ADR-004's user table SQL uses snake_case (`first_name`, `extended_addr`). This means the backend must translate from camelCase API body to snake_case DB columns — which is standard Spring Boot JPA behavior (column names are snake_case, fields are camelCase).

---

### 10. `address.dart` — Address

| Field (Dart) | Type | Case Style | fromJson | toJson | Status |
|---|---|---|---|---|---|
| `firstName` | `String` | camelCase | ❌ None | ❌ None | INCOMPLETE MODEL |
| `lastName` | `String` | camelCase | ❌ | ❌ | ⚠️ |
| `phone` | `String` | camelCase | ❌ | ❌ | ⚠️ |
| `addr` | `String` | camelCase | ❌ | ❌ | ⚠️ |
| `extendedAddr` | `String` | camelCase | ❌ | ❌ | ⚠️ |
| `extendedAddr2` | `String` | camelCase | ❌ | ❌ | ⚠️ |
| `city` | `String` | camelCase | ❌ | ❌ | ⚠️ |
| `stateCode` | `String` | camelCase | ❌ | ❌ | ⚠️ |
| `zip` | `String` | camelCase | ❌ | ❌ | ⚠️ |
| `validationStatus` | `bool` | camelCase | ❌ | ❌ | ⚠️ |
| `subscriptionId` | `String` | camelCase | ❌ | ❌ | ⚠️ |

**Getter naming chaos** (FLAG-005):
- `get getFirstName` (camelCase with `get` prefix) → wraps `firstName`
- `get getLastName` → wraps `lastName`
- `get getPhone` → wraps `phone`
- `get getAddr` → wraps `addr`
- `get extendedaddr` (lowercase, no `get` prefix) → wraps `extendedAddr`
- `get extendedaddr2` (lowercase) → wraps `extendedAddr2`
- `get getCity` → wraps `city`
- `get statecode` (lowercase) → wraps `stateCode`
- `get getZip` → wraps `zip`
- `get validationstatus` (lowercase) → wraps `validationStatus`
- `get subscriptionid` (lowercase) → wraps `subscriptionId`

Three distinct naming conventions in 70 lines: `getXxx`, `xxx` (lowercase), and the field itself (`xxxYyy`).

---

### 11. `order.dart` — Order

| Field (Dart) | Type | Case Style | fromJson Key | Status |
|---|---|---|---|---|
| `id` | `String` | camelCase | `json['id']` 🟢 | ✅ |
| `documentNumber` | `String` | camelCase | `json['documentNumber']` | ⚠️ camelCase in fromJson |
| `status` | `String` | camelCase | `json['status']` 🟢 | ✅ |
| `createdAt` | `String` | camelCase | `json['createdAt']` | ⚠️ |
| `total` | `int` | camelCase | `json['total']` 🟢 | ✅ |
| `paymentStatus` | `String` | camelCase | `json['paymentStatus']` | ⚠️ |
| `items` | `List<String>` | camelCase | `json['orderLineItems']` (JSON string → parsed) | ⚠️ |

**NOTE:** Order.fromJson() reads camelCase keys (`documentNumber`, `paymentStatus`, `createdAt`, `orderLineItems`). If the backend Java entity stores these as snake_case columns (e.g., `document_number`, `payment_status`), the JSON response from `/api/orders` would need to map accordingly — either via `@JsonProperty` annotations in Java or manual mapping.

---

### 12. `cart.dart` — Cart

| Field (Dart) | Type | Case Style | fromJson | toJson | Status |
|---|---|---|---|---|---|
| `items` | `List<Item>` | camelCase | ❌ None | ❌ None | Simple runtime model, no serialization needed |

Cart is a simple container class with only `getTotalPrice()` and `getItemCount()` helper methods. No serialization.

---

### 13. `cart_item.dart` — CartItem

| Field (Dart) | Type | Case Style | fromJson | toJson | Status |
|---|---|---|---|---|---|
| `item` | `Item` | camelCase | via cart_repository | via cart_repository | Serialized by CartRepository |
| `quantity` | `int` | camelCase | via cart_repository | via cart_repository | ✅ handled externally |
| `selectedSize` | `String?` | camelCase | via cart_repository | via cart_repository | ✅ |
| `customizations` | `Map<String, dynamic>?` | camelCase | via cart_repository | via cart_repository | ✅ |
| `selectedPrice` | `ItemPrice?` | camelCase | via cart_repository | via cart_repository | ✅ |

No direct serialization in this file — all handled by `CartRepository._cartItemToJson()` and `CartRepository._cartItemFromJson()`.

---

### 14. `model.dart` — Product

| Field (Dart) | Type | Case Style | Notes |
|---|---|---|---|
| `name` | `String` | camelCase | Legacy demo data |
| `details` | `String` | camelCase | Legacy demo data |
| `price` | `String` | camelCase | Legacy demo data (String, not num) |
| `imgUrl` | `String` | camelCase | Legacy demo data |
| `likes` | `int` | camelCase | Legacy demo data |
| `bgColor` | `Color` | camelCase | Legacy demo data |
| `nameColor` | `Color` | camelCase | Legacy demo data |
| `liked` | `bool` | camelCase | Legacy demo data |

This is a legacy demo/product model, not related to Chargebee or current API. No serialization.

---

<!-- PHANTOM-001 REMOVED 2026-05-27: plan.dart section was here (empty file, no model). The entire section was a phantom — file has zero code, no fields to map. See FLAG-011 in the Cleanup Required table above. -->

---

## Bottle Tracking Cross-Reference

**Do any models reference bottle tracking fields?**

Model scan result: ❌ **No.** Only `bottle_ledger.dart` itself references bottle tracking fields:

- `BottleLedgerEntry`: customerId, bottleType, totalIssued, totalReturned, totalBroken, outstanding, lastTransactionAt
- `BottleTransaction`: id, orderId, customerId, bottleType, quantity, action, referenceId, notes, createdAt, updatedAt

**No other model** (Item, ItemPrice, DynamicItem, DynamicJuice, User, Order, Cart, CartItem, Address, Contact, SignupRequest) references bottle tracking fields. This is **correct** — bottle tracking is a separate domain.

**Consistency with API.md:**
- BottleLedgerEntry fields ✅ match API.md response (lines 1076–1082)
- BottleTransaction fields ✅ match API.md response (lines 1116–1128, 1163–1172, 1204–1214)
- All use camelCase keys consistently between model and API doc

---

## Chargebee Catalog Cross-Reference

> ⚠️ **DUPLICATE CONTENT COLLAPSED (2026-05-27):** The raw `chargebee_catalog.json` snippet that was here has been removed in favor of a single canonical reference. See `API.md` (lines 964–1048 for catalog field definitions) and the actual file `x:\BMJ\chargebee_catalog.json` (1873 lines) for full data.

`chargebee_catalog.json` contains 3 item families (delight, signature, premium). Full field mapping is in the table below.

**Fields present in both Chargebee catalog AND in at least one Dart model:**

| Chargebee Field | Item | DynamicItem | DynamicJuice | ✅ / ❌ |
|---|---|---|---|---|
| `id` | `id` ✅ | `itemID` ✅ | `juiceID` ✅ | 🟢 All |
| `name` | `name` ✅ | `name` ✅ | `name` ✅ | 🟢 All |
| `description` | `description` ✅ | `description` ✅ | `description` ✅ | 🟢 All |
| `type` | `type` ✅ | `type` ✅ | `type` ✅ | 🟢 All |
| `item_family_id` | `itemFamilyId` ✅ | `itemFamilyId` ❌ (wrong key) | `itemFamilyId` ❌ (wrong key) | 🟡 Item correct, others wrong |
| `metered` | ❌ **MISSING** | ❌ MISSING | ❌ MISSING | 🔴 **FLAG-009** |
| `metadata` | `metaData` ✅ (`meta_data` key) | `metaData` ❌ (wrong key) | `metaData` ❌ (wrong key) | 🟡 Item correct, others wrong |
| `status` | `status` 🟢 | `status` 🟢 | `status` 🟢 | 🟢 All |

**💥 CRITICAL FINDING:** `Item.fromJson()` correctly reads Chargebee snake_case keys (`item_family_id`, `external_name`, `enabled_for_checkout`), but `DynamicItem.fromApiResponse()` and `DynamicJuice.fromApiResponse()` read camelCase keys (`itemFamilyId`, `externalName`, `enabledForCheckout`) — **which do NOT exist in Chargebee JSON responses**. These two models will silently get default values for all their fields when processing Chargebee data.

---

## Doc Contradiction Scan

### DUPLICATE: Same shape in multiple docs

| Shape | Found In | Status |
|---|---|---|
| Bottle ledger response JSON | API.md lines 1071–1085, `bottle_ledger.dart` lines 24–34 | ✅ Consistent (camelCase in both) |
| Bottle transaction response JSON | API.md lines 1115–1128, `bottle_ledger.dart` lines 84–96 | ✅ Consistent |
| User schema | ADR-004 unified signup schema (camelCase), User.toJson() (camelCase), SignupRequest.toJson() (camelCase) | ✅ Consistent between Dart models and ADR schema. SQL in ADR-004 uses snake_case (expected JPA behavior). |
| Chargebee customer creation payload | ADR-004 §7 (camelCase `firstName`, `billingEmail`, etc.) | Matches Chargebee API conventions |

### CONTRADICTION: Field names differ between docs

| Contradiction | Source 1 | Source 2 | Verdict |
|---|---|---|---|
| **JWT expiration** 🔴 | ADR-004 §6: **15 minutes** (900000ms) | API.md §Token Lifecycle: **30 days** (2592000000ms) | **CONTRA-001** — Code confirms 30 days (`user_repository.dart` autoLogin checks JWT). ADR-004 is outdated/wrong. |
| `metadata` vs `metaData` | Chargebee catalog: `"metadata"` | All Dart models: `metaData` | Minor naming mismatch. fromJson key in `item.dart` correctly uses `meta_data`. |
| `giftable` field name | Chargebee: `giftable` | DynamicItem: `isGiftable` with fromJson key `'isGiftable'` | ⚠️ Name mismatch. `Item.dart` correctly uses `json['giftable']`. |

### PHANTOM: Model described in docs but absent from code

| Phantom | Description | Status |
|---|---|---|
| `plan.dart` | Described in ADR-003 as local cache table `plans` | **PHANTOM-001** — file exists but is empty (1 blank line). Plan model never implemented. |
| `chargebee_final_state.md` | Requested as cross-reference doc | **PHANTOM-002** — file does not exist. |
| Bottle tracking Java backend | Described in API.md §Bottle Tracking (4 endpoints) | Code exists in `bmjServer` but no corresponding Flutter BLoC/service for bottle tracking was found in the initial scan. |

---

## Summary Statistics

| Metric | Count |
|---|---|
| Total .dart model files in `models/` | 16 (including UI files, legacy, plus real models) |
| Real data models with serialization | 5 (Item, ItemPrice, BottleLedgerEntry, BottleTransaction, Order) |
| Models missing `fromJson()` | 6 (Contact, Address, User, SignupRequest, Cart, model.dart) |
| Models missing `toJson()` | 6+ (Contact, Address, Cart, model.dart, DynamicJuice, etc.) |
| Empty/skeleton model files | 1 (plan.dart) |
| 🔴 HIGH severity flags | 3 (FLAG-002, FLAG-003, FLAG-012) |
| 🟡 MEDIUM severity flags | 8 (FLAG-001, FLAG-004, FLAG-005, FLAG-006, FLAG-007, FLAG-009, FLAG-011, FLAG-014) |
| 🔍 LOW severity flags | 4 (FLAG-008, FLAG-010, FLAG-015, FLAG-016) |
| 🟢 Info flags | 1 (FLAG-013) |
| Doc contradictions | 1 (CONTRA-001: JWT lifetime) |
| Phantoms | 2 (PHANTOM-001: plan.dart empty; PHANTOM-002: chargebee_final_state.md missing) |

---

*Generated by automated data model audit. No .dart files were modified.*
