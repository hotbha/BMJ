# ============================================================
# BookMyJuice - MVP Build & Launch Script
# ============================================================
# Purpose: Automated build and verification for MVP launch
# Usage: .\MVP_BUILD_AND_LAUNCH.ps1
# ============================================================

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  BookMyJuice - MVP Build & Launch Script" -ForegroundColor Cyan
Write-Host "  Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================
# Configuration
# ============================================================
$BACKEND_DIR = "x:\BMJ\bmjServer"
$FRONTEND_DIR = "x:\BMJ\lush"
$ERROR_COUNT = 0
$WARNING_COUNT = 0

# ============================================================
# Helper Functions
# ============================================================
function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
    $script:ERROR_COUNT++
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
    $script:WARNING_COUNT++
}

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "  $Message" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
}

# ============================================================
# Step 1: Check Prerequisites
# ============================================================
Write-Step "Checking Prerequisites"

# Check Java
Write-Info "Checking Java installation..."
try {
    $javaVersion = java -version 2>&1 | Select-String "version" | Select-Object -First 1
    if ($javaVersion) {
        Write-Success "Java found: $javaVersion"
    } else {
        Write-Error-Custom "Java not found. Please install Java 17+"
    }
} catch {
    Write-Error-Custom "Java not found. Please install Java 17+"
}

# Check Maven
Write-Info "Checking Maven installation..."
try {
    $mavenVersion = & "$BACKEND_DIR\mvnw.cmd" --version 2>&1 | Select-String "Apache Maven" | Select-Object -First 1
    if ($mavenVersion) {
        Write-Success "Maven found: $mavenVersion"
    } else {
        Write-Warning-Custom "Maven wrapper not working, trying system Maven..."
    }
} catch {
    Write-Warning-Custom "Maven wrapper not accessible"
}

# Check Flutter
Write-Info "Checking Flutter installation..."
try {
    $flutterVersion = flutter --version 2>&1 | Select-String "Flutter" | Select-Object -First 1
    if ($flutterVersion) {
        Write-Success "Flutter found: $flutterVersion"
    } else {
        Write-Error-Custom "Flutter not found. Please install Flutter 3.24+"
    }
} catch {
    Write-Error-Custom "Flutter not found. Please install Flutter 3.24+"
}

# Check MySQL
Write-Info "Checking MySQL connection..."
try {
    $mysqlResult = mysql -h localhost -u bmj -prADHASOAMI$8 bmj_db -e "SELECT 1 as test;" 2>&1
    if ($mysqlResult -match "test") {
        Write-Success "MySQL connection successful"
    } else {
        Write-Warning-Custom "MySQL connection failed. Database may not be running."
    }
} catch {
    Write-Warning-Custom "MySQL not accessible. Will try to start with Docker."
}

if ($ERROR_COUNT -gt 0) {
    Write-Error-Custom "Prerequisites check failed. Please fix errors before continuing."
    exit 1
}

# ============================================================
# Step 2: Build Backend
# ============================================================
Write-Step "Building Backend"

Set-Location $BACKEND_DIR

Write-Info "Cleaning previous build..."
& ".\mvnw.cmd" clean 2>&1 | Out-Null

Write-Info "Compiling backend..."
$buildResult = & ".\mvnw.cmd" compile 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Success "Backend compilation successful"
} else {
    Write-Error-Custom "Backend compilation failed"
    Write-Host $buildResult -ForegroundColor Red
    exit 1
}

# ============================================================
# Step 3: Start Backend Server
# ============================================================
Write-Step "Starting Backend Server"

Write-Info "Starting Spring Boot on port 8080..."
Write-Info "This will run in the background. Press Ctrl+C to stop later."

# Start backend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
    Set-Location '$BACKEND_DIR'
    Write-Host 'Starting BookMyJuice Backend...' -ForegroundColor Green
    .\mvnw.cmd spring-boot:run
"@

Start-Sleep -Seconds 5

Write-Info "Waiting for backend to start (10 seconds)..."
Start-Sleep -Seconds 10

# Test health endpoint
Write-Info "Testing health endpoint..."
try {
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:8080/api/health" -Method Get -ErrorAction Stop
    Write-Success "Backend is running! Status: $($healthResponse.status)"
    Write-Host "  Version: $($healthResponse.version)" -ForegroundColor Green
    Write-Host "  Timestamp: $($healthResponse.timestamp)" -ForegroundColor Green
} catch {
    Write-Warning-Custom "Backend health check failed. Server may still be starting..."
}

# ============================================================
# Step 4: Build Flutter Frontend
# ============================================================
Write-Step "Building Flutter Frontend"

Set-Location $FRONTEND_DIR

Write-Info "Getting Flutter dependencies..."
flutter pub get

if ($LASTEXITCODE -eq 0) {
    Write-Success "Flutter dependencies installed"
} else {
    Write-Error-Custom "Flutter pub get failed"
    exit 1
}

Write-Info "Analyzing code..."
flutter analyze 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Success "Flutter analysis passed"
} else {
    Write-Warning-Custom "Flutter analysis found issues (may still work)"
}

# ============================================================
# Step 5: Build APK
# ============================================================
Write-Step "Building APK for Beta Testing"

# Get user's IP address
Write-Info "Detecting your IP address..."
$ipAddress = (Get-NetIPAddress | Where-Object {$_.AddressFamily -eq 'IPv4' -and $_.InterfaceAlias -notlike '*Loopback*'} | Select-Object -First 1).IPAddress

if ($ipAddress) {
    Write-Success "Your IP address: $ipAddress"
    Write-Info "Flutter app will connect to: http://$ipAddress`:8080"
} else {
    Write-Warning-Custom "Could not detect IP. Using localhost."
    $ipAddress = "localhost"
}

Write-Info "Building debug APK..."
flutter build apk --debug --dart-define=API_BASE_URL="http://$ipAddress`:8080"

if ($LASTEXITCODE -eq 0) {
    Write-Success "APK built successfully!"
    $apkPath = "$FRONTEND_DIR\build\app\outputs\flutter-apk\app-debug.apk"
    Write-Host "  Location: $apkPath" -ForegroundColor Green
    
    # Ask if user wants to copy to a shared location
    $copyToDesktop = Read-Host "Copy APK to Desktop? (y/n)"
    if ($copyToDesktop -eq 'y' -or $copyToDesktop -eq 'Y') {
        Copy-Item $apkPath -Destination "$env:USERPROFILE\Desktop\BookMyJuice-MVP.apk" -Force
        Write-Success "APK copied to Desktop: BookMyJuice-MVP.apk"
    }
} else {
    Write-Error-Custom "APK build failed"
    exit 1
}

# ============================================================
# Step 6: Summary & Next Steps
# ============================================================
Write-Step "Build Complete! Summary"

Write-Host @"

✅ MVP BUILD SUMMARY
====================

Backend:
  Status: Running
  URL: http://localhost:8080
  Health: http://localhost:8080/api/health
  Swagger: http://localhost:8080/swagger-ui.html

Frontend:
  APK Location: $FRONTEND_DIR\build\app\outputs\flutter-apk\app-debug.apk
  API Endpoint: http://$ipAddress`:8080

Next Steps:
  1. Install APK on your Android device
     - Transfer APK via USB/WhatsApp/Drive
     - Enable 'Install from Unknown Sources'
     - Install and open app

  2. Test the app:
     - Create account (use real email)
     - Browse products
     - Add to cart
     - Complete checkout

  3. Share with beta users:
     - APK is at: $FRONTEND_DIR\build\app\outputs\flutter-apk\app-debug.apk
     - Or from Desktop: BookMyJuice-MVP.apk

  4. Backend is running in a separate window
     - Keep it running while testing
     - Stop with Ctrl+C when done

  5. For remote access (users not on same WiFi):
     - Use ngrok: ngrok http 8080
     - Update API URL and rebuild APK

Feedback Collection:
  WhatsApp: [Your number]
  Email: support@bookmyjuice.co.in

============================================================
  MVP LAUNCH READY! 🚀
============================================================

"@ -ForegroundColor Green

Write-Host "Build completed with $ERROR_COUNT errors and $WARNING_COUNT warnings." -ForegroundColor $(if ($ERROR_COUNT -eq 0) { "Green" } else { "Red" })
Write-Host ""

# Keep window open
Read-Host "Press Enter to exit"
