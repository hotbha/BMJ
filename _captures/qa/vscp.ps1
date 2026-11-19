<#
    Non-interactive scp wrapper (PuTTY pscp). Credentials read from the same
    temp file as vps.ps1 so they never appear in this script.

    Usage: vscp.ps1 -LocalFile "X:\path\to\file" -RemotePath "/home/bmj/bmj/file"
#>
param(
    [Parameter(Mandatory = $true)][string]$LocalFile,
    [Parameter(Mandatory = $true)][string]$RemotePath,
    [int]$Timeout = 300
)

$ErrorActionPreference = 'Stop'
$credFile = Join-Path $env:TEMP 'bmj_vps.cred'
$host_ = '160.250.205.241'
$user = 'bmj'
$pass = (Get-Content -LiteralPath $credFile -Raw).Trim()
$pscp = 'C:\Program Files\PuTTY\pscp.exe'

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $pscp
$psi.Arguments = "-batch -P 22 -pw `"$pass`" `"$LocalFile`" ${user}@${host_}:$RemotePath"
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.UseShellExecute = $false
$psi.CreateNoWindow = $true

$proc = [System.Diagnostics.Process]::Start($psi)
$out = $proc.StandardOutput.ReadToEnd()
$err = $proc.StandardError.ReadToEnd()
$proc.WaitForExit($Timeout * 1000) | Out-Null

if ($out) { Write-Output $out.Trim() }
if ($err) { Write-Output "stderr: $($err.Trim())" }
Write-Output "exit: $($proc.ExitCode)"
