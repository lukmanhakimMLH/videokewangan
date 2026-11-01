import subprocess,sys
K=[(0.00,1.55),(1.95,2.50),(3.20,4.95),(5.10,6.95),(7.30,11.15),(11.45,14.00),(14.62,18.15),(18.50,19.15),(19.88,21.85),(22.22,23.65),(23.82,24.40)]
f=[];v=[];a=[]
for i,(s,e) in enumerate(K):
    d=e-s
    f.append(f"[0:v]trim={s}:{e},setpts=PTS-STARTPTS[v{i}]")
    f.append(f"[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st={d-0.04:.3f}:d=0.04[a{i}]")
    v.append(f"[v{i}][a{i}]")
f.append("".join(v)+f"concat=n={len(K)}:v=1:a=1[v][a]")
open("cut_filter.txt","w").write(";\n".join(f))
t=0
for s,e in K: print(f"{s:.2f}-{e:.2f} -> out {t:.2f}"); t+=e-s
print("total",round(t,2))
