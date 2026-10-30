"""Print MCP tool input schemas straight from tools/list (no get_tool_spec).

Usage
    python cb_list_schemas.py <agent> [<tool> ...]

The data-lookup agent does not expose get_tool_spec, so schemas are read from
the tools/list payload instead.
"""

import json
import sys
import uuid

from mcp_call import AGENTS, _post


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:  # pragma: no cover
        pass

    agent = sys.argv[1]
    wanted = set(sys.argv[2:])
    url, key = AGENTS[agent]
    _, sid = _post(
        url,
        key,
        {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "bmj-verify", "version": "1.0.0"},
            },
        },
    )
    listed, _ = _post(
        url,
        key,
        {"jsonrpc": "2.0", "id": "tools", "method": "tools/list", "params": {}},
        sid,
    )
    tools = listed["result"]["tools"]
    for tool in tools:
        if wanted and tool["name"] not in wanted:
            continue
        schema = tool.get("inputSchema", {})
        print(f"== {tool['name']} ==")
        print(f"  required: {schema.get('required')}")
        for section, value in (schema.get("properties") or {}).items():
            names = sorted((value.get("properties") or {}).keys())
            if names:
                print(f"  {section}: {names}")
            else:
                print(f"  {section}: {value.get('type')}")
        print()
    print(f"{len(tools)} tool(s) on the {agent} agent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
