import base64,json,os
os.chdir("x:/BMJ")
for d in ["lush/lib/models","lush/lib/repositories","lush/lib/bloc/ReferralBloc","lush/lib/utils","lush/lib/views/screens/referral"]: os.makedirs(d,exist_ok=True)
data=json.load(open("files_b64.json"))
for path,b64 in data.items():
  open(path,"w").write(base64.b64decode(b64).decode())
  print("WROTE:",path)
print("ALL DONE")
