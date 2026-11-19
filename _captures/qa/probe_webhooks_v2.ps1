<#
    Webhook endpoint verification after the 865fb16 deployment.

    Columns:
      noauth   -> expect 401 (endpoint protected)
      wrongpw  -> expect 401 (password really checked)
      noid     -> expect 400 (NEW: malformed body rejected before the controller)
      fakeid   -> expect 500 (request reaches the controller; Event.retrieve fails on a fake id)
#>
$ErrorActionPreference = 'Stop'
$lines = Get-Content -LiteralPath (Join-Path $env:TEMP 'bmj_webhook.cred')
$pass = $lines[0].Trim(); $user = $lines[1].Trim()

$paths = @(
    '/api/webhooks/customers',
    '/api/webhooks/subscriptions',
    '/api/webhooks/items',
    '/api/webhooks/item-prices',
    '/api/webhooks/orders'
)

function Status([string]$path, $headers, [string]$body) {
    try {
        $r = Invoke-WebRequest -Uri "https://api.bookmyjuice.co.in$path" -Method Post `
            -ContentType 'application/json' -Body $body -Headers $headers -TimeoutSec 25 -UseBasicParsing
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

$auth = Basic $user $pass
$bad = Basic $user 'definitely-not-the-password'

'{0,-32} {1,7} {2,8} {3,6} {4,8}' -f 'endpoint', 'noauth', 'wrongpw', 'noid', 'fakeid'
foreach ($p in $paths) {
    $a = Status $p @{}            '{"id":"x"}'
    $b = Status $p $bad           '{"id":"x"}'
    $c = Status $p $auth          '{}'
    $d = Status $p $auth          '{"id":"probe-not-a-real-event"}'
    '{0,-32} {1,7} {2,8} {3,6} {4,8}' -f $p, $a, $b, $c, $d
}
