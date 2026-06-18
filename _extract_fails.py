import json
import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

names = {}
lines = content.splitlines()
for line in lines:
    line = line.strip()
    if not line:
        continue
    try:
        d = json.loads(line)
        t = d.get('type', '')
        if t == 'testStart':
            test = d.get('test', {})
            tid = test.get('id', '')
            name = test.get('name', '')
            names[tid] = name
        elif t == 'testDone':
            tid = d.get('testID', '')
            result = d.get('result', '')
            if result == 'error':
                name = names.get(tid, 'UNKNOWN')
                print(name)
    except json.JSONDecodeError:
        continue