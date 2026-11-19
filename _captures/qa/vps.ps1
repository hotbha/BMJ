<#
    Thin wrapper around PuTTY's plink for non-interactive, password-based SSH.
    Credentials are read from a file OUTSIDE the repository so they can never be
    committed. The password is never echoed, never written to a log, and never
    placed in this script.

    Usage:
        vps.ps1 -Command "hostname; uptime"
        vps.ps1 -Command "docker ps" -Timeout 60
#>
param(
    [Parameter(Mandatory = $true)][string]$Command,
    [int]$Timeout = 60
)

$ErrorActionPreference = 'Stop'

$credFile = Join-Path $env:TEMP 'bmj_vps.cred'
$host_; $user = 'bmj', '160.250.205.241'
if (-not (Test-Path -LiteralPath $credFile)) {
    Write-Error "credential file not found: $credFile"
    exit 2
}
$pass = (Get-Content -LiteralPath $credFile -Raw).Trim()

$plink = 'C:\Program Files\PuTTY\plink.exe'
if (-not (Test-Path -LiteralPath $plink)) { Write-Error 'plink not found'; exit 2 }

# -batch would reject an unknown host key, so accept it once by piping "y".
$answer = "y`n"
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $plink
$psi.Arguments = "-ssh -P 22 -l $user -pw `"$pass`" $host_ `"$Command`""
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.RedirectStandardInput = $true
$psi.UseShellExecute = $false
$psi.CreateNoWindow = $true

$proc = [System.Diagnostics.Process]::Start($psi)
$proc.StandardInput.WriteLine($answer)
$proc.StandardInput.Flush()

$out = $proc.StandardOutput.ReadToEnd()
$err = $proc.StandardError.ReadToEnd()
if (-not $proc.WaitForExit($Timeout * 1000)) {
    try { $proc.Kill() } catch { }
    Write-Output '--- TIMEOUT ---'
}

# plink prints the host-key prompt on stderr; that is expected on first contact.
if ($err) { Write-Output "--- stderr ---"; Write-Output $err.Trim() }
if ($out) { Write-Output $out.Trim() }
Write-Output "--- exit: $($proc.ExitCode) ---"
