#requires -Version 5.1

<#
.SYNOPSIS
    Stops the BMJ backend started by ops\run_local_server.ps1.

.DESCRIPTION
    Finds the process listening on the given port and stops it. Only java processes (and the
    cmd.exe/Maven wrapper spawned by run_local_server.ps1) are targeted, so an unrelated
    service squatting on the port is never killed.

.PARAMETER Port
    Port the backend was started on (default 8085).

.PARAMETER Force
    Also stop processes that are not java/mvn/cmd.

.EXAMPLE
    .\ops\stop_local_server.ps1 -Port 8085
#>

param(
    [int]$Port = 8085,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

$listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $listener) {
    Write-Host "[STOP] Nothing is listening on port $Port." -ForegroundColor Yellow
} else {
    $proc = Get-Process -Id $listener.OwningProcess -ErrorAction SilentlyContinue
    if (-not $proc) {
        Write-Host "[STOP] Port $Port is held by PID $($listener.OwningProcess) which cannot be resolved." -ForegroundColor Yellow
    } else {
        $isTarget = ($proc.ProcessName -like 'java*') -or ($proc.ProcessName -eq 'mvn') -or
                    ($proc.ProcessName -eq 'mvnw') -or ($proc.ProcessName -eq 'cmd')
        if (-not $isTarget -and -not $Force) {
            Write-Host "[STOP] Port $Port is owned by '$($proc.ProcessName)' (PID $($proc.Id)), not the BMJ backend. Use -Force to stop it anyway." -ForegroundColor Red
            exit 1
        }
        Write-Host "[STOP] Stopping $($proc.ProcessName) (PID $($proc.Id)) on port $Port" -ForegroundColor Yellow
        Stop-Process -Id $proc.Id -Force
        Start-Sleep -Seconds 3
    }
}

# Spring Boot's fork keeps the port after the wrapper exits - make sure it is really gone.
Start-Sleep -Seconds 2
$still = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($still) {
    Write-Host "[STOP] Port $Port is still held by PID $($still[0].OwningProcess)." -ForegroundColor Red
    exit 1
}

Write-Host "[STOP] Port $Port is free." -ForegroundColor Green
