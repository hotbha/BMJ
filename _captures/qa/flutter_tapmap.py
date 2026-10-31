"""Fetch the Flutter render tree from the VM service and print text -> tap point."""

import json
import re
import sys
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:33901/sI4AdCS2kxM="
ISOLATE = "isolates/168241820757051"


def fetch(method):
    url = f"{BASE}/{method}?isolateId={urllib.parse.quote(ISOLATE, safe='')}"
    with urllib.request.urlopen(url, timeout=60) as resp:
        payload = json.load(resp)
    return payload["result"]["data"]


tree = fetch(sys.argv[1] if len(sys.argv) > 1 else "ext.flutter.debugDumpRenderTree")

blocks = tree.split("\n")
offset = None
size = None
out = []
for line in blocks:
    m = re.search(r"offset=Offset\((-?[\d.]+), (-?[\d.]+)\)", line)
    if m:
        offset = (float(m.group(1)), float(m.group(2)))
    m = re.search(r"size: Size\(([\d.]+), ([\d.]+)\)", line)
    if m:
        size = (float(m.group(1)), float(m.group(2)))
    m = re.search(r'text: TextSpan\(.*?text: "([^"]{1,60})"', line)
    if not m:
        m = re.search(r'TextSpan\(.*?"([^"]{1,60})"', line)
    if m and offset and size:
        label = m.group(1)
        cx = offset[0] + size[0] / 2
        cy = offset[1] + size[1] / 2
        out.append((label, round(cx), round(cy), round(size[0]), round(size[1])))
        offset, size = None, None

seen = set()
for label, cx, cy, w, h in out:
    key = (label, cy)
    if key in seen:
        continue
    seen.add(key)
    print(f"{label!r:34} tap=({cx},{cy}) size=({w}x{h})")
print(f"\n{len(out)} paragraphs parsed", file=sys.stderr)
