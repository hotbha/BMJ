curl.exe -v --max-time 15 ^
  -H "Authorization: Bearer test_ai_-ZFEjZ3qiK2mW3k7C9M2Q60OK2QmLslRdSnNWt61z4E" ^
  -H "Content-Type: application/json" ^
  -H "Accept: text/event-stream" ^
  -d @chargebee_init_payload.json ^
  https://bookmyjuice-test.mcp.chargebee.com/onboarding_agent 2>&1