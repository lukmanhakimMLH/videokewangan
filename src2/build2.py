import json,re
R="/home/user/videokewangan"
sig=json.load(open(f"{R}/src/sig.json"));W=json.load(open(f"{R}/src2/cutwords.json"))
def T(i): return W[i]["s"],W[i]["e"]
END=11.5; DUR=round(END+4.75,2); VID=12.03
BR=("|",None)
G=[[("Bersyukurlah",4,1),("dengan",5),BR,("apa",6),("yang",7),("ada,",8)],
   [("dan",9),("bersabarlah",10,1)],
   [("dengan",11),("apa",12),("yang",13),BR,("belum",14,1),("ada.",15)]]
caps_html=[];caps_js=[]
for gi,g in enumerate(G):
    ws=[w for w in g if w[0]!="|"]
    s=T(ws[0][1])[0]-0.08
    nxt=T([w for w in G[gi+1] if w[0]!="|"][0][1])[0]-0.08 if gi+1<len(G) else 5.66
    e=min(T(ws[-1][1])[1]+0.6,nxt)
    rows=[[]];k=0
    for w in g:
        if w[0]=="|": rows.append([]);continue
        key=len(w)>2
        rows[-1].append(f'<span class="{"w k" if key else "w"}" id="c{gi}w{k}"><span class="in">{w[0]}</span></span>')
        caps_js.append(f'word("#c{gi}w{k}",{T(w[1])[0]-0.06:.2f},{1 if key else 0});');k+=1
    caps_html.append(f'<div class="cap clip" id="cap{gi}" data-start="{s:.2f}" data-duration="{e-s:.2f}" data-track-index="3"><div class="line">{"".join("<span class=row>"+" ".join(r)+"</span>" for r in rows)}</div></div>')
    caps_js.append(f'capOut("#cap{gi}",{e-s:.2f},{s:.2f});')
AUD=[("music","pad",0,0.11,DUR),("sfx-hook","impact",0,0.55,4.2),("sfx-wh1","whoosh",1.2,0.38,1.7),("sfx-sig","shimmer",1.95,0.22,4.0),
 ("sfx-t1","tick",1.56,0.2,0.52),("sfx-t2","tick",3.64,0.2,0.52),("sfx-t3","tick",5.06,0.2,0.52),
 ("sfx-rise","riser",4.1,0.26,1.6),("sfx-hit","impact",5.66,0.5,4.2),("sfx-pasti","shimmer",6.3,0.26,4.0),
 ("sfx-t4","tick",7.5,0.22,0.52),("sfx-wh2","whoosh_soft",9.05,0.32,1.3),("sfx-t5","tick",9.38,0.22,0.52),("sfx-drop","subdrop",10.2,0.4,1.5),
 ("sfx-wh3","whoosh_soft",11.3,0.32,1.3),("sfx-end","shimmer",11.8,0.34,4.0)]
aud="\n".join(f'      <audio id="{i}" src="assets/sfx/{f}.wav" data-start="{st}" data-duration="{min(d,DUR-st):.2f}" data-volume="{v}"{" data-fade-out=\"1.5\"" if i=="music" else ""} data-track-index="{10+k}"></audio>' for k,(i,f,st,v,d) in enumerate(AUD))
s=open(f"{R}/src/tools/index.tpl.html").read()
def IX(m): return s.index(m, s.index("const tl ="))
def rep(a,b):
    global s
    assert a in s, a[:60]; s=s.replace(a,b)
rep('data-duration="24.5" data-width',f'data-duration="{DUR}" data-width')
rep('data-start="0" data-duration="20.28" data-track-index="0"',f'data-start="0" data-duration="{VID}" data-track-index="0"')
rep('<span class="l1" id="h1">Siapa yang paling</span>','<span class="l1" id="h1">Kata-kata hari ini 🤲</span>')
rep('<span class="l2 gold" id="h2">jujur</span>','<span class="l2 gold" id="h2">Syukur &amp; Sabar</span>')
rep('<span class="l3" id="h3">tentang dirimu?</span>','<span class="l3" id="h3">✨ 🤍 ✨</span>')
rep('#hook .l2 { display: inline-block; font-family: "Playfair Display"; font-style: italic; font-weight: 800; font-size: 200px;','#hook .l2 { display: inline-block; font-family: "Playfair Display"; font-style: italic; font-weight: 800; font-size: 118px;')
rep('#hook .l1, #hook .l3 { display: block; font-family: "Montserrat";','#hook .l1, #hook .l3 { display: block; font-family: "Montserrat", "EmojiColor";')
rep('<div id="badge" class="clip" data-start="1.5" data-duration="14.2"','<div id="badge" class="clip" data-start="1.4" data-duration="4.3"')
# quote
rep('''<div id="bars" class="clip" data-start="15.6" data-duration="4.3"''','''<div id="bars" class="clip" data-start="5.55" data-duration="6.1"''')
rep('''<div id="quote" class="clip" data-start="15.68" data-duration="4.2" data-track-index="5" data-track-kind="graphics"><div id="quoteInner">
        <div class="q" id="q0"><span class="gold">YANG PENTING</span></div>
        <div class="q" id="q1"><span class="gold">di mata Allah SWT,</span></div>
        <div class="q" id="q2">kita hamba-Nya</div>
        <div class="q" id="q3">yang macam mana?</div>
      </div></div>''','''<div id="quote" class="clip" data-start="5.62" data-duration="5.95" data-track-index="5" data-track-kind="graphics"><div id="quoteInner">
        <div class="q" id="q0"><span class="gold">JANJI DIA PASTI</span></div>
        <div class="q" id="q1">tidak akan</div>
        <div class="q" id="q1b">dan</div>
        <div class="q" id="q2"><span class="gold">melambatkan</span></div>
        <div class="q" id="q2b"><span class="gold">mempercepatkan</span></div>
        <div class="q" id="q3">walaupun satu saat.</div>
      </div></div>''')
rep('''      #q0 { top: 232px; font-family: "Montserrat"; font-weight: 600; font-size: 30px; letter-spacing: .5em; padding-left: .5em; }
      #q1 { top: 286px; font-family: "Playfair Display"; font-style: italic; font-weight: 700; font-size: 92px; }
      #q2 { top: 410px; font-family: "Playfair Display"; font-weight: 600; font-size: 74px; color: #fff; text-shadow: 0 5px 26px rgba(0,0,0,.8); }
      #q3 { top: 506px; font-family: "Playfair Display"; font-style: italic; font-weight: 600; font-size: 74px; color: #fff; text-shadow: 0 5px 26px rgba(0,0,0,.8); }
      #q1 .gold { padding: 0 14px; filter: drop-shadow(0 6px 24px rgba(0,0,0,.7)); }''','''      #q0 { top: 200px; font-family: "Montserrat"; font-weight: 600; font-size: 34px; letter-spacing: .5em; padding-left: .5em; }
      #q1, #q1b { top: 262px; font-family: "Playfair Display"; font-weight: 600; font-size: 70px; color: #fff; text-shadow: 0 5px 26px rgba(0,0,0,.8); }
      #q2, #q2b { top: 340px; font-family: "Playfair Display"; font-style: italic; font-weight: 800; font-size: 112px; line-height: 1.15; }
      #q3 { top: 484px; font-family: "Playfair Display"; font-style: italic; font-weight: 600; font-size: 66px; color: #fff; text-shadow: 0 5px 26px rgba(0,0,0,.8); }
      #q2 .gold, #q2b .gold { padding: 0 16px; filter: drop-shadow(0 6px 24px rgba(0,0,0,.7)); }''')
rep('<div id="sign" class="clip" data-start="1.7" data-duration="18.2"','<div id="sign" class="clip" data-start="1.7" data-duration="9.9"')
rep('<div id="endcard" class="clip" data-start="19.75" data-duration="4.75"',f'<div id="endcard" class="clip" data-start="{END}" data-duration="4.75"')
# JS: camera
a=IX("      tl.fromTo(cam, { scale: 1.14 }");b=IX("      /* ---------- light leaks")
s=s[:a]+'''      tl.fromTo(cam, { scale: 1.14 }, { scale: 1.08, duration: 1.42, ease: "power2.out" }, 0);
      const cuts = [[1.42, 1.00, 1.02], [3.54, 1.06, 1.08], [5.66, 1.10, 1.13], [6.84, 1.05, 1.07], [11.44, 1.08, 1.09]];
      cuts.forEach(([t, a, b], i) => {
        const end = i + 1 < cuts.length ? cuts[i + 1][0] : 12.03;
        tl.set(cam, { scale: a }, t);
        tl.to(cam, { scale: b, duration: (t === 6.84 ? 7.5 : end) - t, ease: "none" }, t);
      });
      // punches on melambatkan / mempercepatkan
      tl.to(cam, { scale: 1.12, duration: 0.22, ease: "power3.out" }, 7.5);
      tl.to(cam, { scale: 1.08, duration: 1.4, ease: "power2.inOut" }, 7.72);
      tl.to(cam, { scale: 1.15, duration: 0.22, ease: "power3.out" }, 9.38);
      tl.to(cam, { scale: 1.12, duration: 1.8, ease: "power2.inOut" }, 9.6);

'''+s[b:]
a=IX("      leak(1.40, -500");b=IX("      /* ---------- hook")
s=s[:a]+'''      leak(1.28, -500, 400, 0.45);
      leak(5.58, -400, 500, 0.5);
      leak(9.1, 500, -400, 0.3);
      leak(11.4, 300, -300, 0.4);
      tl.to("#flash", { opacity: 0.35, duration: 0.06 }, 5.64);
      tl.to("#flash", { opacity: 0, duration: 0.4 }, 5.70);

'''+s[b:]
rep('tl.to(["#h1", "#h3", "#hrule"], { opacity: 0, y: -30, duration: 0.25, ease: "power2.in" }, 1.42);','tl.to(["#h1", "#h3", "#hrule"], { opacity: 0, y: -30, duration: 0.25, ease: "power2.in" }, 1.24);')
rep('tl.to("#h2", { opacity: 0, scale: 0.7, y: -120, duration: 0.3, ease: "power2.in" }, 1.42);','tl.to("#h2", { opacity: 0, scale: 0.7, y: -120, duration: 0.3, ease: "power2.in" }, 1.24);')
rep('{ opacity: 1, scale: 1, duration: 0.7, ease: E }, 1.55);','{ opacity: 1, scale: 1, duration: 0.7, ease: E }, 1.42);')
rep('tl.to("#badgeInner", { opacity: 0, y: -16, duration: 0.25, ease: "power2.in" }, 15.42);','tl.to("#badgeInner", { opacity: 0, y: -16, duration: 0.25, ease: "power2.in" }, 5.4);')
rep('{ attr: { x: 900 }, duration: 1.0, ease: "power2.inOut" }, 10.2);','{ attr: { x: 900 }, duration: 1.0, ease: "power2.inOut" }, 8.6);')
rep('tl.to("#signBox", { opacity: 0, y: 10, duration: 0.3, ease: "power2.in" }, 19.55);','tl.to("#signBox", { opacity: 0, y: 10, duration: 0.3, ease: "power2.in" }, 11.25);')
a=IX('      tl.fromTo("#barT"');b=IX("      /* ---------- end card")
s=s[:a]+'''      tl.fromTo("#barT", { yPercent: -100 }, { yPercent: 0, duration: 0.5, ease: "power3.inOut" }, 5.55);
      tl.fromTo("#barB", { yPercent: 100 }, { yPercent: 0, duration: 0.5, ease: "power3.inOut" }, 5.55);
      tl.to("#dim", { opacity: 0.32, duration: 0.6, ease: "power2.out" }, 5.55);
      tl.fromTo("#q0", { opacity: 0, scale: 1.15 }, { opacity: 1, scale: 1, duration: 0.6, ease: E }, 5.70);
      tl.fromTo("#q1", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.5, ease: E }, 7.04);
      tl.fromTo("#q2", { opacity: 0, y: 40, scale: 0.9 }, { opacity: 1, y: 0, scale: 1, duration: 0.6, ease: "expo.out" }, 7.50);
      tl.fromTo("#q3", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.5, ease: E }, 8.14);
      // mirror swap: melambatkan -> mempercepatkan
      tl.to("#q1", { opacity: 0, y: -24, duration: 0.25, ease: "power2.in" }, 9.0);
      tl.fromTo("#q1b", { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.4, ease: E }, 9.14);
      tl.to("#q2", { opacity: 0, y: -40, scale: 0.9, duration: 0.25, ease: "power2.in" }, 9.14);
      tl.fromTo("#q2b", { opacity: 0, y: 40, scale: 0.9 }, { opacity: 1, y: 0, scale: 1, duration: 0.6, ease: "expo.out" }, 9.38);
      tl.to("#q3", { scale: 1.08, duration: 0.25, ease: "power2.out" }, 10.2);
      tl.to("#q3", { scale: 1, duration: 0.5, ease: "power2.inOut" }, 10.45);
      tl.to("#quoteInner", { opacity: 0, duration: 0.2, ease: "power2.in" }, 11.32);

'''+s[b:]
off=END-19.75
def shift(m): return f"{float(m.group(1))+off:.2f})"
a=IX("      /* ---------- end card");b=IX("      window.__timelines =")
blk=re.sub(r"(\d+\.\d+)\)(;?)$",lambda m:shift(m)+m.group(2),s[a:b],flags=re.M)
blk=re.sub(r'sigDraw\("B", [^)]*\)',f'sigDraw("B", {20.05+off:.2f}, 1.25)',blk)
s=s[:a]+blk+s[b:]
out=s.replace("%%SIG_D%%",sig["d"]).replace("%%SIG_VB%%",sig["vb"]).replace("%%CAPS%%","\n      ".join(caps_html)).replace("%%CAPS_JS%%","\n      ".join(caps_js)).replace("%%AUDIO%%",aud)
open(f"{R}/syukur-sabar/index.html","w").write(out); print("ok",DUR)
