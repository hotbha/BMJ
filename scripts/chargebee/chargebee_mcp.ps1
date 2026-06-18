param(
    [Parameter(Mandatory=$true)]
    [string]$Action,
    [string]$SessionId = "",
    [string]$MethodName = "",
    [string]$Params = "{}"
)

$token = "test_ai_-ZFEjZ3qiK2mW3k7C9M2Q60OK2QmLslRdSnNWt61z4E"
$baseUrl = "https://bookmyjuice-test.mcp.chargebee.com/onboarding_agent"

function New-Session {
    $body = @{
        jsonrpc = "2.0"
        id = 1
        method = "initialize"
        params = @{
            protocolVersion = "2024-11-05"
            capabilities = @{}
            clientInfo = @{
                name = "curl-client"
                version = "1.0.0"
            }
        }
    } | ConvertTo-Json -Compress

    $response = Invoke-WebRequest -UseBasicParsing -Uri $baseUrl -Method Post -Headers @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
        "Accept" = "text/event-stream"
    } -Body $body -TimeoutSec 15

    return $response.Content
}

function Get-Tools {
    param([string]$sessionId)
    $body = @{
        jsonrpc = "2.0"
        id = 2
        method = "tools/list"
        params = @{}
    } | ConvertTo-Json -Compress

    $response = Invoke-WebRequest -UseBasicParsing -Uri $baseUrl -Method Post -Headers @{
        "Authorization" = "Bearer $token"
        "mcp-session-id" = $sessionId
        "Content-Type" = "application/json"
        "Accept" = "text/event-stream"
    } -Body $body -TimeoutSec 15

    return $response.Content
}

function Call-Tool {
    param([string]$sessionId, [string]$methodName, [string]$paramsJson)
    $body = @{
        jsonrpc = "2.0"
        id = 3
        method = "tools/call"
        params = @{
            name = $methodName
            arguments = ($paramsJson | ConvertFrom-Json)
        }
    } | ConvertTo-Json -Compress -Depth 10

    $response = Invoke-WebRequest -UseBasicParsing -Uri $baseUrl -Method Post -Headers @{
        "Authorization" = "Bearer $token"
        "mcp-session-id" = $sessionId
        "Content-Type" = "application/json"
        "Accept" = "text/event-stream"
    } -Body $body -TimeoutSec 30

    return $response.Content
}

switch ($Action) {
    "new-session" {
        New-Session
    }
    "get-tools" {
        Get-Tools -sessionId $SessionId
    }
    "call-tool" {
        Call-Tool -sessionId $SessionId -methodName $MethodName -paramsJson $Params
    }
    default {
        Write-Host "Usage: .\chargebee_mcp.ps1 -Action new-session|get-tools|call-tool"
    }
}
