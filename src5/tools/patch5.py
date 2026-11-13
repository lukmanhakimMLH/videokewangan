p="/home/user/videokewangan/src5/build5.py";s=open(p).read()
a='''   [("So",20),("bila",21),("tanya,",22),BR,("dia",23),("kata",24),("OK,",25)],
   [("dalam",26),("2",27,1),("orang.",28)],'''
assert a in s
s=s.replace(a,'''   [("So",20),("bila",21),("tanya,",22),("dia",23),("kata",24),BR,("OK,",25),("dalam",26),("2 orang.",27,1)],''')
assert 'BR,("10",35,1),("orang!",36)]' in s
s=s.replace('BR,("10",35,1),("orang!",36)]','BR,("10 orang!",35,1)]')
k=s.index("rep('<span class=")
s=s[:k]+"""rep('{ y: -6, duration: 1.4, ease: "none" }, 0);','{ y: -6, duration: 1.05, ease: "none" }, 0);')
rep('{ y: 6, duration: 1.4, ease: "none" }, 0);','{ y: 6, duration: 1.05, ease: "none" }, 0);')
"""+s[k:]
open(p,"w").write(s)
