# Helper to get a new Chargebee MCP session
$token = "test_ai_-ZFEjZ3qiK2mW3k7C9M2Q60OK2QmLslRdSnNWt61z4E"
$baseUrl = "https://bookmyjuice-test.mcp.chargebee.com/onboarding_agent"

$body = @{
    jsonrpc = "2.0"
    id = 1
    method = "initialize"
    params = @{
        protocolVersion = "2024-11-05"
        capabilities = @{}
        clientInfo = @{
            name = "ps-session"
            version = "1.0.0"
        }
    }
} | ConvertTo-Json -Compress

try {
    $response = Invoke-WebRequest -Uri $baseUrl -Method Post -UseBasicParsing -Headers @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
        "Accept" = "text/event-stream"
    } -Body $body -TimeoutSec 15

    Write-Host "=== RESPONSE HEADERS ==="
    $response.Headers | Format-List | Out-String | Write-Host
    Write-Host "=== RAW CONTENT ==="
    Write-Host $response.Content
} catch {
    Write-Host "Error: $_"
    if ($_.Exception.Response) {
        Write-Host "Status: $($_.Exception.Response.StatusCode)"
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        Write-Host "Body: $($reader.ReadToEnd())"
    }
}
