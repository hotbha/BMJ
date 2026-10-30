"""Inspect the Chargebee MCP tool schemas used by the price rollout.

Usage
    python cb_tool_schema.py <agent> <tool> [<tool> ...]

Prints the input_schema sections (path/query/header/body params) with their
property names and required lists so a caller can build valid arguments without
guessing field names. Stdlib only; the bearer key never hits the shell.
"""

import json
import sys

from mcp_call import AGENTS, _post

import uuid


def session(agent):
    url, key = AGENTS[agent]
    init, sid = _post(
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
    if "error" in init:
        raise SystemExit(json.dumps(init, indent=2))
    return url, key, sid


def load_spec(agent, tool):
    url, key, sid = session(agent)
    result, _ = _post(
        url,
        key,
        {
            "jsonrpc": "2.0",
            "id": "spec",
            "method": "tools/call",
            "params": {"name": "get_tool_spec", "arguments": {"tool_name": tool}},
        },
        sid,
    )
    text = result["result"]["content"][0]["text"]
    return json.loads(text)


def describe(spec):
    schema = spec["input_schema"]
    print(f"== {spec['tool_name']} ==")
    print(f"description: {spec.get('description', '')}")
    for section, value in schema.get("properties", {}).items():
        required = value.get("required", [])
        names = sorted(value.get("properties", {}).keys())
        print(f"  {section}: required={required}")
        print(f"    {len(names)} properties: {names}")
    print(f"  top-level required: {schema.get('required')}")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:  # pragma: no cover
        pass
    agent = sys.argv[1]
    for tool in sys.argv[2:]:
        describe(load_spec(agent, tool))
    return 0


if __name__ == "__main__":
    sys.exit(main())
