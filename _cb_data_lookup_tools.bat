curl.exe -s --max-time 15 ^
  -H "Authorization: Bearer test_ai_WvyPvGTh7AKfZ6vM6UHOrWZduN1xKiU1Ir_MxccF3-Q" ^
  -H "mcp-session-id: 019ea86e-ad6b-7b82-ac95-1317dc6f9c9d" ^
  -H "Content-Type: application/json" ^
  -H "Accept: text/event-stream" ^
  -d @_cb_data_lookup_tools_payload.json ^
  https://bookmyjuice-test.mcp.chargebee.com/data_lookup_agent > chargebee_data_lookup_tools.json 2>&1