curl.exe -v --max-time 30 ^
  -H "Authorization: Bearer test_ai_WvyPvGTh7AKfZ6vM6UHOrWZduN1xKiU1Ir_MxccF3-Q" ^
  -H "Content-Type: application/json" ^
  -H "Accept: text/event-stream" ^
  -H "mcp-session-id: 019ea86e-ad6b-7b82-ac95-1317dc6f9c9d" ^
  -d @_cb_search_plans_payload.json ^
  https://bookmyjuice-test.mcp.chargebee.com/data_lookup_agent 2>&1