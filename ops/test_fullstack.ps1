#requires -Version 5.1

$ErrorActionPreference = 'Continue'

$baseUrl = 'http://127.0.0.1:8080'
$adminUser = 'support@bookmyjuice.co.in'
$adminPass = 'testpass123'
$webhookUser = 'support@bookmyjuice.co.in'
$webhookPass = 'rADHASOAMI@0'

Write-Host '=== BookMyJuice Full-Stack Tests ===' -ForegroundColor Cyan
Write-Host ''

# Test 1: Signin
Write-Host '[TEST 1] Signing in to get JWT...' -ForegroundColor Yellow
try {
    $body = @{ username = $adminUser; password = $adminPass } | ConvertTo-Json
    $response = Invoke-WebRequest -Method POST -Uri "$baseUrl/api/auth/signin" -Body $body -ContentType 'application/json'
    $jwt = $response.Content
    Write-Host "✓ JWT obtained (length: $($jwt.Length))" -ForegroundColor Green
} catch {
    Write-Host "✗ Signin failed: $_" -ForegroundColor Red
    exit 1
}

$authHeaders = @{ Authorization = "Bearer $jwt" }

# Test 2: Subscriptions pricing plans
Write-Host '[TEST 2] Testing subscriptions pricing plans...' -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Method GET -Uri "$baseUrl/api/subscriptions/pricing/plans" -Headers $authHeaders
    Write-Host "✓ Pricing plans: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "✗ Pricing plans failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Hosted pricing page URLs
Write-Host '[TEST 3] Testing hosted pricing page URLs...' -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Method GET -Uri "$baseUrl/api/subscriptions/pricing-page" -Headers $authHeaders
    Write-Host "✓ Pricing page URLs: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "✗ Pricing page URLs failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Local order history
Write-Host '[TEST 4] Testing local order history...' -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Method GET -Uri "$baseUrl/api/orders/local/history" -Headers $authHeaders
    Write-Host "✓ Order history: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "✗ Order history failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Invoice fetch (sample id)
Write-Host '[TEST 5] Testing invoice fetch (sample id)...' -ForegroundColor Yellow
$sampleInvoiceId = 'inv_test_001'
try {
    $response = Invoke-WebRequest -Method GET -Uri "$baseUrl/api/invoices/$sampleInvoiceId" -Headers $authHeaders
    Write-Host "✓ Invoice fetch: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "✗ Invoice fetch failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: Subscription webhook with Basic Auth
Write-Host '[TEST 6] Testing subscription webhook with Basic Auth...' -ForegroundColor Yellow
try {
    $pair = "${webhookUser}:${webhookPass}"
    $basic = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($pair))
    $basicHeaders = @{ Authorization = "Basic $basic" }
    $webhookBody = @{ id = 'evt_test_001' } | ConvertTo-Json
    $response = Invoke-WebRequest -Method POST -Uri "$baseUrl/api/webhooks/subscriptions" -Headers $basicHeaders -Body $webhookBody -ContentType 'application/json'
    Write-Host "✓ Webhook: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "✗ Webhook failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ''
Write-Host '=== Tests Complete ===' -ForegroundColor Cyan
