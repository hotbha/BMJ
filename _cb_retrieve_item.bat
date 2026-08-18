@echo off
curl.exe -s --max-time 15 ^
  -H "Authorization: Bearer test_ai_WvyPvGTh7AKfZ6vM6UHOrWZduN1xKiU1Ir_MxccF3-Q" ^
  -H "mcp-session-id: 019efa8e-502a-7bba-8b20-fa6cde34449c" ^
  -H "Content-Type: application/json" ^
  -H "Accept: text/event-stream" ^
  -d @_cb_retrieve_item_payload.json ^
  https://bookmyjuice-test.mcp.chargebee.com/data_lookup_agent 2>&1