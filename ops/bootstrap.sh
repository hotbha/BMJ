#!/bin/bash
set -e

echo "=== Bootstrapping BookMyJuice Dev Environment (Android only) ==="

# --- Flutter setup ---
echo ">> Checking Flutter SDK..."
cd /workspace/BOOKMYJUICE/lush
flutter doctor
flutter pub get

# --- Backend setup ---
echo ">> Building Spring Boot backend..."
cd /workspace/BOOKMYJUICE/bmServer
./mvnw clean verify -DskipTests=false || true

# --- Android SDK setup ---
echo ">> Configuring Android SDK..."
flutter config --android-sdk /opt/android-sdk

# Return to workspace root
cd /workspace/BOOKMYJUICE

echo "=== Bootstrap complete! ==="