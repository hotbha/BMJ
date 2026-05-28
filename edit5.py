t=open('lush/lib/bloc/CartBloc/cart_bloc.dart','r',encoding='utf-8').read()
idx=t.find('Future<void>.delayed')
eol1=t.find('\n',idx)
eol2=t.find('\n',eol1+1)
eol3=t.find('\n',eol2+1)
old=t.indexx:eol3+1]
line1=t[inxx:eol1+1]
rest=t[eol1+1:eol3+1]
new=line1 + '        await AnalyticsService.logOrderPlaced();' + '\n' + rest
t=t.replace(old,new)
open('lush/lib/bloc/CartBloc/cart_bloc.dart','w',encoding='utf-8').write(t)
print('logOrderPlaced:','logOrderPlaced' in t)