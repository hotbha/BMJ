#requires -Version 5.1

<#
.SYNOPSIS
    Builds the Flutter app with the correct API_BASE_URL for phone testing.
.DESCRIPTION
    Automatically detects your current machine IP and builds the Flutter app
    with API_BASE_URL set to that IP, so your phone can connect to the backend.
    
    Usage:
        .\ops\build_flutter_for_phone.ps1
        .\ops\build_flutter_for_phone.ps1 -Port 8080
        .\ops\build_flutter_for_phone.ps1 -UseEmulator  (uses 10.0.2.2:8080)
.PARAMETER Port
    The backend port (default: 8080)
.PARAMETER UseEmulator
    Use 10.0.2.2 (Android emulator loopback) instead of detecting your IP
.PARAMETER RunOnly
    Don't rebuild, just print the command and instructions
.EXAMPLE
    .\ops\build_flutter_for_phone.ps1
    Detects IP and builds Flutter for Android with API_BASE_URL set.
.EXAMPLE
    .\ops\build_flutter_for_phone.ps1 -UseEmulator
    Builds with API_BASE_URL=http://10.0.2.2:8080 (for emulator testing)
#>

param(
    [int]$Port = 8080,
    [switch]$UseEmulator,
    [switch]$RunOnly
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$lushDir = Join-Path $projectRoot "lush"

if (-not (Test-Path (Join-Path $lushDir "pubspec.yaml"))) {
    Write-Error "Could not find Flutter project at $lushDir. Make sure you're running from the repo root."
    exit 1
}

# Determine the API base URL
if ($UseEmulator) {
    $apiUrl = "http://10.0.2.2:$Port"
    Write-Host "[INFO] Using Android emulator loopback: $apiUrl" -ForegroundColor Cyan
} else {
    try {
        $detectedIp = & (Join-Path $PSScriptRoot "find_active_ip.ps1")
        $apiUrl = "http://${detectedIp}:$Port"
        Write-Host "[INFO] Detected your IP: $detectedIp" -ForegroundColor Green
        Write-Host "[INFO] API Base URL: $apiUrl" -ForegroundColor Cyan
    } catch {
        Write-Error "Could not detect IP: $_"
        Write-Host "Please run: .\ops\find_active_ip.ps1 manually and pass the IP to Flutter." -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "  Building Flutter App for Phone Testing" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "  API_BASE_URL: $apiUrl" -ForegroundColor White
Write-Host "  Backend must be running at: $apiUrl" -ForegroundColor Yellow
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

if ($RunOnly) {
    Write-Host "Build command (run from lush/):" -ForegroundColor Yellow
    Write-Host "  cd lush" -ForegroundColor White
    Write-Host "  flutter run --dart-define=API_BASE_URL=$apiUrl" -ForegroundColor White
    Write-Host ""
    Write-Host "For APK:" -ForegroundColor Yellow
    Write-Host "  cd lush" -ForegroundColor White
    Write-Host "  flutter build apk --dart-define=API_BASE_URL=$apiUrl" -ForegroundColor White
    exit 0
}

# Check if any Android devices are connected
Write-Host "[CHECK] Looking for connected Android devices..." -ForegroundColor Yellow
try {
    $devices = & adb devices 2>$null
    if ($devices -match "^\w+\s+device$" -or $UseEmulator) {
        Write-Host "[INFO] Device(s) found. Running Flutter app..." -ForegroundColor Green
        Push-Location $lushDir
        try {
            flutter run --dart-define="API_BASE_URL=$apiUrl"
        } finally {
            Pop-Location
        }
    } else {
        Write-Host "[INFO] No Android device detected. Building APK instead..." -ForegroundColor Yellow
        Push-Location $lushDir
        try {
            flutter build apk --dart-define="API_BASE_URL=$apiUrl"
            Write-Host ""
            Write-Host "[DONE] APK built at: lush\build\app\outputs\flutter-apk\app-release.apk" -ForegroundColor Green
            Write-Host "Install it on your phone with:" -ForegroundColor Cyan
            Write-Host "  adb install lush\build\app\outputs\flutter-apk\app-release.apk" -ForegroundColor White
            Write-Host ""
            Write-Host "Ensure your phone is on the same WiFi network as this machine." -ForegroundColor Yellow
            Write-Host "Backend must be running at: $apiUrl" -ForegroundColor Yellow
        } finally {
            Pop-Location
        }
    }
} catch {
    Write-Host "[WARN] ADB not found. Building APK instead..." -ForegroundColor Yellow
    Push-Location $lushDir
    try {
        flutter build apk --dart-define="API_BASE_URL=$apiUrl"
        Write-Host "[DONE] APK built at: lush\build\app\outputs\flutter-apk\app-release.apk" -ForegroundColor Green
    } finally {
        Pop-Location
    }
}

Write-Host ""
Write-Host "=== If IP changes in the future, just re-run this script ===" -ForegroundColor Cyan
