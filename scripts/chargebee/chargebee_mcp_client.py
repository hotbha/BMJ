#!/usr/bin/env python3
"""
Chargebee MCP Client - Creates items and prices for BMJ
"""
import json
import requests
import sys
import uuid

BASE_URL = "https://bookmyjuice-test.mcp.chargebee.com/onboarding_agent"
TOKEN = "test_ai_-ZFEjZ3qiK2mW3k7C9M2Q60OK2QmLslRdSnNWt61z4E"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "text/event-stream",
}

def new_session():
    """Get a new session ID"""
    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "bmj-client", "version": "1.0.0"}
        }
    }
    resp = requests.post(BASE_URL, json=body, headers=headers, timeout=15)
    # Extract session ID from response headers
    session_id = resp.headers.get("mcp-session-id", "")
    print(f"Session ID: {session_id}")
    
    # Also check content for session info
    content = resp.text
    print(f"Response: {content[:500]}")
    return session_id

def get_tools(session_id):
    """List available MCP tools"""
    body = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    h = headers.copy()
    h["mcp-session-id"] = session_id
    resp = requests.post(BASE_URL, json=body, headers=h, timeout=15)
    print(f"Tools response: {resp.text[:2000]}")
    return resp.text

def call_tool(session_id, method_name, arguments):
    """Call an MCP tool"""
    body = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": method_name,
            "arguments": arguments
        }
    }
    h = headers.copy()
    h["mcp-session-id"] = session_id
    resp = requests.post(BASE_URL, json=body, headers=h, timeout=30)
    # Parse SSE format
    content = resp.text
    print(f"Tool '{method_name}' response: {content[:3000]}")
    return content

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python chargebee_mcp_client.py <action> [args]")
        print("Actions: new-session, get-tools, call-tool")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "new-session":
        sid = new_session()
        print(f"\nUse this session ID: {sid}")
    
    elif action == "get-tools":
        session_id = sys.argv[2] if len(sys.argv) > 2 else ""
        if not session_id:
            print("Error: session_id required")
            sys.exit(1)
        get_tools(session_id)
    
    elif action == "call-tool":
        session_id = sys.argv[2] if len(sys.argv) > 2 else ""
        method_name = sys.argv[3] if len(sys.argv) > 3 else ""
        params_str = sys.argv[4] if len(sys.argv) > 4 else "{}"
        if not all([session_id, method_name]):
            print("Error: session_id, method_name required")
            sys.exit(1)
        params = json.loads(params_str)
        call_tool(session_id, method_name, params)
    
    else:
        print(f"Unknown action: {action}")
