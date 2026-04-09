# ============================================================
# BookMyJuice - MVP Endpoint Testing Script
# ============================================================
# Purpose: Verify all critical endpoints are working
# Usage: .\MVP_TEST_ENDPOINTS.ps1
# ============================================================

param(
    [string]$BaseUrl = "http://localhost:8080",
    [switch]$Verbose
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  BookMyJuice - MVP Endpoint Testing" -ForegroundColor Cyan
Write-Host "  Base URL: $BaseUrl" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================
# Test Counters
# ============================================================
$TOTAL_TESTS = 0
$PASSED_TESTS = 0
$FAILED_TESTS = 0

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Method,
        [string]$Url,
        [object]$Body = $null,
        [hashtable]$Headers = @{},
        [int]$ExpectedStatus = 200
    )
    
    $TOTAL_TESTS++
    Write-Host "Testing: $Name" -ForegroundColor Yellow
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            ContentType = 'application/json'
            Headers = $Headers
        }
        
        if ($Body) {
            $params.Body = $Body | ConvertTo-Json -Depth 10
        }
        
        $response = Invoke-RestMethod @params -ErrorAction Stop
        
        if ($Verbose) {
            Write-Host "Response: $($response | ConvertTo-Json -Depth 5)" -ForegroundColor Gray
        }
        
        Write-Host "  ✓ PASSED" -ForegroundColor Green
        $PASSED_TESTS++
        return $response
    } catch {
        Write-Host "  ✗ FAILED: $($_.Exception.Message)" -ForegroundColor Red
        $FAILED_TESTS++
        return $null
    }
}

# ============================================================
# 1. Health Check
# ============================================================
Write-Host "`n=== HEALTH CHECK ===" -ForegroundColor Cyan
Test-Endpoint -Name "Health Check" -Method "GET" -Url "$BaseUrl/api/health"

# ============================================================
# 2. Public Endpoints (No Auth)
# ============================================================
Write-Host "`n=== PUBLIC ENDPOINTS ===" -ForegroundColor Cyan

# Test signup
$signupBody = @{
    username = "test_$(Get-Random -Maximum 9999)@test.com"
    email = "test_$(Get-Random -Maximum 9999)@test.com"
    password = "Test123!"
    firstName = "Test"
    lastName = "User"
} | ConvertTo-Json

$signupResponse = Test-Endpoint -Name "User Signup" -Method "POST" -Url "$BaseUrl/api/auth/signup" -Body $signupBody

# Test login
$loginBody = @{
    username = "test@test.com"
    password = "Test123!"
} | ConvertTo-Json

$loginResponse = Test-Endpoint -Name "User Login" -Method "POST" -Url "$BaseUrl/api/auth/signin" -Body $loginBody

# Extract token if login successful
$accessToken = $null
if ($loginResponse -and $loginResponse.accessToken) {
    $accessToken = $loginResponse.accessToken
    Write-Host "  Access token obtained: $($accessToken.Substring(0, 50))..." -ForegroundColor Green
} else {
    Write-Host "  ⚠ Could not extract access token. Authenticated tests will fail." -ForegroundColor Yellow
}

# ============================================================
# 3. Authenticated Endpoints
# ============================================================
Write-Host "`n=== AUTHENTICATED ENDPOINTS ===" -ForegroundColor Cyan

if ($accessToken) {
    $authHeaders = @{
        "Authorization" = "Bearer $accessToken"
    }
    
    Test-Endpoint -Name "User Profile" -Method "GET" -Url "$BaseUrl/api/test/user" -Headers $authHeaders
    Test-Endpoint -Name "Chargebee Items" -Method "GET" -Url "$BaseUrl/api/test/chargebeeItems" -Headers $authHeaders
    Test-Endpoint -Name "Database Items" -Method "GET" -Url "$BaseUrl/api/test/databaseItems" -Headers $authHeaders
    
    # Test subscription endpoints
    Test-Endpoint -Name "Subscription Plans" -Method "GET" -Url "$BaseUrl/api/test/generate_pricing_page_session_url" -Headers $authHeaders
    
    # Test order endpoints
    Test-Endpoint -Name "One-Time Checkout" -Method "GET" -Url "$BaseUrl/api/test/oneTimeCheckoutPageUrl" -Headers $authHeaders
} else {
    Write-Host "  Skipping authenticated tests (no token)" -ForegroundColor Yellow
}

# ============================================================
# 4. Chargebee Integration
# ============================================================
Write-Host "`n=== CHARGEBEE INTEGRATION ===" -ForegroundColor Cyan

Test-Endpoint -Name "Chargebee Sync Status" -Method "GET" -Url "$BaseUrl/api/chargebee-sync/status"

# ============================================================
# 5. Summary
# ============================================================
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  TEST SUMMARY" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Total Tests:  $TOTAL_TESTS" -ForegroundColor White
Write-Host "Passed:       $PASSED_TESTS" -ForegroundColor Green
Write-Host "Failed:       $FAILED_TESTS" -ForegroundColor $(if ($FAILED_TESTS -eq 0) { "Green" } else { "Red" })
Write-Host ""

if ($FAILED_TESTS -eq 0) {
    Write-Host "✅ ALL TESTS PASSED! MVP is ready for beta testing." -ForegroundColor Green
} else {
    Write-Host "⚠ Some tests failed. Review errors above." -ForegroundColor Yellow
    Write-Host "  Critical failures: Login, Signup, Health Check" -ForegroundColor Red
    Write-Host "  Non-critical: Chargebee items (may be empty)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan

# Keep window open
Read-Host "Press Enter to exit"
