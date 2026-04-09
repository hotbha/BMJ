# BookMyJuice Android Emulator Setup Guide

**Version:** 1.0  
**Date:** April 1, 2026  
**Status:** LIVE

---

## 🎯 Purpose

This guide provides step-by-step instructions for setting up Android emulators to test the BookMyJuice Flutter app during development and E2E testing.

---

## � Prerequisites

### Required Software
- ✅ Android Studio (Arctic Fox or later)
- ✅ Flutter SDK 3.x
- ✅ Dart SDK 2.x
- ✅ 20GB free disk space
- ✅ Hardware virtualization enabled (VT-x/AMD-V)

### Verify Installation
```bash
# Check Flutter
flutter doctor

# Check Android SDK
flutter doctor --android-licenses

# Check emulator
emulator -list-avds
```

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Create Emulator via Android Studio
1. Open Android Studio
2. **Tools** → **Device Manager**
3. Click **Create Device**
4. Select **Pixel 6** (or similar)
5. Click **Next**
6. Select **Android 13 (API 33)**
7. Click **Next** → **Finish**

### Step 2: Start Emulator

**Windows:**
```powershell
# List available emulators
emulator -list-avds

# Start emulator (replace with your AVD name)
emulator -avd Pixel_6_API_33

# Or via Flutter
flutter emulators
```

**Linux/Mac:**
```bash
# List available emulators
emulator -list-avds

# Start emulator
emulator -avd Pixel_6_API_33

# Or via Flutter
flutter emulators
```

### Step 3: Connect Flutter App
```bash
# Check device is detected
flutter devices

# Run app
flutter run
```

---

## 📱 Recommended Emulator Configurations

### For Development
| Setting | Value |
|---------|-------|
| Device | Pixel 6 |
| Android Version | 13 (API 33) |
| RAM | 4096 MB |
| VM Heap | 256 MB |
| Internal Storage | 8192 MB |
| SD Card | 2048 MB |

### For E2E Testing (Physical Device Simulation)
| Setting | Value |
|---------|-------|
| Device | Pixel 6 Pro |
| Android Version | 13 (API 33) |
| RAM | 6144 MB |
| VM Heap | 512 MB |
| Internal Storage | 16384 MB |
| SD Card | 4096 MB |

### For Performance Testing
| Setting | Value |
|---------|-------|
| Device | Pixel 7 Pro |
| Android Version | 14 (API 34) |
| RAM | 8192 MB |
| VM Heap | 768 MB |
| Internal Storage | 32768 MB |
| SD Card | 8192 MB |

---

## ⚙️ Advanced Emulator Configuration

### Create Emulator via Command Line
```bash
# List available device definitions
avdmanager list device

# Create new AVD (Android Virtual Device)
avdmanager create avd \
  -n BookMyJuice_Test \
  -k "system-images;android-33;google_apis;x86_64" \
  -d pixel_6

# Start emulator with custom settings
emulator \
  -avd BookMyJuice_Test \
  -memory 4096 \
  -cores 4 \
  -gpu host \
  -camera-back virtualscene \
  -camera-front emulated
```

### Emulator Configuration File
**Location:** `~/.android/avd/BookMyJuice_Test.avd/config.ini`

```ini
hw.device.name=pixel_6
hw.device.manufacturer=Google
hw.lcd.density=420
hw.lcd.width=1080
hw.lcd.height=2400
hw.ramSize=4096
vm.heapSize=256
hw.gpu.enabled=yes
hw.gpu.mode=host
hw.keyboard=yes
hw.camera.back=virtualscene
hw.camera.front=emulated
disk.dataPartition.size=8G
disk.sdCard.size=2G
```

---

## 🔧 Troubleshooting

### Issue 1: Emulator Won't Start
**Symptoms:** Emulator crashes immediately or shows black screen

**Solutions:**
```bash
# Check virtualization is enabled
# Windows: Task Manager → Performance → CPU → Virtualization: Enabled
# Mac: sysctl -a | grep machdep.cpu.features | grep VMX

# Wipe emulator data
emulator -avd BookMyJuice_Test -wipe-data

# Start with verbose output
emulator -avd BookMyJuice_Test -verbose

# Use different GPU mode
emulator -avd BookMyJuice_Test -gpu swiftshader_indirect
```

### Issue 2: Emulator is Slow
**Symptoms:** Laggy UI, slow app launch

**Solutions:**
```bash
# Increase RAM
emulator -avd BookMyJuice_Test -memory 6144

# Use host GPU
emulator -avd BookMyJuice_Test -gpu host

# Enable multi-core
emulator -avd BookMyJuice_Test -cores 4

# Disable animations (in emulator settings)
Settings → Developer Options → 
  Window animation scale: Off
  Transition animation scale: Off
  Animator duration scale: Off
```

### Issue 3: Flutter Doesn't Detect Emulator
**Symptoms:** `flutter devices` shows no devices

**Solutions:**
```bash
# Restart ADB server
adb kill-server
adb start-server

# Check ADB connection
adb devices

# Restart emulator
emulator -avd BookMyJuice_Test

# Check Flutter configuration
flutter config --android-studio-dir="/path/to/android/studio"

# Verify Android SDK
flutter doctor --android-licenses
```

### Issue 4: No Internet in Emulator
**Symptoms:** App can't connect to backend

**Solutions:**
```bash
# Check emulator DNS settings
# In emulator: Settings → Network & Internet → DNS
# Set to: 8.8.8.8

# Check host machine internet
# Emulator shares host's internet connection

# Restart emulator with DNS
emulator -avd BookMyJuice_Test -dns-server 8.8.8.8

# For localhost access, use special IP
# Instead of localhost:8080, use: 10.0.2.2:8080
```

---

## 🧪 E2E Testing with Emulator

### Setup for E2E Tests
```bash
# Create dedicated test emulator
avdmanager create avd \
  -n BookMyJuice_E2E \
  -k "system-images;android-33;google_apis;x86_64" \
  -d pixel_6

# Start emulator
emulator -avd BookMyJuice_E2E -no-boot-anim -gpu host

# Wait for boot completion
adb wait-for-device shell \
  'while [[ -z $(getprop sys.boot_completed | tr -d '\r') ]]; do sleep 1; done'

# Run E2E tests
cd lush
flutter test integration_test/ \
  --dart-define=E2E=true \
  --device-id=emulator-5554
```

### Automated E2E Test Script
**File:** `scripts/run_e2e_tests.sh`

```bash
#!/bin/bash

# Start emulator
echo "Starting emulator..."
emulator -avd BookMyJuice_E2E -no-boot-anim -gpu host &

# Wait for emulator to boot
echo "Waiting for emulator to boot..."
adb wait-for-device shell \
  'while [[ -z $(getprop sys.boot_completed | tr -d '\r') ]]; do sleep 1; done'

# Unlock screen
adb shell input keyevent 82

# Run tests
echo "Running E2E tests..."
cd lush
flutter test integration_test/ \
  --dart-define=E2E=true \
  --dart-define=API_BASE_URL=http://10.0.2.2:8080 \
  --device-id=emulator-5554 \
  --reporter=json \
  --file-reporter=json:../.e2e-reports/emulator_results.json

# Stop emulator
echo "Stopping emulator..."
adb emu kill

echo "Tests complete!"
```

---

## � Emulator Performance Optimization

### Enable Hardware Acceleration

**Windows:**
1. BIOS/UEFI → Enable Intel VT-x or AMD-V
2. Windows Features → Enable Hyper-V
3. Install Intel HAXM or Windows Hypervisor Platform

**Mac:**
```bash
# Check virtualization
sysctl -a | grep machdep.cpu.features | grep VMX

# Enable if needed (usually enabled by default)
```

**Linux:**
```bash
# Check virtualization
egrep -c '(vmx|svm)' /proc/cpuinfo

# Enable KVM
sudo apt install qemu-kvm
sudo adduser $USER kvm
```

### Optimize Emulator Settings

**In Android Studio:**
1. **Settings** → **Appearance & Behavior** → **System Settings** → **Android Emulator**
2. Enable:
   - ✅ Launch in a tool window
   - ✅ Use Host GPU
   - ✅ Store a snapshot for faster startup
   - ✅ Initialize camera from: VirtualScene

**In emulator config.ini:**
```ini
hw.gpu.enabled=yes
hw.gpu.mode=host
disk.dataPartition.size=16G
vm.heapSize=512
hw.ramSize=6144
```

---

## 🔗 Backend Connection from Emulator

### Access Local Backend
```dart
// In Flutter app, use special IP for localhost
const String baseUrl = 'http://10.0.2.2:8080';

// NOT: http://localhost:8080 (refers to emulator itself)
// NOT: http://127.0.0.1:8080 (refers to emulator itself)
```

### Access Backend on Network
```dart
// If backend is on another machine
const String baseUrl = 'http://192.168.1.6:8080';

// Ensure:
// 1. Backend allows external connections
// 2. Firewall allows port 8080
// 3. Emulator has network access
```

### Test Connection
```bash
# From host machine
curl http://localhost:8080/api/health

# From emulator (via ADB shell)
adb shell curl http://10.0.2.2:8080/api/health

# From Flutter app
print('Testing connection...');
final response = await http.get(Uri.parse('http://10.0.2.2:8080/api/health'));
print('Response: ${response.statusCode}');
```

---

## 📸 Emulator Screenshots for Testing

### Take Screenshot
```bash
# Via ADB
adb shell screencap -p /sdcard/screenshot.png
adb pull /sdcard/screenshot.png

# Via emulator console
echo "screenshot screenshot.png" | telnet localhost 5554
```

### Record Screen
```bash
# Start recording
adb shell screenrecord /sdcard/test_video.mp4

# Stop recording (Ctrl+C)
# Pull video
adb pull /sdcard/test_video.mp4
```

---

## 🧹 Maintenance

### Clean Up Old Emulators
```bash
# List all AVDs
emulator -list-avds

# Delete unused AVD
avdmanager delete avd -n Old_Emulator_Name

# Clean emulator cache
rm -rf ~/.android/avd/*.avd/cache.img
rm -rf ~/.android/avd/*.avd/userdata-qemu.img
```

### Update Emulator
```bash
# Update Android SDK tools
sdkmanager --update

# Update emulator
sdkmanager "emulator"

# Update system images
sdkmanager "system-images;android-33;google_apis;x86_64"
```

---

## 📚 Resources

| Resource | Link |
|----------|------|
| Android Emulator Docs | https://developer.android.com/studio/run/emulator |
| Flutter Testing Docs | https://docs.flutter.dev/testing/integration-tests |
| ADB Commands | https://developer.android.com/studio/command-line/adb |
| AVD Manager | https://developer.android.com/studio/run/managing-avds |

---

## 🎯 Quick Reference

### Common Commands
```bash
# List emulators
emulator -list-avds

# Start emulator
emulator -avd <AVD_NAME>

# Check connected devices
adb devices

# Install APK
adb install app-release.apk

# Run Flutter app
flutter run -d emulator-5554

# Take screenshot
adb shell screencap -p /sdcard/screen.png && adb pull /sdcard/screen.png

# Clear app data
adb shell pm clear com.bookmyjuice.app

# View logs
adb logcat | grep -i bookmyjuice
```

### Emulator Keyboard Shortcuts
| Shortcut | Action |
|----------|--------|
| Ctrl+F11 | Rotate screen |
| F11 | Fullscreen toggle |
| Ctrl+Shift+F11 | Rotate screen (opposite) |
| Home | Home button |
| Back | Back button |
| Menu | Menu button |
| PgUp/PgDn | Volume up/down |

---

**Last Updated:** April 1, 2026  
**Maintained By:** BookMyJuice Engineering Team  
**Next Review:** May 1, 2026
