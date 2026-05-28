param([string]$SessionId, [string]$PayloadFile = "batch1_generic_plans.json")
$token = "test_ai_-ZFEjZ3qiK2mW3k7C9M2Q60OK2QmLslRdSnNWt61z4E"
$baseUrl = "https://bookmyjuice-test.mcp.chargebee.com/onboarding_agent"

$payloadJson = Get-Content -Path $PayloadFile -Raw
$innerArgs = $payloadJson | ConvertFrom-Json

$body = @{
    jsonrpc = "2.0"
    id = 3
    method = "tools/call"
    params = @{
        name = "import_product_catalog"
        arguments = $innerArgs
    }
} | ConvertTo-Json -Compress -Depth 10

Write-Host "Calling import_product_catalog..."
$response = Invoke-WebRequest -UseBasicParsing -Uri $baseUrl -Method Post -Headers @{
    "Authorization" = "Bearer $token"
    "mcp-session-id" = $SessionId
    "Content-Type" = "application/json"
    "Accept" = "text/event-stream"
} -Body $body -TimeoutSec 60

Write-Host $response.Content