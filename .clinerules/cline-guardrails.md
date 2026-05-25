# Windows Environment Rules

Always assume the local terminal environment is Windows PowerShell.
Do not use Linux/Bash shorthand command syntax like `curl -s`.
Instead, always use native PowerShell commands like `Invoke-WebRequest` or use `curl.exe` explicitly to avoid execution hangs.

# Chargebee Account Access

use chargebee mcp like this:
-> Get a session id with this command: curl.exe -v --max-time 15 -H "Authorization: Bearer test_ai_-ZFEjZ3qiK2mW3k7C9M2Q60OK2QmLslRdSnNWt61z4E" -H "Content-Type: application/json" -H "Accept: text/event-stream" -d "{\`"jsonrpc\`":\`"2.0\`",\`"id\`":1,\`"method\`":\`"initialize\`",\`"params\`":{\`"protocolVersion\`":\`"2024-11-05\`",\`"capabilities\`":{},\`"clientInfo\`":{\`"name\`":\`"curl-client\`",\`"version\`":\`"1.0.0\`"}}}" <https://bookmyjuice-test.mcp.chargebee.com/onboarding_agent>

-> use the session id to get the tool-list: curl.exe -v --max-time 15 -H "Authorization: Bearer test_ai_-ZFEjZ3qiK2mW3k7C9M2Q60OK2QmLslRdSnNWt61z4E" -H "mcp-session-id: 019e5b06-bb63-7f6d-b745-bb1bd8bd231a" -H "Content-Type: application/json" -H "Accept: text/event-stream" -d "{\`"jsonrpc\`":\`"2.0\`",\`"id\`":2,\`"method\`":\`"tools/list\`",\`"params\`":{}}" <https://bookmyjuice-test.mcp.chargebee.com/onboarding_agent>

