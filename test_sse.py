#!/usr/bin/env python3
"""Test SSE streaming from Chargebee MCP"""
import json
import requests

BASE_URL = "https://bookmyjuice-test.mcp.chargebee.com/onboarding_agent"
TOKEN = "test_ai_-ZFEjZ3qiK2mW3k7C9M2Q60OK2QmLslRdSnNWt61z4E"

# Use the session from before
session_id = "019e6559-4a55-7192-9fba-cd8d8f70327b"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "text/event-stream",
    "mcp-session-id": session_id,
}

body = {
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
        "name": "import_product_catalog",
        "arguments": {
            "items": [],
            "itemFamilies": [],
            "itemPrices": [],
            "currencies": [{"currency_code": "INR"}]
        }
    }
}

# First, let's just test that the session is still valid
print("Testing session with get-tools...")
body2 = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
}

resp = requests.post(BASE_URL, json=body2, headers=headers, timeout=15)
print(f"Tools list response: {resp.text[:500]}")
