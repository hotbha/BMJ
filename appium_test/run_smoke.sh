#!/bin/bash
set -e

echo "═══════════════════════════════════════"
echo " BookMyJuice E2E — Smoke Suite (REAL)"
echo "═══════════════════════════════════════"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Preflight checks
python3 preflight.py || exit 1

# Start Appium if not running
if ! curl -s http://127.0.0.1:4723/status > /dev/null 2>&1; then
  appium --port 4723 \
    --log reports/appium.log \
    --log-level warn &
  APPIUM_PID=$!
  sleep 3
fi

# Run smoke suites (auth, catalog, subscription, orders)
python3 -m pytest tests/suite_1_auth/ \
  tests/suite_3_catalog/ \
  tests/suite_4_subscription/ \
  tests/suite_5_orders/ \
  --html=reports/smoke_report.html \
  --self-contained-html \
  -v \
  --tb=long \
  --capture=no \
  2>&1 | tee reports/smoke_output.log

RESULT=$?

# Kill Appium if we started it
if [ -n "$APPIUM_PID" ]; then
  kill $APPIUM_PID 2>/dev/null || true
fi

echo ""
echo "═══════════════════════════════════════"
if [ $RESULT -eq 0 ]; then
  echo " ✅ SMOKE TESTS PASSED"
else
  echo " ❌ FAILURES — see reports/"
fi
echo " Report: reports/smoke_report.html"
echo " Failures: reports/screenshots/FAIL_*"
echo "═══════════════════════════════════════"
exit $RESULT