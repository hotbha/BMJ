# Deployment Guide

## Required Environment Variables

### Flutter App (passed via --dart-define at build time)

| Variable | Default | Description |
|----------|---------|-------------|
| `ENV` | `test` | Set to `production` for prod builds |
| `CHARGEBEE_PROD_KEY` | (none) | Production Chargebee Full Access API key |
| `CHARGEBEE_TEST_KEY` | Read-only test key (safe default) | Test Chargebee API key |
| `API_BASE_URL` | Platform default | Backend API base URL |

### bmjServer (Spring Boot)

| Variable | Default | Description |
|----------|---------|-------------|
| `CHARGEBEE_SITE` | `bookmyjuice-test` | Chargebee site name |
| `CHARGEBEE_API_KEY` | (required) | Chargebee Full Access API key |
| `JWT_SECRET` | (required) | JWT signing secret |
| `DB_USERNAME` | (required) | MySQL database user |
| `DB_PASSWORD` | (required) | MySQL database password |
| `DB_HOSTNAME` | (required) | MySQL host |
| `DB_NAME` | (required) | MySQL database name |

## Build Commands

### Test Build (default — safe to run anywhere)
```
flutter build apk
```

### Production Build
```
flutter build apk \
  --dart-define=ENV=production \
  --dart-define=CHARGEBEE_PROD_KEY=[prod api key here] \
  --dart-define=API_BASE_URL=https://api.bookmyjuice.com
```

## Server Deployment
```
# Set environment variables on server
export CHARGEBEE_SITE=bookmyjuice
export CHARGEBEE_API_KEY=[prod api key]
export JWT_SECRET=[secret]
export DB_USERNAME=[user]
export DB_PASSWORD=[password]
export DB_HOSTNAME=[host]
export DB_NAME=bookmyjuice

# Start Spring Boot
java -jar bmjServer.jar
```

## Notes
- Never commit API keys to git
- Test key in `.clinerules/cline-guardrails.md` is read-only, test-only
- Production key must be obtained from Chargebee dashboard under Settings → API Keys → Full Access API Key
- bmjServer reads `application.properties` which references env vars with defaults