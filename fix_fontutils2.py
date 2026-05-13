with open("lush/lib/views/screens/forgot_password_screen.dart","r",encoding="utf-8") as f:
    c=f.read()
import re
cnt=str(c.count("FontUtils"))
print("FontUtils count: "+cnt)
lines=c.split("\n")
for i,l in enumerate(lines):
    if "FontUtils" in l:
        print("Line "+str(i+1)+": "+repr(l))
        for j in range(i+1,min(i+5,len(lines))):
            print("  "+str(j+1)+": "+repr(lines[j]))
        print("---")
