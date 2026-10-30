#Requires -Version 5.1
<#
.SYNOPSIS
    B5 launch smoke test for BookMyJuice V1 - exercises the release artifact over HTTP.

.DESCRIPTION
    Runs the 11-probe battery from PRODUCTION_READINESS_REPORT.md section 3 / B5_SMOKE_TEST_PLAN.md.
    READ-ONLY with respect to Chargebee: it never creates, pauses, resumes or cancels anything.
    Probe 8 additionally asserts the PR-14 regression (no password hash in /api/user/profile).
    Exits with the number of failed probes (0 = all green).

.PARAMETER BaseUrl
    Backend root, e.g. http://127.0.0.1:8085 (local) or https://api.<host> (deployed).

.PARAMETER Username
    Account used for probes 7-10. Defaults to the V6-seeded test account.

.PARAMETER Password
    Password for that account.

.PARAMETER Seeded
    Set when the account genuinely exists with a chargebee_customer_id, so probe 9 is a hard
    failure instead of a known-caveat warning (PR-15).

.EXAMPLE
    powershell -File ops\smoke_test.ps1 -BaseUrl http://127.0.0.1:8085

.EXAMPLE
    powershell -File ops\smoke_test.ps1 -BaseUrl https://api.bookmyjuice.example -Seeded
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$BaseUrl,
    [string]$Username = '9999999901',
    [string]$Password = 'Test@1234',
    [switch]$Seeded
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'   # Invoke-WebRequest's progress bar corrupts captured output
$BaseUrl = $BaseUrl.TrimEnd('/')
$script:passed = 0
$script:failed = 0
$script:warned = 0
$script:notes = New-Object System.Collections.Generic.List[string]

function Get-Snippet {
    param([string]$Text)
    if (-not $Text) { return '' }
    $flat = ($Text -replace '\s+', ' ').Trim()
    if ($flat.Length -gt 76) { return $flat.Substring(0, 76) + '...' }
    return $flat
}

function Write-Result {
    param([string]$Tag, [string]$Name, [string]$Detail)
    $colour = switch ($Tag) { 'PASS' { 'Green' } 'FAIL' { 'Red' } default { 'Yellow' } }
    Write-Host ('  [{0}] {1,-46} {2}' -f $Tag, $Name, $Detail) -ForegroundColor $colour
}

# Returns @{ Code = <int>; Body = <string> } and never throws on 4xx/5xx.
function Invoke-Probe {
    param([string]$Method, [string]$Path, [string]$Body, [hashtable]$Headers)
    $req = @{ Method = $Method; Uri = ($BaseUrl + $Path); TimeoutSec = 30; UseBasicParsing = $true }
    if ($Body) { $req.ContentType = 'application/json'; $req.Body = $Body }
    if ($Headers) { $req.Headers = $Headers }
    try {
        $r = Invoke-WebRequest @req
        return @{ Code = [int]$r.StatusCode; Body = [string]$r.Content }
    }
    catch {
        $code = 0
        $text = ''
        try { $code = [int]$_.Exception.Response.StatusCode.value__ } catch { }
        try {
            $stream = $_.Exception.Response.GetResponseStream()
            if ($stream) { $text = (New-Object System.IO.StreamReader($stream)).ReadToEnd() }
        } catch { }
        if (-not $text) { $text = $_.Exception.Message }
        return @{ Code = $code; Body = $text }
    }
}

function Assert-Probe {
    param(
        [string]$Name, [int]$Expected, [hashtable]$Result,
        [string]$MustContain, [string]$MustNotContain, [switch]$Caveat401
    )
    $ok = ($Result.Code -eq $Expected)

    # Use ordinal IndexOf, not -like: the payload contains '[' and ']', which -like
    # interprets as wildcard character classes and throws WildcardPatternException.
    if ($ok -and $MustContain) {
        if ($Result.Body.IndexOf($MustContain, [StringComparison]::Ordinal) -lt 0) { $ok = $false }
    }
    if ($ok -and $MustNotContain) {
        if ($Result.Body.IndexOf($MustNotContain, [StringComparison]::Ordinal) -ge 0) { $ok = $false }
    }

    if ($ok) {
        $script:passed++
        Write-Result 'PASS' $Name ('{0} {1}' -f $Result.Code, (Get-Snippet $Result.Body))
        return
    }
    # Known caveat: authed /api/subscriptions/my returns 401 when chargebee_customer_id is null (PR-15)
    if ($Caveat401 -and $Result.Code -eq 401 -and
        $Result.Body.IndexOf('User not authenticated', [StringComparison]::Ordinal) -ge 0 -and -not $Seeded) {
        $script:warned++
        $script:notes.Add("$Name returned 401 'User not authenticated' - known PR-15 caveat (no chargebee_customer_id on this account).")
        Write-Result 'WARN' $Name '401 - known PR-15 caveat, see report'
        return
    }
    $script:failed++
    Write-Result 'FAIL' $Name ('expected {0}, got {1} {2}' -f $Expected, $Result.Code, (Get-Snippet $Result.Body))
}

Write-Host ''
Write-Host "B5 launch smoke - $BaseUrl" -ForegroundColor Cyan
Write-Host ('-' * 78) -ForegroundColor DarkGray

# --- 1. health --------------------------------------------------------------------------
$r = Invoke-Probe GET '/api/health' $null $null
Assert-Probe -Name 'GET /api/health' -Expected 200 -Result $r -MustContain 'UP'

# --- 2. catalog (flow 1; served by CatalogController - see PR-1) ------------------------
$r = Invoke-Probe GET '/api/v1/catalog/charge-items' $null $null
Assert-Probe -Name 'GET /api/v1/catalog/charge-items' -Expected 200 -Result $r -MustContain 'itemId'

# --- 2b. catalog payload must carry PRICES, not just items (PR-16/PR-17/PR-18) ------------
# A 200 with "prices":[] is a store that cannot be bought from - assert on payload, not status.
# This probe CANNOT pass until PR-18 is closed: the census (report section 3.5) found 0 of the
# 15 bmj-item-* items carrying an ItemPrice, so even a correct limit(100) returns "prices":[].
# A failure here is therefore expected - the probe is the gate working, not a broken probe.
$r = Invoke-Probe GET '/api/v1/catalog/charge-items' $null $null
Assert-Probe -Name 'catalog items carry prices' -Expected 200 -Result $r -MustContain '"prices":[' -MustNotContain '"prices":[]'

# --- 3-4. B2 closure: anonymous test-order routes must be gone ---------------------------
$r = Invoke-Probe GET '/api/test/orders' $null $null
Assert-Probe -Name 'GET /api/test/orders (anon, must be gone)' -Expected 404 -Result $r

$r = Invoke-Probe GET '/api/test/ordersByCustomerId' $null $null
Assert-Probe -Name 'GET /api/test/ordersByCustomerId (anon, gone)' -Expected 404 -Result $r

# --- 5-6. protected flows reject anonymous callers ---------------------------------------
$r = Invoke-Probe GET '/api/subscriptions/my' $null $null
Assert-Probe -Name 'GET /api/subscriptions/my (anon)' -Expected 401 -Result $r

$r = Invoke-Probe GET '/api/orders/by-customer' $null $null
Assert-Probe -Name 'GET /api/orders/by-customer (anon)' -Expected 401 -Result $r

# --- 7. password sign-in (creates NO Chargebee customer - safe) --------------------------
$signinBody = ('{{"username":"{0}","password":"{1}"}}' -f $Username, $Password)
$r = Invoke-Probe POST '/api/auth/signin' $signinBody $null
Assert-Probe -Name "POST /api/auth/signin ($Username)" -Expected 200 -Result $r -MustContain 'token'

$token = $null
if ($r.Code -eq 200) {
    try {
        $j = $r.Body | ConvertFrom-Json
        $token = $j.accessToken
        if (-not $token) { $token = $j.token }
    } catch { }
}
if (-not $token) {
    Write-Host ''
    Write-Host 'No JWT obtained - probes 8-10 skipped.' -ForegroundColor Red
    Write-Host ("Result: {0} passed, {1} failed, {2} warnings" -f $script:passed, $script:failed, $script:warned)
    exit ($script:failed + 1)
}
$auth = @{ Authorization = ('Bearer ' + $token) }

# --- 8. profile must NOT leak the credential hash (PR-14) --------------------------------
$r = Invoke-Probe GET '/api/user/profile' $null $auth
Assert-Probe -Name 'GET /api/user/profile (no hash leak)' -Expected 200 -Result $r -MustNotContain '"password"'

# --- 9. subscriptions for the signed-in account ------------------------------------------
$r = Invoke-Probe GET '/api/subscriptions/my' $null $auth
Assert-Probe -Name 'GET /api/subscriptions/my (auth)' -Expected 200 -Result $r -Caveat401

# --- 10. orders for the signed-in account (D-6 null handling) ------------------------------
$r = Invoke-Probe GET '/api/orders/by-customer' $null $auth
Assert-Probe -Name 'GET /api/orders/by-customer (auth)' -Expected 200 -Result $r

Write-Host ('-' * 78) -ForegroundColor DarkGray
foreach ($n in $script:notes) { Write-Host ("  note: {0}" -f $n) -ForegroundColor Yellow }
$colour = if ($script:failed -eq 0) { 'Green' } else { 'Red' }
Write-Host ("Result: {0} passed, {1} failed, {2} warnings" -f $script:passed, $script:failed, $script:warned) -ForegroundColor $colour
Write-Host ''
exit $script:failed

