# Comprehensive API Testing with Timeouts
# Tests all 20 BookMyJuice endpoints with proper timeout handling

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BookMyJuice API Comprehensive Test Suite" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$serverUrl = "http://127.0.0.1:8080"
$results = @()
$timeout = 15  # 15 second timeout for Chargebee calls

# Step 1: Authenticate
Write-Host "[AUTH] Logging in as admin..." -ForegroundColor Yellow
$loginBody = @{username="support"; password="testpass123"} | ConvertTo-Json
$loginResponse = Invoke-RestMethod -Uri "$serverUrl/api/auth/signin" -Method Post -ContentType "application/json" -Body $loginBody
$token = $loginResponse.accessToken
$headers = @{"Authorization"="Bearer $token"}

Write-Host "✅ Authenticated: User ID $($loginResponse.id), Role: $($loginResponse.roles -join ', ')`n" -ForegroundColor Green

# Helper function
function Test-API {
    param([string]$name, [string]$endpoint, [string]$method="GET", [hashtable]$headers)
    
    $fullUrl = "$serverUrl$endpoint"
    try {
        if ($method -eq "GET") {
            $response = Invoke-RestMethod -Uri $fullUrl -Method Get -Headers $headers -TimeoutSec $timeout
        } else {
            $response = Invoke-RestMethod -Uri $fullUrl -Method Post -Headers $headers -TimeoutSec $timeout
        }
        Write-Host "✅ $name" -ForegroundColor Green
        return $true
    } catch {
        $msg = $_.Exception.Message
        if ($msg -like "*500*") {
            Write-Host "⚠️  $name (Chargebee API Error)" -ForegroundColor Yellow
        } elseif ($msg -like "*timeout*") {
            Write-Host "⏱️  $name (Timeout)" -ForegroundColor Yellow
        } else {
            Write-Host "❌ $name ($msg)" -ForegroundColor Red
        }
        return $false
    }
}

Write-Host "=== SUBSCRIPTION ENDPOINTS (8) ===" -ForegroundColor Cyan
Write-Host "[1] GET /api/subscriptions" -ForegroundColor DarkGray
$results += Test-API -name "Get My Subscriptions" -endpoint "/api/subscriptions" -headers $headers

Write-Host "[2] GET /api/subscriptions/{id}" -ForegroundColor DarkGray
$results += Test-API -name "Get Subscription Details" -endpoint "/api/subscriptions/test_sub_123" -headers $headers

Write-Host "[3] GET /api/subscriptions/pricing/plans" -ForegroundColor DarkGray
$results += Test-API -name "Get Subscription Plans" -endpoint "/api/subscriptions/pricing/plans" -headers $headers

Write-Host "[4] GET /api/subscriptions/pricing-page" -ForegroundColor DarkGray
$results += Test-API -name "Get Pricing Page" -endpoint "/api/subscriptions/pricing-page" -headers $headers

Write-Host "[5] PUT /api/subscriptions/{id}/pause" -ForegroundColor DarkGray
$results += Test-API -name "Pause Subscription" -endpoint "/api/subscriptions/test_sub_123/pause" -method "PUT" -headers $headers

Write-Host "[6] PUT /api/subscriptions/{id}/resume" -ForegroundColor DarkGray
$results += Test-API -name "Resume Subscription" -endpoint "/api/subscriptions/test_sub_123/resume" -method "PUT" -headers $headers

Write-Host "[7] DELETE /api/subscriptions/{id}" -ForegroundColor DarkGray
$results += Test-API -name "Cancel Subscription" -endpoint "/api/subscriptions/test_sub_123" -method "DELETE" -headers $headers

Write-Host "[8] POST /api/subscriptions/create" -ForegroundColor DarkGray
$results += Test-API -name "Create Subscription" -endpoint "/api/subscriptions/create" -method "POST" -headers $headers

Write-Host "`n=== ORDER ENDPOINTS (5) ===" -ForegroundColor Cyan
Write-Host "[9] GET /api/orders" -ForegroundColor DarkGray
$results += Test-API -name "Get My Orders" -endpoint "/api/orders" -headers $headers

Write-Host "[10] GET /api/orders/{id}" -ForegroundColor DarkGray
$results += Test-API -name "Get Order Details" -endpoint "/api/orders/test_order_123" -headers $headers

Write-Host "[11] GET /api/orders/local/history" -ForegroundColor DarkGray
$results += Test-API -name "Get Local Order History" -endpoint "/api/orders/local/history" -headers $headers

Write-Host "[12] GET /api/orders/local/details" -ForegroundColor DarkGray
$results += Test-API -name "Get Local Order Details" -endpoint "/api/orders/local/details?orderId=1" -headers $headers

Write-Host "[13] GET /api/orders/admin/all" -ForegroundColor DarkGray
$results += Test-API -name "Get Admin All Orders" -endpoint "/api/orders/admin/all" -headers $headers

Write-Host "`n=== INVOICE ENDPOINTS (7) ===" -ForegroundColor Cyan
Write-Host "[14] GET /api/invoices" -ForegroundColor DarkGray
$results += Test-API -name "Get My Invoices" -endpoint "/api/invoices" -headers $headers

Write-Host "[15] GET /api/invoices/{id}" -ForegroundColor DarkGray
$results += Test-API -name "Get Invoice Details" -endpoint "/api/invoices/test_inv_123" -headers $headers

Write-Host "[16] GET /api/invoices/{id}/pdf" -ForegroundColor DarkGray
$results += Test-API -name "Get Invoice PDF" -endpoint "/api/invoices/test_inv_123/pdf" -headers $headers

Write-Host "[17] POST /api/invoices/{id}/email" -ForegroundColor DarkGray
$results += Test-API -name "Send Invoice Email" -endpoint "/api/invoices/test_inv_123/email" -method "POST" -headers $headers

Write-Host "[18] GET /api/invoices/local/history" -ForegroundColor DarkGray
$results += Test-API -name "Get Local Invoice History" -endpoint "/api/invoices/local/history" -headers $headers

Write-Host "[19] GET /api/invoices/local/details" -ForegroundColor DarkGray
$results += Test-API -name "Get Local Invoice Details" -endpoint "/api/invoices/local/details?invoiceId=1" -headers $headers

Write-Host "[20] GET /api/invoices/admin/all" -ForegroundColor DarkGray
$results += Test-API -name "Get Admin All Invoices" -endpoint "/api/invoices/admin/all" -headers $headers

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TEST SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$passCount = ($results | Where-Object { $_ -eq $true }).Count
$failCount = ($results.Count - $passCount)

Write-Host "Total Endpoints: $($results.Count)" -ForegroundColor Cyan
Write-Host "Successful: $passCount" -ForegroundColor Green
Write-Host "Failed/Timeout: $failCount" -ForegroundColor Yellow

$percentage = [math]::Round(($passCount / $results.Count) * 100, 1)
Write-Host "Success Rate: $percentage%" -ForegroundColor Cyan

Write-Host "`nNote: Chargebee API calls (Subscriptions, Orders, Invoices) may timeout or fail" -ForegroundColor Yellow
Write-Host "if the Chargebee test account is not properly configured." -ForegroundColor Yellow
Write-Host "Local database endpoints should succeed with proper data." -ForegroundColor Gray
