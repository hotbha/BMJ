#requires -Version 5.1

<#
.SYNOPSIS
    Detects your current active WiFi/Ethernet IPv4 address for full-stack testing.
.DESCRIPTION
    This script finds your machine's active IPv4 address on the network.
    Use it to determine what IP to use when testing on a physical phone.
    
    For Android emulator, always use: 10.0.2.2
    For physical device on same WiFi, use the IP this script returns.
.EXAMPLE
    .\ops\find_active_ip.ps1
    Returns: 10.77.221.139
#>

$ErrorActionPreference = 'Stop'

try {
    # Get all IPv4 addresses, filtering out 127.0.0.1 and Docker/virtual adapter ranges
    $ip = Get-NetIPAddress -AddressFamily IPv4 -PrefixOrigin Dhcp |
        Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '172.*' -and $_.IPAddress -notlike '169.254.*' } |
        Select-Object -First 1 -ExpandProperty IPAddress
    
    if (-not $ip) {
        # Fallback: try any non-loopback IPv4
        $ip = Get-NetIPAddress -AddressFamily IPv4 |
            Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*' } |
            Select-Object -First 1 -ExpandProperty IPAddress
    }
    
    if ($ip) {
        Write-Output $ip
    } else {
        Write-Error "Could not detect active IP address."
        exit 1
    }
} catch {
    Write-Error "Error detecting IP: $_"
    exit 1
}
