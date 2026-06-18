# Chargebee MCP Integration Reference

> **Site:** bookmyjuice-test (TEST environment)  
> **Updated:** 2026-06-08  
> **Purpose:** Quick reference for interacting with Chargebee MCP agents

---

## 1. Overview

Two MCP agents provide programmatic access to Chargebee:

| Agent | URL | Auth Token (Bearer) | Capability |
|-------|-----|---------------------|------------|
| **Onboarding Agent** | `https://bookmyjuice-test.mcp.chargebee.com/onboarding_agent` | `test_ai_-ZFEjZ3qiK2mW3k7C9M2Q60OK2QmLslRdSnNWt61z4E` | **DESTRUCTIVE** — Create/import product catalog, customers, subscriptions, quotes, features, entitlements |
| **Data Lookup Agent** | `https://bookmyjuice-test.mcp.chargebee.com/data_lookup_agent` | `test_ai_WvyPvGTh7AKfZ6vM6UHOrWZduN1xKiU1Ir_MxccF3-Q` | **READ-ONLY** — Search plans, addons, items, prices, customers, subscriptions, invoices, transactions, events, quotes, credit notes |

> ⚠️ **NEVER use the Onboarding Agent for read/lookup operations.**
> ⚠️ **NEVER create/import anything in Chargebee without explicit user permission.**

---

## 2. Protocol

Both agents use **JSON-RPC 2.0** over HTTP with **Server-Sent Events (SSE)**.

| Property | Value |
|----------|-------|
| Protocol | JSON-RPC 2.0 |
| Transport | HTTP POST |
| Response Format | `text/event-stream` (SSE) |
| Session Model | Stateless — session ID returned on `initialize`, passed as header on subsequent calls |
| Auth | Bearer token in `Authorization` header |

---

## 3. Interaction Flow

### Step 1: Initialize (Get Session ID)

```batch
curl.exe -v --max-time 15 ^
  -H "Authorization: Bearer <TOKEN>" ^
  -H "Content-Type: application/json" ^
  -H "Accept: text/event-stream" ^
  -d @payload_initialize.json ^
  https://bookmyjuice-test.mcp.chargebee.com/<agent>
```

**Payload** (`payload_initialize.json`):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "curl-client",
      "version": "1.0.0"
    }
  }
}
```

**Response** includes `mcp-session-id` header in the HTTP response (e.g. `019ea86e-ad6b-7b82-ac95-1317dc6f9c9d`). Save this value — it's needed for all subsequent calls.

### Step 2: Discover Tools

```batch
curl.exe -s --max-time 15 ^
  -H "Authorization: Bearer <TOKEN>" ^
  -H "mcp-session-id: <SESSION_ID>" ^
  -H "Content-Type: application/json" ^
  -H "Accept: text/event-stream" ^
  -d @payload_tools_list.json ^
  https://bookmyjuice-test.mcp.chargebee.com/<agent> > output.json 2>&1
```

**Payload** (`payload_tools_list.json`):
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

### Step 3: Call a Tool

```batch
curl.exe -s --max-time 15 ^
  -H "Authorization: Bearer <TOKEN>" ^
  -H "mcp-session-id: <SESSION_ID>" ^
  -H "Content-Type: application/json" ^
  -H "Accept: text/event-stream" ^
  -d @payload_tool_call.json ^
  https://bookmyjuice-test.mcp.chargebee.com/<agent> > output.json 2>&1
```

**Payload** (`payload_tool_call.json`):
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "<tool_name>",
    "arguments": {
      ...
    }
  }
}
```

---

## 4. Windows PowerShell Requirements

**PowerShell mangling issue:** PowerShell interprets `{ }` braces as script blocks and `@` as the splatting operator, which corrupts inline JSON. **Always use separate payload files** with `-d @file.json`.

**Best practice — use `.bat` files:**

1. Create a `.bat` file with the curl command
2. Use caret `^` for line continuation (not backtick)
3. Store JSON payloads in separate `.json` files
4. Execute with `.\filename.bat` from PowerShell

**Redirect SSE output to a file** for clean parsing:
```batch
curl.exe -s ... > output.json 2>&1
```

---

## 5. Available Tools

### 5.1 Data Lookup Agent (Read-Only)

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `search_plans` | List all plans in catalog | `limit` (max 100), `offset` (paginate with `next_offset`) |
| `search_addons` | List all addons in catalog | `limit` (max 100), `offset` |
| `retrieve_item` | Get item details (id, name, type, status, metadata) | `item_id` |
| `retrieve_item_price` | Get pricing info for an item price ID | `item_price_id` |
| `list_item_prices` | All pricing options for an item | `item_id`, `limit` |
| `list_customers` | List customers with optional filters | `limit`, `offset`, `filters_json`, `include_fields_json` |
| `fetch_customers_via_email` | Find customer by email | `email`, `limit` |
| `fetch_customers_via_company` | Find customer by company | `company_name`, `company_email_domain` |
| `retrieve_customer` | Get customer details by ID | `customer_id` |
| `list_subscriptions` | List subscriptions with filters | `limit`, `offset`, `filters_json`, `include_fields_json` |
| `list_subscriptions_for_customer` | Subscriptions for one customer | `customer_id`, `limit`, `status` |
| `retrieve_subscription` | Get subscription details | `subscription_id` |
| `list_invoices` | List invoices with filters | `limit`, `offset`, `filters_json`, `include_fields_json` |
| `list_invoices_by_customer` | Invoices for one customer | `customer_id`, `limit`, `status` |
| `list_invoices_by_subscription` | Invoices for one subscription | `subscription_id`, `limit`, `status` |
| `retrieve_invoice` | Get invoice details | `invoice_id` |
| `retrieve_invoice_pdf` | Generate invoice PDF URL | `invoice_id` |
| `list_transactions` | List transactions with filters | `limit`, `offset`, `filters_json`, `include_fields_json` |
| `list_transactions_by_customer` | Transactions for one customer | `customer_id`, `status`, `limit`, `offset` |
| `list_transactions_by_invoices` | Transactions for one invoice | `invoice_id`, `limit`, `offset` |
| `retrieve_transaction` | Get transaction details | `transaction_id` |
| `list_credit_notes` | List credit notes with filters | `limit`, `offset`, `filters_json`, `include_fields_json` |
| `retrieve_credit_note` | Get credit note details | `credit_note_id` |
| `retrieve_credit_note_pdf` | Generate credit note PDF URL | `credit_note_id` |
| `list_quotes` | List quotes with filters | `limit`, `offset`, `filters_json`, `include_fields_json` |
| `retrieve_quote` | Get quote details | `quote_id` |
| `retrieve_quote_pdf` | Generate quote PDF URL | `quote_id` |
| `list_events` | List events by type and date range | `event_type`, `from_date`, `to_date`, `limit`, `offset` |
| `fetch_events_by_customer_id` | Events for one customer | `customer_handle`, `event_type`, `from_date`, `to_date`, `limit`, `offset` |
| `retrieve_event` | Get event details | `event_id` |
| `retrieve_payment_intent` | Get payment intent details | `payment_intent_id` |
| `export_customers` | Start customer export job | `filters_json`, `export_type` |
| `export_subscriptions` | Start subscription export job | `filters_json`, `export_type` |
| `export_invoices` | Start invoice export job | `filters_json` |
| `export_credit_notes` | Start credit note export job | `filters_json` |
| `export_transactions` | Start transaction export job | `filters_json` |
| `retrieve_export` | Check export job status + get download URL | `export_id` |
| `get_filter_conditions_metadata` | Get filter schema for a list resource | `resource` (customers/subscriptions/invoices/etc.) |
| `get_response_field_metadata` | Get response schema for include_fields_json | `resource` |

### 5.2 Onboarding Agent (Write/Destructive)

| Tool | Purpose | Notes |
|------|---------|-------|
| `customize_branding` | Extract logo/colors from website URL | DESTRUCTIVE |
| `generate_product_catalog` | Generate Chargebee catalog from pricing summary text | AI-generation tool (read-only output) |
| `import_product_catalog` | Import items, families, prices, currencies | DESTRUCTIVE — writes to Chargebee |
| `generate_features` | Generate features from pricing summary | AI-generation tool (read-only output) |
| `generate_entitlements` | Generate entitlements from pricing + features + catalog | AI-generation tool (read-only output) |
| `import_features_and_entitlements` | Import features and entitlements | DESTRUCTIVE — writes to Chargebee |
| `generate_customers_and_subscriptions` | Generate demo data from pricing + catalog | AI-generation tool (read-only output) |
| `import_customers` | Import customer data | DESTRUCTIVE — writes to Chargebee |
| `import_subscriptions` | Import subscription data | DESTRUCTIVE — writes to Chargebee |
| `import_quotes` | Import quote data | DESTRUCTIVE — writes to Chargebee |

---

## 6. Common Query Patterns

### Search all plans
```json
// JSON-RPC call payload
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "search_plans",
    "arguments": {
      "limit": 100,
      "offset": null
    }
  }
}
```

### Search all addons
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "search_addons",
    "arguments": {
      "limit": 100,
      "offset": null
    }
  }
}
```

### Retrieve item details
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "tools/call",
  "params": {
    "name": "retrieve_item",
    "arguments": {
      "item_id": "bmj-generic-delight-200ml"
    }
  }
}
```

### List item prices
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "tools/call",
  "params": {
    "name": "list_item_prices",
    "arguments": {
      "item_id": "bmj-generic-delight-200ml",
      "limit": 50
    }
  }
}
```

### Find customer by email
```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "method": "tools/call",
  "params": {
    "name": "fetch_customers_via_email",
    "arguments": {
      "email": "user@example.com",
      "limit": 10
    }
  }
}
```

### List subscriptions for a customer
```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "method": "tools/call",
  "params": {
    "name": "list_subscriptions_for_customer",
    "arguments": {
      "customer_id": "cust_abc123",
      "limit": 50,
      "status": null
    }
  }
}
```

---

## 7. Existing Batch Files (at project root)

| File | Purpose |
|------|---------|
| `_cb_data_lookup_init.bat` | Initialize data_lookup_agent session |
| `_cb_data_lookup_init_payload.json` | Initialize payload for data_lookup_agent |
| `_cb_data_lookup_tools.bat` | List data_lookup_agent tools |
| `_cb_data_lookup_tools_payload.json` | Tools/list payload for data_lookup_agent |
| `_cb_search_plans_payload.json` | Search plans payload (ready to use) |
| `_chargebee_init.bat` | Initialize onboarding_agent session |
| `chargebee_init_payload.json` | Initialize payload for onboarding_agent |
| `_chargebee_tools.bat` | List onboarding_agent tools |
| `_chargebee_tools_payload.json` | Tools/list payload for onboarding_agent |

### Quick start — search plans:
1. Initialize: `.\_cb_data_lookup_init.bat` → extract session ID from response (look for `mcp-session-id` header)
2. Create a batch file that uses that session ID and the search_plans payload, or edit `_cb_data_lookup_tools.bat` to point to `_cb_search_plans_payload.json`

---

## 8. Response Format

All responses use SSE format:
```
event: message
data: {"jsonrpc": "2.0", "id": <ID>, "result": {...}}
```

If there's an error:
```
event: message
data: {"jsonrpc": "2.0", "id": <ID>, "error": {"code": -32601, "message": "Method not found"}}
```

**Parse with Python:**
```python
import json

with open('output.json', 'r') as f:
    for line in f:
        if line.startswith('data: '):
            response = json.loads(line[6:])
            result = response.get('result')
            error = response.get('error')
            if result:
                tools = result.get('tools', [])
                # Process tools
            if error:
                print(f"Error: {error['message']}")
```

---

## 9. Useful Documents

| Document | Description |
|----------|-------------|
| `docs/chargebee_final_state.md` | Full catalog inventory — 3 families, 66 items, 102 prices |
| `chargebee_catalog.json` | Complete local copy of the Chargebee catalog (1504 lines) |
| `chargebee_data_lookup_tools.json` | Saved tools/list output for data_lookup_agent |
| `chargebee_tools_full.json` | Saved tools/list output for onboarding_agent |

---

## 10. Import Rules & Validation

When importing product catalog items via `import_product_catalog`:

- **IDs must be unique** across the entire Chargebee site (not just within your import). Conflicting IDs cause `"Internal name must be unique"` errors.
- **Error handling**: If import fails due to conflicts, the conflicting IDs must be manually deleted from the Chargebee dashboard before retrying.
- **Item types**: `plan` (subscription), `charge` (one-time), `addon` (supplemental)
- **Pricing model**: `flat_fee` for all BMJ plans
- **Currency**: `INR` (all prices in **paise** — divide by 100 for rupees)
- **Period**: `period: 1` + `period_unit: "week"` for weekly, `period: 1` + `period_unit: "month"` for monthly
- **Trial**: `trial_period: 0` (no trial)
- **Metadata**: `is_custom_pricing: false`

---

## 11. Quick Reference — Session Management

```
┌─────────────────────────────────────────────────────────┐
│  1. Initialize → get session ID                         │
│     curl.exe ... -d @init.json → extract mcp-session-id  │
│                                                          │
│  2. Discover tools (optional, one-time per session)      │
│     curl.exe ... -H "mcp-session-id: <ID>" ... tools/list  │
│                                                          │
│  3. Call tool                                            │
│     curl.exe ... -H "mcp-session-id: <ID>" ... tools/call  │
│                                                          │
│  Note: Session IDs persist for ~15 minutes of inactivity  │
│  Re-initialize if you get an invalid session error.       │
└─────────────────────────────────────────────────────────┘