$ErrorActionPreference = 'Continue'
try {
    $r = Invoke-WebRequest -Uri 'https://api.bookmyjuice.co.in/api/health' -TimeoutSec 20 -UseBasicParsing
    $out = "health: HTTP $($r.StatusCode) :: $($r.Content)"
} catch {
    $out = "health: FAILED - $($_.Exception.Message)"
}
try {
    $c = Invoke-WebRequest -Uri 'https://api.bookmyjuice.co.in/api/catalog/charge-items' -TimeoutSec 25 -UseBasicParsing
    $out += "`ncatalog: HTTP $($c.StatusCode) :: $($c.RawContentLength) bytes"
} catch {
    $out += "`ncatalog: FAILED - $($_.Exception.Message)"
}
$out
