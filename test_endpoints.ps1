# BookMyJuice API Endpoint Testing Script
# Tests all 20 Chargebee integration endpoints
# Date: January 9, 2026

$serverUrl = "http://127.0.0.1:8080"
$adminEmail = "support@bookmyjuice.co.in"
$adminPassword = "testpass123"
$adminId = 515

# Color codes for output
$successColor = "Green"
$errorColor = "Red"
$infoColor = "Cyan"
$warningColor = "Yellow"

Write-Host "========================================" -ForegroundColor $infoColor
Write-Host "BookMyJuice API Endpoint Testing" -ForegroundColor $infoColor
Write-Host "========================================" -ForegroundColor $infoColor
Write-Host ""

# Step 1: Login and get JWT token
Write-Host "[1/21] Logging in as admin user..." -ForegroundColor $infoColor
$loginBody = @{username=$adminEmail;password=$adminPassword} | ConvertTo-Json
try {
    $loginResponse = Invoke-RestMethod -Uri "$serverUrl/api/auth/signin" -Method Post -ContentType "application/json" -Body $loginBody -ErrorAction Stop
    $token = $loginResponse.accessToken
    Write-Host "✅ Login successful! Token: $($token.Substring(0, 40))..." -ForegroundColor $successColor
    Write-Host "   User ID: $($loginResponse.id)" -ForegroundColor $infoColor
    Write-Host "   Roles: $($loginResponse.roles -join ', ')" -ForegroundColor $infoColor
} catch {
    Write-Host "❌ Login failed: $($_.Exception.Message)" -ForegroundColor $errorColor
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

# Helper function to test endpoint
function Test-Endpoint {
    param(
        [string]$name,
        [string]$method,
        [string]$endpoint,
        [hashtable]$body = $null,
        [int]$expectedStatus = 200,
        [int]$testNumber
    )
    
    Write-Host ""
    Write-Host "[$testNumber] Testing: $name" -ForegroundColor $infoColor
    Write-Host "   $method $endpoint" -ForegroundColor $warningColor
    
    try {
        $params = @{
            Uri = "$serverUrl$endpoint"
            Method = $method
            Headers = $headers
            ErrorAction = "Stop"
        }
        
        if ($body) {
            $params["Body"] = $body | ConvertTo-Json
            $params["ContentType"] = "application/json"
        }
        
        $response = Invoke-RestMethod @params
        
        Write-Host "✅ SUCCESS - Status: 200" -ForegroundColor $successColor
        Write-Host "   Response: $($response | ConvertTo-Json -Depth 2 | Select-Object -First 100)" -ForegroundColor $infoColor
        return $true
    } catch {
        $errorResponse = $null
        try {
            $errorResponse = $_.Exception.Response.Content | ConvertFrom-Json
        } catch {
            $errorResponse = $_.Exception.Message
        }
        
        Write-Host "❌ FAILED" -ForegroundColor $errorColor
        Write-Host "   Error: $errorResponse" -ForegroundColor $errorColor
        return $false
    }
}

$results = @()

# SUBSCRIPTION ENDPOINTS (8 total)
Write-Host "" -ForegroundColor $infoColor
Write-Host "--- SUBSCRIPTION ENDPOINTS (8) ---" -ForegroundColor $infoColor
Write-Host "" -ForegroundColor $infoColor

$results += Test-Endpoint -name "Get All Subscriptions" -method "GET" -endpoint "/api/subscriptions" -testNumber 2
$results += Test-Endpoint -name "Get Subscription Details" -method "GET" -endpoint "/api/subscriptions/test_sub_123" -testNumber 3
$results += Test-Endpoint -name "Get Subscription Plans" -method "GET" -endpoint "/api/subscriptions/plans" -testNumber 4
$results += Test-Endpoint -name "Get Subscription Pricing" -method "GET" -endpoint "/api/subscriptions/pricing" -testNumber 5
$results += Test-Endpoint -name "Pause Subscription" -method "POST" -endpoint "/api/subscriptions/test_sub_123/pause" -testNumber 6
$results += Test-Endpoint -name "Resume Subscription" -method "POST" -endpoint "/api/subscriptions/test_sub_123/resume" -testNumber 7
$results += Test-Endpoint -name "Cancel Subscription" -method "POST" -endpoint "/api/subscriptions/test_sub_123/cancel" -testNumber 8
$results += Test-Endpoint -name "Create Subscription" -method "POST" -endpoint "/api/subscriptions" -body @{plan_id="test_plan";customer_id="test_cust"} -testNumber 9

# ORDER ENDPOINTS (5 total)
Write-Host "" -ForegroundColor $infoColor
Write-Host "--- ORDER ENDPOINTS (5) ---" -ForegroundColor $infoColor
Write-Host "" -ForegroundColor $infoColor

$results += Test-Endpoint -name "Get All Orders" -method "GET" -endpoint "/api/orders" -testNumber 10
$results += Test-Endpoint -name "Get Order Details" -method "GET" -endpoint "/api/orders/test_order_123" -testNumber 11
$results += Test-Endpoint -name "Get Local Order History" -method "GET" -endpoint "/api/orders/local/history" -testNumber 12
$results += Test-Endpoint -name "Get Local Order Details" -method "GET" -endpoint "/api/orders/local/details?orderId=1" -testNumber 13
$results += Test-Endpoint -name "Get Admin All Orders" -method "GET" -endpoint "/api/orders/admin/all" -testNumber 14

# INVOICE ENDPOINTS (7 total)
Write-Host "" -ForegroundColor $infoColor
Write-Host "--- INVOICE ENDPOINTS (7) ---" -ForegroundColor $infoColor
Write-Host "" -ForegroundColor $infoColor

$results += Test-Endpoint -name "Get All Invoices" -method "GET" -endpoint "/api/invoices" -testNumber 15
$results += Test-Endpoint -name "Get Invoice Details" -method "GET" -endpoint "/api/invoices/test_invoice_123" -testNumber 16
$results += Test-Endpoint -name "Get Invoice PDF" -method "GET" -endpoint "/api/invoices/test_invoice_123/pdf" -testNumber 17
$results += Test-Endpoint -name "Send Invoice Email" -method "POST" -endpoint "/api/invoices/test_invoice_123/email" -testNumber 18
$results += Test-Endpoint -name "Get Local Invoice History" -method "GET" -endpoint "/api/invoices/local/history" -testNumber 19
$results += Test-Endpoint -name "Get Local Invoice Details" -method "GET" -endpoint "/api/invoices/local/details?invoiceId=1" -testNumber 20
$results += Test-Endpoint -name "Get Admin All Invoices" -method "GET" -endpoint "/api/invoices/admin/all" -testNumber 21

# Summary
Write-Host "" -ForegroundColor $infoColor
Write-Host "========================================" -ForegroundColor $infoColor
Write-Host "TEST SUMMARY" -ForegroundColor $infoColor
Write-Host "========================================" -ForegroundColor $infoColor

$passCount = ($results | Where-Object { $_ -eq $true }).Count
$failCount = ($results | Where-Object { $_ -eq $false }).Count
$totalTests = $results.Count

Write-Host "Total Tests: $totalTests" -ForegroundColor $infoColor
Write-Host "Passed: $passCount" -ForegroundColor $successColor
Write-Host "Failed: $failCount" -ForegroundColor $errorColor

$passPercentage = [math]::Round(($passCount / $totalTests) * 100, 2)
Write-Host "Pass Rate: $passPercentage%" -ForegroundColor $infoColor

if ($failCount -eq 0) {
    Write-Host "" -ForegroundColor $successColor
    Write-Host "🎉 ALL TESTS PASSED! 🎉" -ForegroundColor $successColor
} else {
    Write-Host "" -ForegroundColor $warningColor
    Write-Host "⚠️  Some tests failed. Review output above." -ForegroundColor $warningColor
}

Write-Host "" -ForegroundColor $infoColor
Write-Host "========================================" -ForegroundColor $infoColor
