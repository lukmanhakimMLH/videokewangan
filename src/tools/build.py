import json,re,sys,os
ROOT="/home/user/videokewangan"
sig=json.load(open(f"{ROOT}/src/sig.json"))
W=json.load(open(f"{ROOT}/src/cutwords.json"))
def wt(i): return W[i]["s"],W[i]["e"]
# caption groups: list of (words[(text,idx,key)])  key=True gold
BR=("|",None)
G=[
 [("Jika",4),("kita",5),("nak",6),("orang",7),("tahu",8),BR,("keburukan",9,1),("kita,",10)],
 [("kita",11),("tanya",12),("orang",13),BR,("yang",14),("membenci",15,1),("kita.",16)],
 [("Jika",17),("kita",18),("nak",19),("tahu",20),BR,("apa",21),("baik",22,1),("kita,",23)],
 [("kita",24),("tanya",25),("orang",26),BR,("yang",27),("sayang",28,1),("kita.",29)],
 [("Tapi,",30),("hakikatnya",31),BR,("dua-dua",32),("adalah",34),("manusia.",35,1)],
 [("Akan",36),("ada",37),("orang",38),BR,("yang",39),("membenci",40,1),("kita",41)],
 [("dan",42),("juga",43),("ada",44),BR,("yang",45),("menyukai",46,1),("kita.",47)],
]
OV={30:(9.62,10.05)}  # fix 'Tapi'
def T(i): return OV.get(i,wt(i))
caps_html=[];caps_js=[]
for gi,g in enumerate(G):
    g=list(g); s=T(g[0][1])[0]-0.08
    nxt = T(G[gi+1][0][1])[0]-0.08 if gi+1<len(G) else 15.70
    e=min(T(g[-1][1])[1]+0.6, nxt)
    spans=[];rows=[[]]
    for wi,w in enumerate(g):
        if w[0]=="|": rows.append([]); continue
        cls="w k" if len(w)>2 else "w"
        rows[-1].append(f'<span class="{cls}" id="c{gi}w{wi}"><span class="in">{w[0]}</span></span>')
        ws=T(w[1])[0]
        caps_js.append(f'word("#c{gi}w{wi}",{ws-0.06:.2f},{1 if len(w)>2 else 0});')
    caps_html.append(f'<div class="cap clip" id="cap{gi}" data-start="{s:.2f}" data-duration="{e-s:.2f}" data-track-index="3"><div class="line">{"".join('<span class="row">'+" ".join(r)+'</span>' for r in rows)}</div></div>')
    caps_js.append(f'capOut("#cap{gi}",{e-s:.2f},{s:.2f});')
AUD=[("music","pad",0,0.11,23.2),("sfx-hook","impact",0,0.55,4.2),("sfx-wh1","whoosh",1.32,0.38,1.7),("sfx-sig","shimmer",1.95,0.22,4.0),
 ("sfx-t1","tick",2.80,0.2,0.52),("sfx-t2","tick",4.72,0.2,0.52),("sfx-t3","tick",6.78,0.2,0.52),("sfx-t4","tick",8.62,0.2,0.52),
 ("sfx-wh2","whoosh_soft",9.45,0.32,1.3),("sfx-drop","subdrop",11.38,0.45,1.5),("sfx-t5","tick",12.74,0.2,0.52),("sfx-t6","tick",14.58,0.2,0.52),
 ("sfx-rise","riser",14.12,0.26,1.6),("sfx-hit","impact",15.70,0.5,4.2),("sfx-allah","shimmer",16.92,0.3,4.0),("sfx-wh3","whoosh_soft",19.62,0.32,1.3),("sfx-end","shimmer",20.05,0.34,2.95)]
aud="\n".join(f'      <audio id="{i}" src="assets/sfx/{f}.wav" data-start="{st}" data-duration="{min(d,23-st):.2f}" data-volume="{v}"{" data-fade-out=\"1.5\"" if i=="music" else ""} data-track-index="{10+k}"></audio>' for k,(i,f,st,v,d) in enumerate(AUD))
tpl=open(f"{ROOT}/src/tools/index.tpl.html").read()
out=tpl.replace("%%SIG_D%%",sig["d"]).replace("%%SIG_VB%%",sig["vb"]).replace("%%CAPS%%","\n      ".join(caps_html)).replace("%%AUDIO%%",aud).replace("%%CAPS_JS%%","\n      ".join(caps_js))
open(f"{ROOT}/kata-kata/index.html","w").write(out)
print("ok",len(G),"groups")
