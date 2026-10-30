#requires -Version 5.1

<#
.SYNOPSIS
    Proves subscription checkout works end to end after the Product Catalog 2.0 migration.

.DESCRIPTION
    Plan selection -> POST /api/subscriptions/create -> Chargebee hosted page.

    The only thing asserted is what the customer would experience: a signed-in
    user asks for a plan, and Chargebee returns a real hosted page URL for it.
    Nothing is paid, so no subscription, invoice or charge is created.

    The two plans used are real, active catalog 2.0 item prices verified on the
    test site (see _captures/verify_plan_prices.py):
        weekly : bmj-delight-mix-punch-200ml-weekly   INR  461.00 / 1 week
        monthly: bmj-delight-mix-punch-200ml-monthly  INR 1697.00 / 1 month

.NOTES
    Creates one QA user (and therefore one Chargebee test customer) per run,
    because /api/subscriptions/create requires an authenticated USER role and a
    Chargebee customer id — both of which a fresh signup provides.
#>

param(
    [string]$ApiBase = 'http://127.0.0.1:8085',
    [string]$OutDir = 'X:\BMJ\_captures\subscription_checkout',
    # Reused on every run so repeat runs do not create additional Chargebee customers.
    [string]$QaEmail = 'qa.sub.probe@bookmyjuice.test',
    [string]$QaPhone = '9876543210',
    [string]$QaPassword = 'QaPassw0rd!2026'
)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir | Out-Null }
$results = [ordered]@{}

function Show-Step($text) { Write-Host "[STEP] $text" -ForegroundColor Yellow }

function Invoke-Json {
    param([string]$Method, [string]$Path, $Body, $Headers)
    $args = @{
        Uri = "$ApiBase$Path"; Method = $Method; UseBasicParsing = $true
        ContentType = 'application/json'; TimeoutSec = 60
    }
    if ($Body) { $args.Body = ($Body | ConvertTo-Json -Depth 6) }
    if ($Headers) { $args.Headers = $Headers }
    try {
        $r = Invoke-WebRequest @args
        return [pscustomobject]@{ Status = [int]$r.StatusCode; Body = $r.Content }
    } catch {
        $status = $null
        $content = $null
        if ($_.Exception.Response) {
            $status = [int]$_.Exception.Response.StatusCode
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $content = $reader.ReadToEnd()
            $reader.Dispose()
        } else {
            $content = $_.Exception.Message
        }
        return [pscustomobject]@{ Status = $status; Body = $content }
    }
}

# --- 1. Ensure the QA user exists (first run creates it + its Chargebee customer)
Show-Step "Ensure QA user $QaEmail"
$signup = Invoke-Json -Method Post -Path '/api/auth/signup' -Body @{
    email = $QaEmail; password = $QaPassword
    firstName = 'QA'; lastName = 'Subscription'; phone = $QaPhone
}
if ($signup.Status -eq 200) {
    Write-Host "       created: $($signup.Body)"
} elseif ($signup.Body -match 'already registered') {
    Write-Host '       already exists, reusing'
} else {
    Write-Host "       signup returned $($signup.Status): $($signup.Body)" -ForegroundColor Red
    $results.signup = "FAILED $($signup.Status): $($signup.Body)"
    $results | ConvertTo-Json -Depth 6 | Tee-Object -FilePath (Join-Path $OutDir 'result.json')
    exit 1
}
$results.signup = $signup.Status

# --- 2. Sign in for a JWT ----------------------------------------------------
Show-Step 'Signin'
$signin = Invoke-Json -Method Post -Path '/api/auth/signin' -Body @{
    username = $QaPhone; password = $QaPassword
}
if ($signin.Status -ne 200) {
    Write-Host "       signin FAILED $($signin.Status): $($signin.Body)" -ForegroundColor Red
    $results.signin = "FAILED $($signin.Status): $($signin.Body)"
    $results | ConvertTo-Json -Depth 6 | Tee-Object -FilePath (Join-Path $OutDir 'result.json')
    exit 1
}
$session = $signin.Body | ConvertFrom-Json
$token = if ($session.accessToken) { $session.accessToken } else { $session.token }
$headers = @{ Authorization = "Bearer $token" }
Write-Host "       jwt for user id $($session.id) roles=$($session.roles -join ',')"
$results.userId = $session.id
$results.userEmail = $session.email
$results.roles = $session.roles

# --- 3. Plan selection -> subscription checkout, weekly + monthly ------------
$plans = @(
    @{ key = 'weekly'; id = 'bmj-delight-mix-punch-200ml-weekly'; expected = 'INR 461.00 / 1 week' },
    @{ key = 'monthly'; id = 'bmj-delight-mix-punch-200ml-monthly'; expected = 'INR 1697.00 / 1 month' }
)

$schedule = @{ monday = $true; wednesday = $true; friday = $true }

foreach ($plan in $plans) {
    Show-Step "POST /api/subscriptions/create planId=$($plan.id)"
    $response = Invoke-Json -Method Post -Path '/api/subscriptions/create' -Headers $headers `
        -Body @{ planId = $plan.id; schedule = $schedule }

    if ($response.Status -eq 200) {
        $page = $response.Body | ConvertFrom-Json
        $response.Body | Set-Content -Path (Join-Path $OutDir "$($plan.key)-create.json")
        Write-Host "       hostedPageId = $($page.hostedPageId)"
        Write-Host "       subscriptionId (reserved) = $($page.subscriptionId)"
        Write-Host "       url = $($page.url)" -ForegroundColor Green
        $results[$plan.key] = [ordered]@{
            planId         = $plan.id
            expectedPrice  = $plan.expected
            status         = $page.status
            hostedPageId   = $page.hostedPageId
            subscriptionId = $page.subscriptionId
            url            = $page.url
        }
    } else {
        Write-Host "       FAILED $($response.Status): $($response.Body)" -ForegroundColor Red
        $results[$plan.key] = [ordered]@{
            planId = $plan.id; status = 'FAILED'
            httpStatus = $response.Status; error = $response.Body
        }
    }
}

$results | ConvertTo-Json -Depth 6 | Tee-Object -FilePath (Join-Path $OutDir 'result.json')
