# BookMyJuice E2E Testing Makefile
# Supports: Emulators, Physical Devices, CI/CD

.PHONY: help test-e2e test-device test-physical test-emulator test-checkout test-signup test-cart test-orders test-full test-report e2e-clean e2e-all

# Default target
help:
	@echo "BookMyJuice E2E Testing Framework"
	@echo ""
	@echo "Usage:"
	@echo "  make test-e2e              # Run all E2E tests on default device"
	@echo "  make test-device DEVICE=ID # Run on specific device (emulator or physical)"
	@echo "  make test-physical         # Run on physical device (25053PC47I)"
	@echo "  make test-emulator         # Run on emulator"
	@echo "  make test-checkout         # Run checkout flow tests only"
	@echo "  make test-signup           # Run signup flow tests only"
	@echo "  make test-cart             # Run cart flow tests only"
	@echo "  make test-orders           # Run orders flow tests only"
	@echo "  make test-full             # Run complete E2E suite"
	@echo "  make test-report           # Run with JSON reporting"
	@echo "  make e2e-clean             # Clean E2E reports"
	@echo "  make e2e-all               # Clean + run with reporting"
	@echo ""
	@echo "Examples:"
	@echo "  make test-device DEVICE=25053PC47I"
	@echo "  make test-device DEVICE=emulator-5554"
	@echo ""

# Run all E2E tests on default device
test-e2e:
	@echo "🚀 Running E2E tests..."
	cd lush && patrol test --dart-define=E2E=true

# Run on specific device (emulator or physical)
test-device:
ifndef DEVICE
	$(error DEVICE is required. Usage: make test-device DEVICE=25053PC47I)
endif
	@echo "🚀 Running E2E tests on device: $(DEVICE)"
	cd lush && patrol test --dart-define=E2E=true --device-id=$(DEVICE)

# Run on physical device (default: 25053PC47I)
test-physical:
	@echo "📱 Running E2E tests on physical device..."
	$(MAKE) test-device DEVICE=25053PC47I

# Run on emulator
test-emulator:
	@echo "🖥️  Running E2E tests on emulator..."
	$(MAKE) test-device DEVICE=emulator-5554

# Run checkout flow tests only
test-checkout:
	@echo "🛒 Running checkout E2E tests..."
	cd lush && patrol test integration_test/e2e_checkout_test.dart --dart-define=E2E=true

# Run signup flow tests only
test-signup:
	@echo "👤 Running signup E2E tests..."
	cd lush && patrol test integration_test/e2e_signup_test.dart --dart-define=E2E=true

# Run cart flow tests only
test-cart:
	@echo "🛍️  Running cart E2E tests..."
	cd lush && patrol test integration_test/e2e_cart_test.dart --dart-define=E2E=true

# Run orders flow tests only
test-orders:
	@echo "📦 Running orders E2E tests..."
	cd lush && patrol test integration_test/e2e_orders_test.dart --dart-define=E2E=true

# Run complete E2E suite
test-full:
	@echo "🎯 Running complete E2E suite..."
	cd lush && patrol test integration_test/e2e_suite.dart --dart-define=E2E=true

# Run with JSON reporting
test-report:
	@echo "📊 Running E2E tests with JSON reporting..."
	mkdir -p ./.e2e-reports
	cd lush && patrol test --dart-define=E2E=true --reporter=json --reporter-path=../.e2e-reports/results.json

# Clean E2E reports
e2e-clean:
	@echo "🧹 Cleaning E2E reports..."
	rm -rf ./.e2e-reports/*
	@echo "✅ Cleaned"

# Clean + run with reporting
e2e-all: e2e-clean test-report
	@echo "✅ E2E tests complete. Reports in ./.e2e-reports/"

# CI/CD target (headless mode)
test-ci:
	@echo "🤖 Running E2E tests in CI mode (headless)..."
	cd lush && patrol test --dart-define=E2E=true --headless

# Video recording mode
test-video:
	@echo "🎥 Running E2E tests with video recording..."
	mkdir -p ./.e2e-reports/videos
	cd lush && patrol test --dart-define=E2E=true --video --video-path=../.e2e-reports/videos/

# Screenshot mode
test-screenshots:
	@echo "📸 Running E2E tests with screenshots..."
	mkdir -p ./.e2e-reports/screenshots
	cd lush && patrol test --dart-define=E2E=true --screenshots --screenshots-path=../.e2e-reports/screenshots/

# Install dependencies
install:
	@echo "📦 Installing E2E dependencies..."
	cd lush && flutter pub get
	npm install
	@echo "✅ Dependencies installed"

# List available devices
devices:
	@echo "📱 Available devices:"
	patrol devices

# Check Patrol installation
check:
	@echo "🔍 Checking Patrol installation..."
	patrol --version
	@echo "✅ Patrol installed"
