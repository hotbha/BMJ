$ErrorActionPreference = 'Continue'

Write-Host ""
Write-Host "=== BookMyJuice Full-Stack Tests ===" -ForegroundColor Cyan
Write-Host ""

$BaseUrl = "http://127.0.0.1:8080"
$AdminEmail = "support@bookmyjuice.co.in"
$AdminPassword = "testpass123"
$WebhookUser = "support@bookmyjuice.co.in"
$WebhookPass = "rADHASOAMI@0"

# TEST 1: Signin
Write-Host "[TEST 1] Signing in to get JWT..." -ForegroundColor Yellow
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
    
    # TEST 2: Subscriptions pricing
    Write-Host "[TEST 2] Testing subscriptions pricing plans..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Method GET `
            -Uri "$BaseUrl/api/subscriptions/pricing/plans" `
            -Headers $headers `
            -UseBasicParsing `
            -ErrorAction Stop | Out-Null
        Write-Host "[PASS] Test 2 passed" -ForegroundColor Green
    } catch {
        Write-Host "[FAIL] Test 2 failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host ""
    
    # TEST 3: Hosted pricing page
    Write-Host "[TEST 3] Testing hosted pricing page URLs..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Method GET `
            -Uri "$BaseUrl/api/subscriptions/pricing-page" `
            -Headers $headers `
            -UseBasicParsing `
            -ErrorAction Stop | Out-Null
        Write-Host "[PASS] Test 3 passed" -ForegroundColor Green
    } catch {
        Write-Host "[FAIL] Test 3 failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host ""
    
    # TEST 4: Order history
    Write-Host "[TEST 4] Testing local order history..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Method GET `
            -Uri "$BaseUrl/api/orders/local/history" `
            -Headers $headers `
            -UseBasicParsing `
            -ErrorAction Stop | Out-Null
        Write-Host "[PASS] Test 4 passed" -ForegroundColor Green
    } catch {
        Write-Host "[FAIL] Test 4 failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host ""
    
    # TEST 5: Invoice fetch
    Write-Host "[TEST 5] Testing invoice fetch (sample id)..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Method GET `
            -Uri "$BaseUrl/api/invoices/1" `
            -Headers $headers `
            -UseBasicParsing `
            -ErrorAction Stop | Out-Null
        Write-Host "[PASS] Test 5 passed" -ForegroundColor Green
    } catch {
        Write-Host "[FAIL] Test 5 failed: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "[SKIP] Skipping authenticated tests (signin failed)" -ForegroundColor Yellow
}

Write-Host ""

# TEST 6: Webhook
Write-Host "[TEST 6] Testing subscription webhook with Basic Auth..." -ForegroundColor Yellow
$webhookBody = @{
    event_type = "subscription_created"
    event_id = "test_123"
} | ConvertTo-Json

$pair = "$WebhookUser`:$WebhookPass"
$bytes = [System.Text.Encoding]::ASCII.GetBytes($pair)
$base64 = [System.Convert]::ToBase64String($bytes)
$webhookHeaders = @{ Authorization = "Basic $base64" }

try {
    Invoke-WebRequest -Method POST `
        -Uri "$BaseUrl/api/webhooks/subscriptions" `
        -ContentType "application/json" `
        -Headers $webhookHeaders `
        -Body $webhookBody `
        -UseBasicParsing `
        -ErrorAction Stop | Out-Null
    Write-Host "[PASS] Test 6 passed" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Test 6 failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Tests Complete ===" -ForegroundColor Cyan
Write-Host ""
