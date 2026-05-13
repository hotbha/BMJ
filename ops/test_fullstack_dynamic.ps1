#requires -Version 5.1

<#
.SYNOPSIS
    Full-stack test script that auto-detects the correct IP to use.
.DESCRIPTION
    Detects your current IP and runs all API tests against it.
    Run this instead of the older scripts that hardcode 127.0.0.1.
    
    Usage:
        .\ops\test_fullstack_dynamic.ps1                    # Local testing
        .\ops\test_fullstack_dynamic.ps1 -Remote            # Test from phone/other device
        .\ops\test_fullstack_dynamic.ps1 -CustomIP "192.168.1.5"  # Manual IP override
.PARAMETER Port
    Backend port (default: 8080)
.PARAMETER Remote
    Auto-detect your WiFi IP for testing from another device
.PARAMETER CustomIP
    Manually specify the IP address
.PARAMETER UseLocalhost
    Use 127.0.0.1 (default for local testing)
#>

param(
    [int]$Port = 8080,
    [switch]$Remote,
    [string]$CustomIP,
    [switch]$UseLocalhost
)

$ErrorActionPreference = 'Continue'
$scriptRoot = Split-Path -Parent $PSScriptRoot

# Determine Base URL
if ($UseLocalhost -or (-not $Remote -and -not $CustomIP)) {
    $BaseUrl = "http://127.0.0.1:$Port"
    Write-Host "[INFO] Testing locally: $BaseUrl" -ForegroundColor Cyan
} elseif ($CustomIP) {
    $BaseUrl = "http://${CustomIP}:$Port"
    Write-Host "[INFO] Using custom IP: $BaseUrl" -ForegroundColor Cyan
} else {
    # Auto-detect IP for remote testing
    $ipScript = Join-Path $scriptRoot "ops\find_active_ip.ps1"
    if (Test-Path $ipScript) {
        try {
            $detectedIp = & $ipScript
            $BaseUrl = "http://${detectedIp}:$Port"
            Write-Host "[INFO] Testing remotely via IP: $BaseUrl" -ForegroundColor Cyan
            Write-Host "[INFO] Make sure your phone is on the same WiFi!" -ForegroundColor Yellow
        } catch {
            Write-Error "Could not detect IP. Please use -CustomIP parameter."
            exit 1
        }
    } else {
        Write-Error "find_active_ip.ps1 not found. Please use -CustomIP parameter."
        exit 1
    }
}

$AdminEmail = "support@bookmyjuice.co.in"
$AdminPassword = "testpass123"
$WebhookUser = "support@bookmyjuice.co.in"
$WebhookPass = "rADHASOAMI@0"

# Test 1: Health Check
Write-Host ""
Write-Host "=== BookMyJuice Full-Stack Tests ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "[TEST 1] Health check..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Method GET -Uri "$BaseUrl/api/health" -UseBasicParsing -ErrorAction Stop
    Write-Host "[PASS] Health check: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[INFO] Is the backend running? Check: docker compose ps" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Test 2: Signin
Write-Host "[TEST 2] Signing in to get JWT..." -ForegroundColor Yellow
$loginBody = @{
    username = $AdminEmail
    password = $AdminPassword
} | ConvertTo-Json

try {
    $signinResponse = Invoke-WebRequest -Method POST `
        -Uri "$BaseUrl/api/auth/signin" `
        -ContentType "application/json" `
        -Body $loginBody `
        -UseBasicParsing `
        -ErrorAction Stop
    $jwt = ($signinResponse.Content | ConvertFrom-Json).accessToken
    Write-Host "[PASS] Signin successful - JWT obtained" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Signin failed: $($_.Exception.Message)" -ForegroundColor Red
    $jwt = $null
}

Write-Host ""

if ($jwt) {
    $headers = @{ Authorization = "Bearer $jwt" }
    
    # Test 3: Subscriptions pricing
    Write-Host "[TEST 3] Subscriptions pricing plans..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Method GET -Uri "$BaseUrl/api/subscriptions/pricing/plans" -Headers $headers -UseBasicParsing -ErrorAction Stop | Out-Null
        Write-Host "[PASS] Test 3 passed" -ForegroundColor Green
    } catch {
        Write-Host "[FAIL] Test 3 failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host ""
    
    # Test 4: Pricing page URLs
    Write-Host "[TEST 4] Pricing page URLs..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Method GET -Uri "$BaseUrl/api/subscriptions/pricing-page" -Headers $headers -UseBasicParsing -ErrorAction Stop | Out-Null
        Write-Host "[PASS] Test 4 passed" -ForegroundColor Green
    } catch {
        Write-Host "[FAIL] Test 4 failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host ""
    
    # Test 5: Order history
    Write-Host "[TEST 5] Local order history..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Method GET -Uri "$BaseUrl/api/orders/local/history" -Headers $headers -UseBasicParsing -ErrorAction Stop | Out-Null
        Write-Host "[PASS] Test 5 passed" -ForegroundColor Green
    } catch {
        Write-Host "[FAIL] Test 5 failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host ""
    
    # Test 6: Invoice fetch
    Write-Host "[TEST 6] Invoice fetch (sample id)..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Method GET -Uri "$BaseUrl/api/invoices/1" -Headers $headers -UseBasicParsing -ErrorAction Stop | Out-Null
        Write-Host "[PASS] Test 6 passed" -ForegroundColor Green
    } catch {
        Write-Host "[FAIL] Test 6 failed: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "[SKIP] Skipping authenticated tests (signin failed)" -ForegroundColor Yellow
}

Write-Host ""

# Test 7: Webhook
Write-Host "[TEST 7] Subscription webhook with Basic Auth..." -ForegroundColor Yellow
$webhookBody = @{
    event_type = "subscription_created"
    event_id = "test_123"
} | ConvertTo-Json

$pair = "$WebhookUser`:$WebhookPass"
$bytes = [System.Text.Encoding]::ASCII.GetBytes($pair)
$base64 = [System.Convert]::ToBase64String($bytes)
$webhookHeaders = @{ Authorization = "Basic $base64" }

try {
    Invoke-WebRequest -Method POST -Uri "$BaseUrl/api/webhooks/subscriptions" -ContentType "application/json" -Headers $webhookHeaders -Body $webhookBody -UseBasicParsing -ErrorAction Stop | Out-Null
    Write-Host "[PASS] Test 7 passed" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Test 7 failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Tests Complete ===" -ForegroundColor Cyan
