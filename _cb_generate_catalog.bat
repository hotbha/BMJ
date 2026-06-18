curl.exe -s --max-time 30 ^
  -H "Authorization: Bearer test_ai_-ZFEjZ3qiK2mW3k7C9M2Q60OK2QmLslRdSnNWt61z4E" ^
  -H "mcp-session-id: 019ea867-9417-7477-bbe0-e6b42d0a32d0" ^
  -H "Content-Type: application/json" ^
  -H "Accept: text/event-stream" ^
  -d @_cb_generate_catalog_payload.json ^
  https://bookmyjuice-test.mcp.chargebee.com/onboarding_agent > chargebee_mcp_generated_catalog.json 2>&1