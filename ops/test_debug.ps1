$ErrorActionPreference = 'Continue'

Write-Host ""
Write-Host "=== TEST RESULTS ===" -ForegroundColor Cyan
Write-Host ""

$BaseUrl = "http://127.0.0.1:8080"
$AdminEmail = "support@bookmyjuice.co.in"
$AdminPassword = "testpass123"

# TEST 1: Signin
Write-Host "[TEST 1] Signing in to get JWT..."
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
    Write-Host "[PASS] JWT obtained" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Signin failed" -ForegroundColor Red
    $jwt = $null
}

Write-Host ""

if ($jwt) {
    $headers = @{ Authorization = "Bearer $jwt" }
    
    # TEST 2: Subscriptions pricing
    Write-Host "[TEST 2] Testing subscriptions pricing plans..."
    try {
        $response = Invoke-WebRequest -Method GET `
            -Uri "$BaseUrl/api/subscriptions/pricing/plans" `
            -Headers $headers `
            -UseBasicParsing `
            -ErrorAction Stop
        Write-Host "[PASS] Response: $($response.Content.Substring(0, 100))..." -ForegroundColor Green
    } catch {
        Write-Host "[FAIL] Error: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
        if ($_.Exception.Response) {
            try {
                $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
                $errorBody = $reader.ReadToEnd()
                Write-Host "Details: $errorBody" -ForegroundColor Yellow
            } catch { }
        }
    }
    
    Write-Host ""
    
    # TEST 3: Pricing page
    Write-Host "[TEST 3] Testing hosted pricing page URLs..."
    try {
        $response = Invoke-WebRequest -Method GET `
            -Uri "$BaseUrl/api/subscriptions/pricing-page" `
            -Headers $headers `
            -UseBasicParsing `
            -ErrorAction Stop
        Write-Host "[PASS] Response received" -ForegroundColor Green
    } catch {
        Write-Host "[FAIL] Error: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
        if ($_.Exception.Response) {
            try {
                $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
                $errorBody = $reader.ReadToEnd()
                Write-Host "Details: $errorBody" -ForegroundColor Yellow
            } catch { }
        }
    }
}

Write-Host ""
Write-Host "=== Done ===" -ForegroundColor Cyan
