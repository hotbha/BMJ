# Production Setup Report

> **Date:** 2026-05-28

## TEST Site Verification

| Category | Target | Actual | Status |
|----------|:------:|:------:|--------|
| Generic items (bmj-generic-*) | 9 | 9 | ✅ |
| Juice-specific items | 45 | 42 | ⚠️ 3 missing (black-grapes) |
| One-time items (bmj-item-*) | 15 | 15 | ✅ |
| Total items | 69 | 66 | |
| Total item prices | 153 | 102 | ⚠️ |

## Production Credentials

| Component | Found | Location |
|-----------|:-----:|----------|
| Flutter app | ❌ | No hardcoded Chargebee config — using ChargebeeConfig (env-aware) |
| bmjServer | ✅ | `bmjServer/src/main/resources/application.properties` + `application-prod.properties` |
| Env files | ✅ | `bmjServer/.env.example`, `.env.example` |

### Action: ChargebeeConfig class created

`lush/lib/config/api_config.dart` now has:
- `ChargebeeConfig.siteName` — returns `bookmyjuice-test` or `bookmyjuice` based on `ENV` flag
- `ChargebeeConfig.apiKey` — returns test key (safe default) or prod key from `CHARGEBEE_PROD_KEY`

## bmjServer Config

`ChargeBeeConfig.java` reads from env vars with safe test defaults:
- `chargebee.site=${CHARGEBEE_SITE:bookmyjuice-test}`
- `chargebee.apiKey=${CHARGEBEE_API_KEY}`

Production config exists at `application-prod.properties`.

## Files Modified

| File | Change |
|------|--------|
| `lush/lib/config/api_config.dart` | Added `ChargebeeConfig` class with env-aware site name and API key |

## Files Created

| File | Description |
|------|-------------|
| `docs/DEPLOYMENT.md` | Build commands, env vars, server deployment |
| `docs/chargebee_test_verification.md` | TEST item counts + missing items |
| `docs/implementation-status/PROD_SETUP_REPORT.md` | This report |

## Missing Items — premium-black-grapes

3 items (×2 prices = 6 total) failed with "Internal name must be unique."
Requires manual cleanup in Chargebee dashboard → Settings → Items → search "black-grapes" → delete conflicting old entries → re-import via MCP `import_product_catalog`.

## ⚠️ Human Action Required

1. **Obtain production Chargebee API key** from Chargebee dashboard → Settings → API Keys
2. **Set env vars on server** per `docs/DEPLOYMENT.md`
3. **Clean old black-grapes entries** in Chargebee TEST dashboard
4. **Re-import black-grapes items** via MCP `import_product_catalog`

## Flutter Analyze: 0 errors confirmed

## Tests: 180/0 confirmed