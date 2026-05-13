import os  
os.chdir('x:/BMJ')  
with open('docs/business-requirements/BRD_Business_Requirements.md','r',encoding='utf-8') as f:  
    lines = f.readlines()  
  
# Line-based operations  
print('Read ' + str(len(lines)) + ' lines') 
