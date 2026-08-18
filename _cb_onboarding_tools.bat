@echo off
curl.exe -s --max-time 15 ^
  -H "Authorization: Bearer test_ai_-ZFEjZ3qiK2mW3k7C9M2Q60OK2QmLslRdSnNWt61z4E" ^
  -H "mcp-session-id: 019efaae-7696-76db-9324-402b563eab40" ^
  -H "Content-Type: application/json" ^
  -H "Accept: text/event-stream" ^
  -d @_chargebee_tools_payload.json ^
  https://bookmyjuice-test.mcp.chargebee.com/onboarding_agent 2>&1