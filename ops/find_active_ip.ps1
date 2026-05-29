<#
.SYNOPSIS
    Detects your current active WiFi IPv4 address for full-stack testing.
.DESCRIPTION
    Prefers Wi-Fi adapter over Ethernet. Filters out virtual adapters.
    Use it to determine what IP to use when testing on a physical phone.

    For Android emulator, always use: 10.0.2.2
    For physical device on same WiFi, use the IP this script returns.
.EXAMPLE
    .\ops\find_active_ip.ps1
    Returns: 10.77.221.139
#>

$ErrorActionPreference = 'Stop'

try {
    $ip = Get-NetIPAddress -AddressFamily IPv4 |
      Where-Object {
        $_.IPAddress -notlike '127.*' -and
        $_.IPAddress -notlike '169.254.*' -and
        ($_.IPAddress -like '10.*' -or $_.IPAddress -like '192.168.*') -and
        $_.InterfaceAlias -notlike '*vEthernet*' -and
        $_.InterfaceAlias -notlike '*VMware*' -and
        $_.InterfaceAlias -notlike '*VPN*' -and
        $_.InterfaceAlias -notlike '*Tailscale*' -and
        $_.InterfaceAlias -notlike '*Loopback*'
      } |
      Sort-Object {
        if ($_.InterfaceAlias -like '*Wi-Fi*') { 0 }
        elseif ($_.InterfaceAlias -like '*Wireless*') { 1 }
        else { 2 }
      } |
      Select-Object -First 1 -ExpandProperty IPAddress

    if ($ip) {
        Write-Host $ip
    } else {
        Write-Error "No WiFi IP found. Connect phone and laptop to same WiFi."
        exit 1
    }
} catch {
    Write-Error "Error detecting IP: $_"
    exit 1
}