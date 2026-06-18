import os
os.chdir("x:/BMJ")
nl=chr(10)
s=[]
s.append("import bs4")
print(len(s))
open("test_s7.txt","w").write(nl.join(s))
print("test ok")
