import json

config = {
    "mcpServers": {
        "dart": {
            "command": "dart",
            "args": ["mcp-server"],
            "env": {}
        },
        "firebase": {
            "command": "npx",
            "args": ["-y", "firebase-tools@latest", "mcp"]
        },
        "google-docs": {
            "type": "streamableHttp",
            "url": "https://developerknowledge.googleapis.com/mcp",
            "headers": {"X-Goog-Api-Key": "YOUR_GOOGLE_CLOUD_API_KEY"},
            "disabled": False
        },
        "m365agentstoolkit": {
            "command": "npx",
            "args": ["-y", "@microsoft/m365agentstoolkit-mcp@latest", "server", "start"]
        },
        "chargebee-knowledge-base": {
            "type": "http",
            "url": "https://bookmyjuice-test.mcp.chargebee.com/knowledge_base_agent"
        },
        "onboarding_agent": {
            "type": "http",
            "url": "https://bookmyjuice-test.mcp.chargebee.com/onboarding_agent",
            "auth": {"CLIENT_ID": "cb_mcp_client_AzZSfDVKSUzR6M7S"}
        },
        "data_lookup_agent": {
            "type": "http",
            "url": "https://bookmyjuice-test.mcp.chargebee.com/data_lookup_agent",
            "auth": {"CLIENT_ID": "cb_mcp_client_16CIVmVKSVjavMKW"}
        },
        "adb-mcp": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
            "env": {"PATH": "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"},
            "disabled": False
        },
        "playwright-mcp": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-playwright"],
            "disabled": False
        }
    }
}

with open("c:/Users/BHARA/AppData/Roaming/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json", "w") as f:
    json.dump(config, f, indent=2)

print("Done - MCP config written successfully")
