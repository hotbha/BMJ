$ErrorActionPreference = 'Continue'

Write-Host ""
Write-Host "=== BookMyJuice Full-Stack Tests ===" -ForegroundColor Cyan
Write-Host ""

$BaseUrl = "http://127.0.0.1:8080"
$AdminEmail = "support@bookmyjuice.co.in"
$AdminPassword = "testpass123"
$WebhookUser = "support@bookmyjuice.co.in"
$WebhookPass = "rADHASOAMI@0"

function Test-Endpoint {
    param(
        [int]$TestNum,
        [string]$TestName,
        [string]$Method,
        [string]$Url,
        [object]$Body,
        [hashtable]$Headers
    )
    
    Write-Host "[TEST $TestNum] $TestName..." -ForegroundColor Yellow
    
    try {
        $params = @{
            Method = $Method
            Uri = $Url
            ContentType = "application/json"
            UseBasicParsing = $true
            ErrorAction = "Stop"
        }
        
        if ($Body) {
            if ($Body -is [hashtable]) {
                $params["Body"] = $Body | ConvertTo-Json
            } else {
                $params["Body"] = $Body
            }
        }
        
        if ($Headers) {
            $params["Headers"] = $Headers
        }
        
        $response = Invoke-WebRequest @params
        Write-Host "✓ Test $TestNum passed" -ForegroundColor Green
        return $response.Content | ConvertFrom-Json
    } catch {
        Write-Host "✗ Test $TestNum failed: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# TEST 1: Signin to get JWT
Write-Host ""
$loginBody = @{
    username = $AdminEmail
    password = $AdminPassword
}
$signinResponse = Test-Endpoint -TestNum 1 -TestName "Signing in to get JWT" `
    -Method "POST" -Url "$BaseUrl/api/auth/signin" -Body $loginBody

if ($signinResponse -and $signinResponse.accessToken) {
    $jwt = $signinResponse.accessToken
    Write-Host "JWT obtained successfully" -ForegroundColor Cyan
    Write-Host ""
    
    # TEST 2: Get subscription pricing plans
    $headers = @{ Authorization = "Bearer $jwt" }
    Test-Endpoint -TestNum 2 -TestName "Testing subscriptions pricing plans" `
        -Method "GET" -Url "$BaseUrl/api/subscriptions/pricing/plans" -Headers $headers | Out-Null
    Write-Host ""
    
    # TEST 3: Get hosted pricing page URLs
    Test-Endpoint -TestNum 3 -TestName "Testing hosted pricing page URLs" `
        -Method "GET" -Url "$BaseUrl/api/subscriptions/pricing-page" -Headers $headers | Out-Null
    Write-Host ""
    
    # TEST 4: Get local order history
    Test-Endpoint -TestNum 4 -TestName "Testing local order history" `
        -Method "GET" -Url "$BaseUrl/api/orders/local/history" -Headers $headers | Out-Null
    Write-Host ""
    
    # TEST 5: Get invoice (sample ID)
    Test-Endpoint -TestNum 5 -TestName "Testing invoice fetch (sample id)" `
        -Method "GET" -Url "$BaseUrl/api/invoices/1" -Headers $headers | Out-Null
    Write-Host ""
} else {
    Write-Host "Cannot proceed with authenticated tests - signin failed" -ForegroundColor Red
}

# TEST 6: Webhook subscription (Basic Auth)
Write-Host ""
$webhookBody = @{
    event_type = "subscription_created"
    event_id = "test_123"
}
$basicAuth = "$WebhookUser`:$WebhookPass"
$webhookHeaders = @{ Authorization = "Basic " + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($basicAuth)) }
Test-Endpoint -TestNum 6 -TestName "Testing subscription webhook with Basic Auth" `
    -Method "POST" -Url "$BaseUrl/api/webhooks/subscriptions" -Body $webhookBody -Headers $webhookHeaders | Out-Null

Write-Host ""
Write-Host "=== Tests Complete ===" -ForegroundColor Cyan
Write-Host ""
