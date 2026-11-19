<#
    Build the VPS .env from the workstation .env, generating fresh secrets.
    Prints only a structural validation (key names + value length), never values.
#>
$ErrorActionPreference = 'Stop'

$src = @{}
Get-Content 'X:\BMJ\.env' | Where-Object { $_ -match '^[A-Z0-9_]+=' } | ForEach-Object {
    $i = $_.IndexOf('=')
    $src[$_.Substring(0, $i)] = $_.Substring($i + 1).Trim()
}

function New-Secret {
    $chars = (48..57) + (65..90) + (97..122)
    -join ($chars | Get-Random -Count 32 | ForEach-Object { [char]$_ })
}

$lines = New-Object System.Collections.Generic.List[string]
$lines.Add('DB_NAME=bmj_db')
$lines.Add('DB_USERNAME=bmj')
$lines.Add('DB_PASSWORD=' + (New-Secret))
$lines.Add('DB_ROOT_PASSWORD=' + (New-Secret))
$lines.Add('CHARGEBEE_SITE=' + $src['CHARGEBEE_SITE'])
$lines.Add('CHARGEBEE_API_KEY=' + $src['CHARGEBEE_API_KEY'])
$lines.Add('WEBHOOK_USERNAME=' + $src['WEBHOOK_USERNAME'])
$lines.Add('WEBHOOK_PASSWORD=' + $src['WEBHOOK_PASSWORD'])
$lines.Add('ADMIN_USER=bmjadmin')
$lines.Add('ADMIN_PASSWORD=' + (New-Secret))

$out = Join-Path $env:TEMP 'bmj_vps.env'
[System.IO.File]::WriteAllLines($out, $lines, (New-Object System.Text.UTF8Encoding($false)))

# Structural validation only: every line must be KEY=value, no empty values.
$bad = 0
foreach ($l in [System.IO.File]::ReadAllLines($out)) {
    if ($l -notmatch '^[A-Z0-9_]+=.+$') {
        Write-Output "MALFORMED: $l"
        $bad++
    }
}
Write-Output "lines=$($lines.Count) malformed=$bad"
foreach ($l in [System.IO.File]::ReadAllLines($out)) {
    $i = $l.IndexOf('=')
    $k = $l.Substring(0, $i)
    $v = $l.Substring($i + 1)
    $kind = if ($k -match 'PASSWORD|API_KEY') { 'secret' } else { 'plain ' }
    Write-Output ("{0} {1,-20} len={2}" -f $kind, $k, $v.Length)
}
