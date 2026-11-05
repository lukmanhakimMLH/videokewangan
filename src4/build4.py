import json,re
R="/home/user/videokewangan"
sig=json.load(open(f"{R}/src/sig.json"));W=json.load(open(f"{R}/src4/cutwords.json"))
def T(i): return W[i]["s"],W[i]["e"]
END=8.55; DUR=round(END+4.75,2); VID=8.9
BR=("|",None)
G=[[("Bila",4),("orang",5),("bercakap",6,1),BR,("pasal",7),("kita,",8)],
   [("jangan",9),("berlawan",10,1),BR,("dengan",11),("kata-kata.",12,1)],
   [("sebab",14),("dia",16),("pasti",17),BR,("nak",18),("menang",19,1),("juga.",20)]]
caps_html=[];caps_js=[]
for gi,g in enumerate(G):
    ws=[w for w in g if w[0]!="|"]
    s=T(ws[0][1])[0]-0.08
    nxt=T([w for w in G[gi+1] if w[0]!="|"][0][1])[0]-0.08 if gi+1<len(G) else 6.84
    e=min(T(ws[-1][1])[1]+0.6,nxt)
    rows=[[]];k=0
    for w in g:
        if w[0]=="|": rows.append([]);continue
        key=len(w)>2
        rows[-1].append(f'<span class="{"w k" if key else "w"}" id="c{gi}w{k}"><span class="in">{w[0]}</span></span>')
        caps_js.append(f'word("#c{gi}w{k}",{T(w[1])[0]-0.06:.2f},{1 if key else 0});');k+=1
    caps_html.append(f'<div class="cap clip" id="cap{gi}" data-start="{s:.2f}" data-duration="{e-s:.2f}" data-track-index="3"><div class="line">{"".join("<span class=row>"+" ".join(r)+"</span>" for r in rows)}</div></div>')
    caps_js.append(f'capOut("#cap{gi}",{e-s:.2f},{s:.2f});')
AUD=[("music","pad",0,0.11,DUR),("sfx-hook","impact",0,0.55,4.2),("sfx-wh1","whoosh",1.1,0.38,1.7),("sfx-sig","shimmer",1.95,0.22,4.0),
 ("sfx-t1","tick",2.08,0.2,0.52),("sfx-t2","tick",3.68,0.2,0.52),("sfx-t3","tick",4.32,0.2,0.52),("sfx-t4","tick",6.26,0.22,0.52),
 ("sfx-rise","riser",5.25,0.24,1.6),("sfx-hit","impact",6.84,0.5,4.2),("sfx-drop","subdrop",7.9,0.42,1.5),("sfx-res","shimmer",7.92,0.32,4.0),
 ("sfx-wh3","whoosh_soft",8.4,0.32,1.3),("sfx-end","shimmer",8.85,0.34,4.0)]
aud="\n".join(f'      <audio id="{i}" src="assets/sfx/{f}.wav" data-start="{st}" data-duration="{min(d,DUR-st):.2f}" data-volume="{v}"{" data-fade-out=\"1.5\"" if i=="music" else ""} data-track-index="{10+k}"></audio>' for k,(i,f,st,v,d) in enumerate(AUD))
s=open(f"{R}/src/tools/index.tpl.html").read()
def IX(m): return s.index(m, s.index("const tl ="))
def rep(a,b):
    global s
    assert a in s, a[:60]; s=s.replace(a,b)
rep('data-duration="24.5" data-width',f'data-duration="{DUR}" data-width')
rep('data-start="0" data-duration="20.28" data-track-index="0"',f'data-start="0" data-duration="{VID}" data-track-index="0"')
rep('overflow: hidden; transform-origin: 50% 56%; }','overflow: hidden; transform-origin: 50% 30%; }')
rep('.cap { position: absolute; left: 0; right: 0; top: 290px;','.cap { position: absolute; left: 0; right: 0; top: 262px;')
rep('{ y: -6, duration: 1.4, ease: "none" }, 0);','{ y: -6, duration: 1.08, ease: "none" }, 0);')
rep('{ y: 6, duration: 1.4, ease: "none" }, 0);','{ y: 6, duration: 1.08, ease: "none" }, 0);')
rep('<span class="l1" id="h1">Siapa yang paling</span>','<span class="l1" id="h1">Kata-kata hari ini 🗣️</span>')
rep('<span class="l2 gold" id="h2">jujur</span>','<span class="l2 gold" id="h2">Lawan Dengan Result</span>')
rep('<span class="l3" id="h3">tentang dirimu?</span>','<span class="l3" id="h3">🤫 📈 🏆</span>')
rep('#hook .l2 { display: inline-block; font-family: "Playfair Display"; font-style: italic; font-weight: 800; font-size: 200px;','#hook .l2 { display: inline-block; font-family: "Playfair Display"; font-style: italic; font-weight: 800; font-size: 80px;')
rep('#hook .l1, #hook .l3 { display: block; font-family: "Montserrat";','#hook .l1, #hook .l3 { display: block; font-family: "Montserrat", "EmojiColor";')
rep('<div id="badge" class="clip" data-start="1.5" data-duration="14.2"','<div id="badge" class="clip" data-start="1.25" data-duration="5.5"')
# quote
rep('''<div id="bars" class="clip" data-start="15.6" data-duration="4.3"''','''<div id="bars" class="clip" data-start="6.76" data-duration="1.84"''')
rep('''<div id="quote" class="clip" data-start="15.68" data-duration="4.2" data-track-index="5" data-track-kind="graphics"><div id="quoteInner">
        <div class="q" id="q0"><span class="gold">YANG PENTING</span></div>
        <div class="q" id="q1"><span class="gold">di mata Allah SWT,</span></div>
        <div class="q" id="q2">kita hamba-Nya</div>
        <div class="q" id="q3">yang macam mana?</div>
      </div></div>''','''<div id="quote" class="clip" data-start="6.82" data-duration="1.78" data-track-index="5" data-track-kind="graphics"><div id="quoteInner">
        <div class="q" id="q0"><span class="gold">TAPI</span></div>
        <div class="q" id="q1">lawan dengan</div>
        <div class="q" id="q2"><span class="gold">result.</span></div>
      </div></div>''')
rep('''      #q0 { top: 232px; font-family: "Montserrat"; font-weight: 600; font-size: 30px; letter-spacing: .5em; padding-left: .5em; }
      #q1 { top: 286px; font-family: "Playfair Display"; font-style: italic; font-weight: 700; font-size: 92px; }
      #q2 { top: 410px; font-family: "Playfair Display"; font-weight: 600; font-size: 74px; color: #fff; text-shadow: 0 5px 26px rgba(0,0,0,.8); }
      #q3 { top: 506px; font-family: "Playfair Display"; font-style: italic; font-weight: 600; font-size: 74px; color: #fff; text-shadow: 0 5px 26px rgba(0,0,0,.8); }
      #q1 .gold { padding: 0 14px; filter: drop-shadow(0 6px 24px rgba(0,0,0,.7)); }''','''      #q0 { top: 192px; font-family: "Montserrat"; font-weight: 600; font-size: 34px; letter-spacing: .5em; padding-left: .5em; }
      #q1 { top: 250px; font-family: "Playfair Display"; font-weight: 600; font-size: 70px; color: #fff; text-shadow: 0 5px 26px rgba(0,0,0,.8); }
      #q2 { top: 340px; font-family: "Playfair Display"; font-style: italic; font-weight: 800; font-size: 132px; line-height: 1.15; }
      #q3 { top: 350px; font-family: "Playfair Display"; font-style: italic; font-weight: 600; font-size: 66px; color: #fff; text-shadow: 0 5px 26px rgba(0,0,0,.8); }
      #q2 .gold { padding: 0 16px; filter: drop-shadow(0 6px 24px rgba(0,0,0,.7)); }''')
rep('<div id="sign" class="clip" data-start="1.7" data-duration="18.2"','<div id="sign" class="clip" data-start="1.7" data-duration="6.9"')
rep('<div id="endcard" class="clip" data-start="19.75" data-duration="4.75"',f'<div id="endcard" class="clip" data-start="{END}" data-duration="4.75"')
# JS: camera
a=IX("      tl.fromTo(cam, { scale: 1.14 }");b=IX("      /* ---------- light leaks")
s=s[:a]+'''      tl.fromTo(cam, { scale: 1.12 }, { scale: 1.03, duration: 3.38, ease: "power2.out" }, 0);
      const cuts = [[3.38, 1.06, 1.08], [6.78, 1.08, 1.12], [8.30, 1.06, 1.07]];
      cuts.forEach(([t, a, b], i) => {
        const end = i + 1 < cuts.length ? cuts[i + 1][0] : 8.9;
        tl.set(cam, { scale: a }, t);
        tl.to(cam, { scale: b, duration: (t === 3.38 ? 3.74 : (t === 6.78 ? 7.94 : end)) - t, ease: "none" }, t);
      });
      tl.to(cam, { scale: 1.12, duration: 0.22, ease: "power3.out" }, 3.74);
      tl.to(cam, { scale: 1.09, duration: 1.2, ease: "power2.inOut" }, 3.96);
      tl.to(cam, { scale: 1.2, duration: 0.25, ease: "power3.out" }, 7.94);
      tl.to(cam, { scale: 1.17, duration: 0.11, ease: "power2.inOut" }, 8.19);

'''+s[b:]
a=IX("      leak(1.40, -500");b=IX("      /* ---------- hook")
s=s[:a]+'''      leak(1.15, -500, 400, 0.45);
      leak(3.34, 500, -400, 0.3);
      leak(6.78, -400, 500, 0.5);
      leak(8.45, 300, -300, 0.4);
      tl.to("#flash", { opacity: 0.35, duration: 0.06 }, 6.84);
      tl.to("#flash", { opacity: 0, duration: 0.4 }, 6.9);
      tl.to("#flash", { opacity: 0.25, duration: 0.05 }, 7.94);
      tl.to("#flash", { opacity: 0, duration: 0.35 }, 7.99);

'''+s[b:]
rep('tl.to(["#h1", "#h3", "#hrule"], { opacity: 0, y: -30, duration: 0.25, ease: "power2.in" }, 1.42);','tl.to(["#h1", "#h3", "#hrule"], { opacity: 0, y: -30, duration: 0.25, ease: "power2.in" }, 1.1);')
rep('tl.to("#h2", { opacity: 0, scale: 0.7, y: -120, duration: 0.3, ease: "power2.in" }, 1.42);','tl.to("#h2", { opacity: 0, scale: 0.7, y: -120, duration: 0.3, ease: "power2.in" }, 1.1);')
rep('{ opacity: 1, scale: 1, duration: 0.7, ease: E }, 1.55);','{ opacity: 1, scale: 1, duration: 0.7, ease: E }, 1.28);')
rep('tl.to("#badgeInner", { opacity: 0, y: -16, duration: 0.25, ease: "power2.in" }, 15.42);','tl.to("#badgeInner", { opacity: 0, y: -16, duration: 0.25, ease: "power2.in" }, 6.55);')
rep('{ attr: { x: 900 }, duration: 1.0, ease: "power2.inOut" }, 10.2);','{ attr: { x: 900 }, duration: 1.0, ease: "power2.inOut" }, 5.2);')
rep('tl.to("#signBox", { opacity: 0, y: 10, duration: 0.3, ease: "power2.in" }, 19.55);','tl.to("#signBox", { opacity: 0, y: 10, duration: 0.3, ease: "power2.in" }, 8.3);')
a=IX('      tl.fromTo("#barT"');b=IX("      /* ---------- end card")
s=s[:a]+'''      tl.fromTo("#barT", { yPercent: -100 }, { yPercent: 0, duration: 0.4, ease: "power3.inOut" }, 6.76);
      tl.fromTo("#barB", { yPercent: 100 }, { yPercent: 0, duration: 0.4, ease: "power3.inOut" }, 6.76);
      tl.to("#dim", { opacity: 0.34, duration: 0.5, ease: "power2.out" }, 6.76);
      tl.fromTo("#q0", { opacity: 0, scale: 1.2 }, { opacity: 1, scale: 1, duration: 0.45, ease: E }, 6.86);
      tl.fromTo("#q1", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.4, ease: E }, 7.16);
      tl.fromTo("#q2", { opacity: 0, y: 40, scale: 1.35 }, { opacity: 1, y: 0, scale: 1, duration: 0.6, ease: "back.out(1.8)" }, 7.92);
      tl.to("#quoteInner", { opacity: 0, duration: 0.15, ease: "power2.in" }, 8.42);

'''+s[b:]
off=END-19.75
def shift(m): return f"{float(m.group(1))+off:.2f})"
a=IX("      /* ---------- end card");b=IX("      window.__timelines =")
blk=re.sub(r"(\d+\.\d+)\)(;?)$",lambda m:shift(m)+m.group(2),s[a:b],flags=re.M)
blk=re.sub(r'sigDraw\("B", [^)]*\)',f'sigDraw("B", {20.05+off:.2f}, 1.25)',blk)
s=s[:a]+blk+s[b:]
out=s.replace("%%SIG_D%%",sig["d"]).replace("%%SIG_VB%%",sig["vb"]).replace("%%CAPS%%","\n      ".join(caps_html)).replace("%%CAPS_JS%%","\n      ".join(caps_js)).replace("%%AUDIO%%",aud)
open(f"{R}/lawan-result/index.html","w").write(out); print("ok",DUR)
