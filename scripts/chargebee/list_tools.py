#!/usr/bin/env python3
"""List Chargebee MCP tools and save to file"""
import json
import requests

BASE_URL = "https://bookmyjuice-test.mcp.chargebee.com/onboarding_agent"
TOKEN = "test_ai_-ZFEjZ3qiK2mW3k7C9M2Q60OK2QmLslRdSnNWt61z4E"
SESSION_ID = "019e5c40-f05d-77ea-820e-037d0cc7a7fc"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "text/event-stream",
    "mcp-session-id": SESSION_ID
}

body = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
}

resp = requests.post(BASE_URL, json=body, headers=headers, timeout=15)
content = resp.text

# Parse SSE JSON from the response and save full data
with open("chargebee_tools_full.json", "w") as f:
    f.write(content)

print("=== RAW RESPONSE ===")
print(content[:10000])

# Try to extract tools
for line in content.split("\n"):
    if line.startswith("data: "):
        data = json.loads(line[6:])
        tools = data.get("result", {}).get("tools", [])
        print(f"\n=== Found {len(tools)} tools ===")
        for t in tools:
            name = t.get("name", "unknown")
            desc = t.get("description", "")[:300]
            schema = t.get("inputSchema", {})
            props = schema.get("properties", {})
            required = schema.get("required", [])
            print(f"\n--- {name} ---")
            print(f"  Description: {desc}")
            print(f"  Required params: {json.dumps(required)}")
            for pname, pinfo in props.items():
                ptype = pinfo.get("type", "any")
                print(f"    {pname} ({ptype}): {pinfo.get('description', '')[:150]}")
        break
