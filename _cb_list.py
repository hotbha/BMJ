import requests, json

# Get session
r = requests.post('https://bookmyjuice-test.mcp.chargebee.com/onboarding_agent',
  headers={'Authorization':'Bearer test_ai_-ZFEjZ3qiK2mW3k7C9M2Q60OK2QmLslRdSnNWt61z4E','Content-Type':'application/json','Accept':'text/event-stream'},
  json={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'python-client','version':'1.0.0'}}},
  timeout=15)
sid = r.headers.get('mcp-session-id', '')
print('Session:', sid)

# List tools
r2 = requests.post('https://bookmyjuice-test.mcp.chargebee.com/onboarding_agent',
  headers={'Authorization':'Bearer test_ai_-ZFEjZ3qiK2mW3k7C9M2Q60OK2QmLslRdSnNWt61z4E','Content-Type':'application/json','Accept':'text/event-stream', 'mcp-session-id': sid},
  json={'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}},
  timeout=15)
data = json.loads(r2.text.split('data: ')[1].strip())
for t in data['result']['tools']:
    print(t['name'], '-', t['description'][:80])