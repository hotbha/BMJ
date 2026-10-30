#requires -Version 5.1

<#
.SYNOPSIS
    Starts the BMJ backend on this machine so a physical phone can reach it over Wi-Fi.

.DESCRIPTION
    Why this script exists (all three facts were verified on this machine):
      * Port 8080 is already owned by an unrelated service ("AgentService"), so the backend
        is hosted on 8085 instead.
      * spring-dotenv does NOT load .env for this project, so WEBHOOK_USERNAME /
        WEBHOOK_PASSWORD / JWT_SECRET / CHARGEBEE_* stay unresolved and startup fails with
        "Cannot pass null or empty values to constructor" (webhookUserDetailsService).
        This script loads .env into the process environment before starting Maven.
      * application(-dev).properties hardcode jdbc:mysql://${DB_HOSTNAME}:3306/... while the
        local MySQL used for dev is the Docker container published on 127.0.0.1:3307.
        This script overrides spring.datasource.url via SPRING_DATASOURCE_URL.

    The app must be built/run with the LAN URL printed at the end, e.g.:
        flutter run -d 192.168.1.5:5555 --dart-define=API_BASE_URL=http://192.168.1.10:8085

.PARAMETER Port
    HTTP port for the backend (default 8085; 8080 is taken by AgentService).

.PARAMETER DbPort
    Host port of the local MySQL container (default 3307; bmj-smoke-mysql).

.PARAMETER DbName
    Database name (default bmj_db).

.PARAMETER Profile
    Spring profile (default dev).

.PARAMETER EnableSms
    Keep Fast2SMS enabled. By default the API key is blanked so OTPs are printed to the
    log only and no real SMS is sent while testing.

.PARAMETER Restart
    If the port is already held by a java process, stop it and continue.

.PARAMETER Rebuild
    Force `mvnw.cmd -DskipTests package` before starting (otherwise the jar is rebuilt only
    when a source file is newer than it).

.PARAMETER HealthTimeoutSeconds
    How long to wait for /api/health to return UP (default 180).

.EXAMPLE
    .\ops\run_local_server.ps1

.EXAMPLE
    .\ops\run_local_server.ps1 -Restart -Port 8085
#>

param(
    [int]$Port = 8085,
    [int]$DbPort = 3307,
    [string]$DbName = 'bmj_db',
    [string]$Profile = 'dev',
    [switch]$EnableSms,
    [switch]$Restart,
    [switch]$Rebuild,
    [int]$HealthTimeoutSeconds = 180
)

$ErrorActionPreference = 'Stop'

$repoRoot  = Split-Path -Parent $PSScriptRoot
$serverDir = Join-Path $repoRoot 'bmjServer'
$envFile   = Join-Path $repoRoot '.env'
$logDir    = Join-Path $serverDir 'logs'
$logFile   = Join-Path $logDir 'local-run.log'

if (-not (Test-Path (Join-Path $serverDir 'pom.xml'))) {
    Write-Error "Could not find bmjServer at $serverDir. Run this script from the repo root."
    exit 1
}
if (-not (Test-Path $envFile)) {
    Write-Error "Could not find .env at $envFile. Copy .env.example and fill it in."
    exit 1
}
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}
# --- 1. Load .env into the process environment -------------------------------
$loadedKeys = 0
foreach ($line in Get-Content $envFile) {
    $trimmed = $line.Trim()
    if ($trimmed -eq '' -or $trimmed.StartsWith('#')) { continue }
    if ($trimmed -notmatch '^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$') { continue }

    $key   = $Matches[1]
    $value = $Matches[2].Trim()
    if ($value.Length -ge 2 -and (($value.StartsWith('"') -and $value.EndsWith('"')) -or
                                  ($value.StartsWith("'") -and $value.EndsWith("'")))) {
        $value = $value.Substring(1, $value.Length - 2)
    }
    Set-Item -Path "env:$key" -Value $value
    $loadedKeys++
}
Write-Host "[ENV] Loaded $loadedKeys keys from $envFile" -ForegroundColor Green

foreach ($required in @('WEBHOOK_USERNAME', 'WEBHOOK_PASSWORD', 'JWT_SECRET')) {
    if (-not (Get-Item -Path "env:$required" -ErrorAction SilentlyContinue)) {
        Write-Error "$required is missing from $envFile - the server cannot start without it."
        exit 1
    }
}

# --- 2. Force the settings that differ from the committed defaults -----------
$env:SPRING_PROFILES_ACTIVE             = $Profile
$env:SERVER_PORT                        = "$Port"
$env:SPRING_DATASOURCE_URL              = "jdbc:mysql://127.0.0.1:$DbPort/$DbName?allowPublicKeyRetrieval=true&useSSL=false"
$env:SPRING_DATASOURCE_USERNAME         = if ($env:DB_USERNAME) { $env:DB_USERNAME } else { 'bmj' }
$env:SPRING_DATASOURCE_PASSWORD         = $env:DB_PASSWORD
$env:CHARGEBEE_SYNC_ENABLE_STARTUP_SYNC = 'false'

if (-not $env:ADMIN_PASSWORD) {
    # .env ships an empty ADMIN_PASSWORD; spring.security.user.password must not be blank.
    $env:ADMIN_PASSWORD = 'local-admin-pw'
}

if (-not $EnableSms) {
    # Empty key => SmsService runs in DEV mode and logs the OTP instead of sending SMS.
    $env:FAST2SMS_API_KEY = ''
}

$smsMode = if ($EnableSms) { 'live' } else { 'console-only' }
Write-Host "[CFG] profile=$Profile port=$Port db=127.0.0.1:$DbPort/$DbName sms=$smsMode" -ForegroundColor Cyan

# --- 3. Free the port if a previous run still owns it ------------------------
$listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($listener) {
    $owner = Get-Process -Id $listener.OwningProcess -ErrorAction SilentlyContinue
    $ownerName = if ($owner) { $owner.ProcessName } else { 'unknown' }
    if ($Restart -and $owner -and $ownerName -like 'java*') {
        Write-Host "[RESTART] Stopping $ownerName (PID $($owner.Id)) holding port $Port" -ForegroundColor Yellow
        Stop-Process -Id $owner.Id -Force
        Start-Sleep -Seconds 4
    } else {
        Write-Error "Port $Port is already in use by '$ownerName' (PID $($listener.OwningProcess)). Re-run with -Restart or choose another -Port."
        exit 1
    }
}

# --- 4a. Build the runnable jar ---------------------------------------------
# `java -jar` (not `mvn spring-boot:run`) is what B5_SMOKE_TEST_PLAN.md §2.1 documents, and it
# is the only path where --spring.datasource.url survives intact: passing the same URL through
# the Maven plugin/env landed in MySQL as jdbc:mysql://127.0.0.1:3307/=true&useSSL=false.
$targetDir = Join-Path $serverDir 'target'
$jar = Get-ChildItem $targetDir -Filter 'com.bookmyjuice.bmjServer-*.jar' -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -notmatch 'sources|javadoc|original' } |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
$newestSource = Get-ChildItem (Join-Path $serverDir 'src'), (Join-Path $serverDir 'pom.xml') -Recurse -File -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
$needBuild = $Rebuild -or -not $jar -or ($newestSource -and $newestSource.LastWriteTime -gt $jar.LastWriteTime)

if ($needBuild) {
    Write-Host "[BUILD] mvnw.cmd -DskipTests package" -ForegroundColor Yellow
    Push-Location $serverDir
    try {
        & cmd.exe /c 'mvnw.cmd -DskipTests package' 2>&1 | Select-String -Pattern 'BUILD|ERROR|Building jar' | ForEach-Object { Write-Host "  $($_.Line.Trim())" }
    } finally {
        Pop-Location
    }
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Build failed (exit $LASTEXITCODE)."
        exit 1
    }
    $jar = Get-ChildItem $targetDir -Filter 'com.bookmyjuice.bmjServer-*.jar' |
        Where-Object { $_.Name -notmatch 'sources|javadoc|original' } |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
}

Write-Host "[JAR] $($jar.FullName) ($($jar.LastWriteTime))" -ForegroundColor Cyan

# --- 4b. Launch the jar with explicit CLI overrides --------------------------
$javaExe = (Get-Command java.exe -ErrorAction SilentlyContinue).Source
if (-not $javaExe) { Write-Error 'java.exe not found on PATH.'; exit 1 }

# NOTE: ${DbName} MUST be braced. "$DbName?allowPublicKeyRetrieval" is parsed by PowerShell as a
# single variable named DbName?allowPublicKeyRetrieval (undefined -> empty), which silently turns
# the URL into jdbc:mysql://127.0.0.1:3307/=true&useSSL=false.
$jdbcUrl  = "jdbc:mysql://127.0.0.1:$DbPort/${DbName}?allowPublicKeyRetrieval=true&useSSL=false"
$errFile  = Join-Path $logDir 'local-run.err.log'
$javaArgs = @(
    '-jar', $jar.FullName,
    "--server.port=$Port",
    "--spring.profiles.active=$Profile",
    "--spring.datasource.url=$jdbcUrl",
    '--chargebee.sync.enable-startup-sync=false'
)

Write-Host "[RUN] java $($javaArgs -join ' ')" -ForegroundColor Yellow
$launcher = Start-Process -FilePath $javaExe -ArgumentList $javaArgs -WorkingDirectory $serverDir `
    -RedirectStandardOutput $logFile -RedirectStandardError $errFile -PassThru -WindowStyle Hidden
Write-Host "[RUN] PID $($launcher.Id); log: $logFile" -ForegroundColor Yellow

# --- 5. Wait for /api/health ------------------------------------------------
$healthUrl = "http://127.0.0.1:$Port/api/health"
$deadline  = (Get-Date).AddSeconds($HealthTimeoutSeconds)
$healthy   = $false
Write-Host "[WAIT] Polling $healthUrl ..." -ForegroundColor Yellow
while ((Get-Date) -lt $deadline) {
    Start-Sleep -Seconds 3
    try {
        $response = Invoke-WebRequest -Uri $healthUrl -TimeoutSec 4 -UseBasicParsing
        if ($response.StatusCode -eq 200) { $healthy = $true; break }
    } catch {
        # not up yet
    }
    if (-not (Get-Process -Id $launcher.Id -ErrorAction SilentlyContinue)) {
        Write-Host "[FAIL] Maven exited before the server became healthy." -ForegroundColor Red
        break
    }
}

if (-not $healthy) {
    Write-Host ""
    Write-Host "[FAIL] Server did not become healthy. Last log lines:" -ForegroundColor Red
    Get-Content $logFile -Tail 40 -ErrorAction SilentlyContinue | Write-Host
    if (Test-Path $errFile) { Get-Content $errFile -Tail 20 -ErrorAction SilentlyContinue | Write-Host }
    if ((Get-Content $logFile -Tail 200 -ErrorAction SilentlyContinue) -match 'Communications link failure|Connection refused') {
        Write-Host "[HINT] MySQL is not reachable on 127.0.0.1:$DbPort. Start it first:" -ForegroundColor Yellow
        Write-Host "       wsl -d Ubuntu-22.04 -e docker start bmj-smoke-mysql" -ForegroundColor Yellow
    }
    exit 1
}

# --- 6. Report the URL the phone should use ---------------------------------
# find_active_ip.ps1 reports with Write-Host (information stream), so 6>&1 is required to
# capture the address instead of having it printed on its own line and losing the value.
$ipScript = Join-Path $PSScriptRoot 'find_active_ip.ps1'
$ip = $null
if (Test-Path $ipScript) {
    $ip = & $ipScript 6>&1 | Where-Object { "$_" -match '^\d{1,3}(\.\d{1,3}){3}$' } | Select-Object -Last 1
}
if (-not $ip) {
    $ip = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object {
            $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*' -and
            $_.InterfaceAlias -notlike '*vEthernet*' -and $_.InterfaceAlias -notlike '*Loopback*'
        } |
        Sort-Object { if ($_.InterfaceAlias -like '*Wi-Fi*') { 0 } else { 1 } } |
        Select-Object -First 1 -ExpandProperty IPAddress
}
if (-not $ip) { $ip = '127.0.0.1' }
$apiUrl = "http://$($ip):$Port"

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Green
Write-Host "  BMJ backend is UP on $apiUrl" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Green
Write-Host "  Health (host)  : $healthUrl -> 200" -ForegroundColor White
Write-Host "  Health (phone) : adb -s 192.168.1.5:5555 shell curl -s $apiUrl/api/health" -ForegroundColor White
Write-Host "  Run the app    : cd lush" -ForegroundColor White
Write-Host "                   flutter run -d 192.168.1.5:5555 --dart-define=API_BASE_URL=$apiUrl" -ForegroundColor White
Write-Host "  OTP codes      : Select-String -Path ""$logFile"" -Pattern 'OTP' | Select-Object -Last 3" -ForegroundColor White
Write-Host "  Stop the server: .\ops\stop_local_server.ps1 -Port $Port" -ForegroundColor White
Write-Host "=======================================================" -ForegroundColor Green
