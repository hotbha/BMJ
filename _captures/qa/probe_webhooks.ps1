<#
    Probe the five Chargebee webhook endpoints on the VPS.

    For each endpoint it reports three status codes:
      noauth      -> must be 401  (the endpoint is protected)
      wrongpass   -> must be 401  (credentials are actually checked)
      authorised  -> must NOT be 401 (the request reaches the controller)

    Credentials are read from a temp file, never embedded here.
#>
$ErrorActionPreference = 'Stop'
$credFile = Join-Path $env:TEMP 'bmj_webhook.cred'
$lines = Get-Content -LiteralPath $credFile
$pass = $lines[0].Trim()
$user = $lines[1].Trim()

$paths = @(
    '/api/webhooks/customers',
    '/api/webhooks/subscriptions',
    '/api/webhooks/items',
    '/api/webhooks/item-prices',
    '/api/webhooks/orders'
)

function Status([string]$path, $headers) {
    $uri = "https://api.bookmyjuice.co.in$path"
    try {
        $r = Invoke-WebRequest -Uri $uri -Method Post -ContentType 'application/json' `
            -Body '{"id":"probe-not-a-real-event"}' -Headers $headers -TimeoutSec 20 -UseBasicParsing
        return $r.StatusCode
    } catch {
        if ($_.Exception.Response) { return [int]$_.Exception.Response.StatusCode }
        return "ERR"
    }
}

function Basic([string]$u, [string]$p) {
    $b = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${u}:${p}"))
    return @{ Authorization = "Basic $b" }
}

Write-Output ("{0,-32} {1,8} {2,10} {3,12}" -f 'endpoint', 'noauth', 'wrongpass', 'authorised')
foreach ($p in $paths) {
    $noauth = Status $p @{}
    $wrong = Status $p (Basic $user 'definitely-not-the-password')
    $ok = Status $p (Basic $user $pass)
    Write-Output ("{0,-32} {1,8} {2,10} {3,12}" -f $p, $noauth, $wrong, $ok)
}
