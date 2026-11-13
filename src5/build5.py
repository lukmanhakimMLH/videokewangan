import json,re
R="/home/user/videokewangan"
sig=json.load(open(f"{R}/src/sig.json"));W=json.load(open(f"{R}/src5/cutwords.json"))
def T(i): return W[i]["s"],W[i]["e"]
END=22.75; DUR=round(END+4.75,2); VID=23.43
BR=("|",None)
G=[[("Ceritanya,",4),("semalam",6),BR,("saya",7),("set",8)],
   [("untuk",10),("buat",11),("taklimat",12,1),BR,("kepada",13),("client.",14,1)],
   [("Dia",15),("pun",16),("memang",17),BR,("nak",18),("bagi.",19)],
   [("So",20),("bila",21),("tanya,",22),("dia",23),("kata",24),BR,("OK,",25),("dalam",26),("2 orang.",27,1)],
   [("Tapi",29),("bila",30),("sampai,",31)],
   [("bukan",32),("2",33),("orang,",34),BR,("10 orang!",35,1)],
   [("Dan",37),("ada",38),("lagi",39),BR,("pertambahan.",40,1)],
   [("Yang",41),("mana",42),("saya",43),("perlu",44),BR,("buat",45),("hari",46),("ini",47),("pula,",48)],
   [("untuk",49),("taklimat",50),BR,("yang",51),("kali",52),("kedua.",53,1)]]
caps_html=[];caps_js=[]
for gi,g in enumerate(G):
    ws=[w for w in g if w[0]!="|"]
    s=T(ws[0][1])[0]-0.08
    nxt=T([w for w in G[gi+1] if w[0]!="|"][0][1])[0]-0.08 if gi+1<len(G) else 18.62
    e=min(T(ws[-1][1])[1]+0.6,nxt)
    rows=[[]];k=0
    for w in g:
        if w[0]=="|": rows.append([]);continue
        key=len(w)>2
        rows[-1].append(f'<span class="{"w k" if key else "w"}" id="c{gi}w{k}"><span class="in">{w[0]}</span></span>')
        caps_js.append(f'word("#c{gi}w{k}",{T(w[1])[0]-0.06:.2f},{1 if key else 0});');k+=1
    caps_html.append(f'<div class="cap clip" id="cap{gi}" data-start="{s:.2f}" data-duration="{e-s:.2f}" data-track-index="3"><div class="line">{"".join("<span class=row>"+" ".join(r)+"</span>" for r in rows)}</div></div>')
    caps_js.append(f'capOut("#cap{gi}",{e-s:.2f},{s:.2f});')
AUD=[("music","pad",0,0.1,DUR),("sfx-hook","impact",0,0.55,4.2),("sfx-wh1","whoosh",1.05,0.38,1.7),("sfx-sig","shimmer",1.95,0.22,4.0),
 ("sfx-t1","tick",4.02,0.2,0.52),("sfx-t2","tick",4.9,0.2,0.52),("sfx-t3","tick",8.76,0.22,0.52),("sfx-wh2","whoosh_soft",9.6,0.28,1.3),
 ("sfx-rise","riser",10.3,0.22,1.6),("sfx-drop","subdrop",11.86,0.45,1.5),("sfx-t4","tick",13.74,0.2,0.52),("sfx-t5","tick",18.18,0.2,0.52),
 ("sfx-hit","impact",18.64,0.5,4.2),("sfx-tuhan","shimmer",20.42,0.26,4.0),("sfx-wh3","whoosh_soft",20.95,0.28,1.3),("sfx-redha","shimmer",22.12,0.3,4.0),
 ("sfx-wh4","whoosh_soft",22.62,0.3,1.3),("sfx-end","shimmer",23.05,0.34,4.0)]
aud="\n".join(f'      <audio id="{i}" src="assets/sfx/{f}.wav" data-start="{st}" data-duration="{min(d,DUR-st):.2f}" data-volume="{v}"{" data-fade-out=\"1.5\"" if i=="music" else ""} data-track-index="{10+k}"></audio>' for k,(i,f,st,v,d) in enumerate(AUD))
s=open(f"{R}/src/tools/index.tpl.html").read()
def IX(m): return s.index(m, s.index("const tl ="))
def rep(a,b):
    global s
    assert a in s, a[:60]; s=s.replace(a,b)
rep('data-duration="24.5" data-width',f'data-duration="{DUR}" data-width')
rep('data-start="0" data-duration="20.28" data-track-index="0"',f'data-start="0" data-duration="{VID}" data-track-index="0"')
rep('{ y: -6, duration: 1.4, ease: "none" }, 0);','{ y: -6, duration: 1.05, ease: "none" }, 0);')
rep('{ y: 6, duration: 1.4, ease: "none" }, 0);','{ y: 6, duration: 1.05, ease: "none" }, 0);')
rep('<span class="l1" id="h1">Siapa yang paling</span>','<span class="l1" id="h1">Kata-kata hari ini 🤲</span>')
rep('<span class="l2 gold" id="h2">jujur</span>','<span class="l2 gold" id="h2">Rezeki &amp; Redha</span>')
rep('<span class="l3" id="h3">tentang dirimu?</span>','<span class="l3" id="h3">✨ 🙏 ✨</span>')
rep('#hook .l2 { display: inline-block; font-family: "Playfair Display"; font-style: italic; font-weight: 800; font-size: 200px;','#hook .l2 { display: inline-block; font-family: "Playfair Display"; font-style: italic; font-weight: 800; font-size: 118px;')
rep('#hook .l1, #hook .l3 { display: block; font-family: "Montserrat";','#hook .l1, #hook .l3 { display: block; font-family: "Montserrat", "EmojiColor";')
rep('<div id="badge" class="clip" data-start="1.5" data-duration="14.2"','<div id="badge" class="clip" data-start="1.15" data-duration="17.5"')
# quote
rep('''<div id="bars" class="clip" data-start="15.6" data-duration="4.3"''','''<div id="bars" class="clip" data-start="18.6" data-duration="4.3"''')
rep('''<div id="quote" class="clip" data-start="15.68" data-duration="4.2" data-track-index="5" data-track-kind="graphics"><div id="quoteInner">
        <div class="q" id="q0"><span class="gold">YANG PENTING</span></div>
        <div class="q" id="q1"><span class="gold">di mata Allah SWT,</span></div>
        <div class="q" id="q2">kita hamba-Nya</div>
        <div class="q" id="q3">yang macam mana?</div>
      </div></div>''','''<div id="quote" class="clip" data-start="18.66" data-duration="4.2" data-track-index="5" data-track-kind="graphics"><div id="quoteInner">
        <div class="q" id="q0"><span class="gold">ORANG KATA REZEKI</span></div>
        <div class="q" id="q1">kita jangan buat</div>
        <div class="q" id="q1b">kita hanya mengharapkan</div>
        <div class="q" id="q2"><span class="gold">kerja Tuhan.</span></div>
        <div class="q" id="q2b"><span class="gold">redha-Nya.</span></div>
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
rep('<div id="sign" class="clip" data-start="1.7" data-duration="18.2"','<div id="sign" class="clip" data-start="1.7" data-duration="21.1"')
rep('<div id="endcard" class="clip" data-start="19.75" data-duration="4.75"',f'<div id="endcard" class="clip" data-start="{END}" data-duration="4.75"')
# JS: camera
a=IX("      tl.fromTo(cam, { scale: 1.14 }");b=IX("      /* ---------- light leaks")
s=s[:a]+'''      tl.fromTo(cam, { scale: 1.14 }, { scale: 1.08, duration: 1.23, ease: "power2.out" }, 0);
      const cuts = [[1.23, 1.00, 1.02], [5.11, 1.06, 1.07], [5.59, 1.00, 1.03], [9.42, 1.06, 1.08], [12.67, 1.00, 1.03], [18.70, 1.06, 1.10], [21.05, 1.09, 1.14], [22.77, 1.08, 1.09]];
      cuts.forEach(([t, a, b], i) => {
        const end = i + 1 < cuts.length ? cuts[i + 1][0] : 23.43;
        tl.set(cam, { scale: a }, t);
        tl.to(cam, { scale: b, duration: (t === 9.42 ? 11.9 : end) - t, ease: "none" }, t);
      });
      // punch on "10 orang!"
      tl.to(cam, { scale: 1.14, duration: 0.2, ease: "power3.out" }, 11.9);
      tl.to(cam, { scale: 1.11, duration: 0.55, ease: "power2.inOut" }, 12.1);

'''+s[b:]
a=IX("      leak(1.40, -500");b=IX("      /* ---------- hook")
s=s[:a]+'''      leak(1.1, -500, 400, 0.45);
      leak(9.55, 500, -400, 0.3);
      leak(18.62, -400, 500, 0.5);
      leak(22.7, 300, -300, 0.4);
      tl.to("#flash", { opacity: 0.35, duration: 0.06 }, 18.66);
      tl.to("#flash", { opacity: 0, duration: 0.4 }, 18.72);
      tl.to("#flash", { opacity: 0.2, duration: 0.05 }, 11.9);
      tl.to("#flash", { opacity: 0, duration: 0.3 }, 11.95);

'''+s[b:]
rep('tl.to(["#h1", "#h3", "#hrule"], { opacity: 0, y: -30, duration: 0.25, ease: "power2.in" }, 1.42);','tl.to(["#h1", "#h3", "#hrule"], { opacity: 0, y: -30, duration: 0.25, ease: "power2.in" }, 1.1);')
rep('tl.to("#h2", { opacity: 0, scale: 0.7, y: -120, duration: 0.3, ease: "power2.in" }, 1.42);','tl.to("#h2", { opacity: 0, scale: 0.7, y: -120, duration: 0.3, ease: "power2.in" }, 1.1);')
rep('{ opacity: 1, scale: 1, duration: 0.7, ease: E }, 1.55);','{ opacity: 1, scale: 1, duration: 0.7, ease: E }, 1.25);')
rep('tl.to("#badgeInner", { opacity: 0, y: -16, duration: 0.25, ease: "power2.in" }, 15.42);','tl.to("#badgeInner", { opacity: 0, y: -16, duration: 0.25, ease: "power2.in" }, 18.4);')
rep('{ attr: { x: 900 }, duration: 1.0, ease: "power2.inOut" }, 10.2);','{ attr: { x: 900 }, duration: 1.0, ease: "power2.inOut" }, 14.0);')
rep('tl.to("#signBox", { opacity: 0, y: 10, duration: 0.3, ease: "power2.in" }, 19.55);','tl.to("#signBox", { opacity: 0, y: 10, duration: 0.3, ease: "power2.in" }, 22.55);')
a=IX('      tl.fromTo("#barT"');b=IX("      /* ---------- end card")
s=s[:a]+'''      tl.fromTo("#barT", { yPercent: -100 }, { yPercent: 0, duration: 0.5, ease: "power3.inOut" }, 18.6);
      tl.fromTo("#barB", { yPercent: 100 }, { yPercent: 0, duration: 0.5, ease: "power3.inOut" }, 18.6);
      tl.to("#dim", { opacity: 0.32, duration: 0.6, ease: "power2.out" }, 18.6);
      tl.fromTo("#q0", { opacity: 0, scale: 1.15 }, { opacity: 1, scale: 1, duration: 0.6, ease: E }, 18.72);
      tl.fromTo("#q1", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.45, ease: E }, 19.76);
      tl.fromTo("#q2", { opacity: 0, y: 40, scale: 0.9 }, { opacity: 1, y: 0, scale: 1, duration: 0.6, ease: "expo.out" }, 20.42);
      tl.to("#q1", { opacity: 0, y: -24, duration: 0.22, ease: "power2.in" }, 20.92);
      tl.to("#q2", { opacity: 0, y: -40, scale: 0.9, duration: 0.25, ease: "power2.in" }, 20.98);
      tl.fromTo("#q1b", { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.4, ease: E }, 21.08);
      tl.fromTo("#q2b", { opacity: 0, y: 40, scale: 0.9 }, { opacity: 1, y: 0, scale: 1, duration: 0.6, ease: "expo.out" }, 22.12);
      tl.to("#quoteInner", { opacity: 0, duration: 0.2, ease: "power2.in" }, 22.62);

'''+s[b:]
off=END-19.75
def shift(m): return f"{float(m.group(1))+off:.2f})"
a=IX("      /* ---------- end card");b=IX("      window.__timelines =")
blk=re.sub(r"(\d+\.\d+)\)(;?)$",lambda m:shift(m)+m.group(2),s[a:b],flags=re.M)
blk=re.sub(r'sigDraw\("B", [^)]*\)',f'sigDraw("B", {20.05+off:.2f}, 1.25)',blk)
s=s[:a]+blk+s[b:]
out=s.replace("%%SIG_D%%",sig["d"]).replace("%%SIG_VB%%",sig["vb"]).replace("%%CAPS%%","\n      ".join(caps_html)).replace("%%CAPS_JS%%","\n      ".join(caps_js)).replace("%%AUDIO%%",aud)
open(f"{R}/rezeki-redha/index.html","w").write(out); print("ok",DUR)
