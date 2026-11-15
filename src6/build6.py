import json,re
R="/home/user/videokewangan"
sig=json.load(open(f"{R}/src/sig.json"));W=json.load(open(f"{R}/src6/cutwords.json"))
def T(i): return W[i]["s"],W[i]["e"]
END=53.15; DUR=round(END+4.75,2); VID=53.96
BR=("|",None)
G=[[("Apa",4),("saja",5),("pertolongan,",6,1),BR,("rezeki,",7,1),("semuanya",8)],
   [("daripada",9),("Dia.",10,1)],
   [("Kita",11),("ambil",12),("satu",13),("kisah",14)],
   [("Pilihan",16),("Raya",17),("Negeri",18),BR,("Melaka",19,1),("yang",20)],
   [("baru",21),("habis",22),("malam.",23)],
   [("Kita",24),("tengok",25),("kat",26),BR,("DUN Bukit Katil.",27,1)],
   [("Satu",30),("nama",31),("kecil,",32,1),BR,("Ridzuan Sarif.",33,1)],
   [("Seorang",35),("penjawat",36),("awam",37),BR,("yang",38),("gaji",39),("dah",40)],
   [("lima angka,",41,1)],
   [("berkhidmat",43),("dengan",44),("KKM,",45,1)],
   [("Kementerian",46),("Kesihatan",47),BR,("Malaysia.",48)],
   [("Sanggup",49),("bersara awal",50,1),BR,("disebabkan",52),("partinya",53)],
   [("minta",54),("dia",55),("untuk",56),BR,("bertanding.",57,1)],
   [("Bertanding",58),("baru.",59),BR,("Bukan",60),("confirm",61,1),("dapat,",62)],
   [("tapi",63),("dia",64),("sanggup",65),BR,("letak jawatan,",66,1)],
   [("bersara",68),("awal",69),BR,("untuk",70),("lawan",71)],
   [("dengan",72),("satu",73),BR,("nama besar.",74,1)],
   [("Tetapi,",76),("di",77),("sini",78),BR,("kita",79),("tengoknya,",80)],
   [("kita",81),("hanya",82),("mengharapkan",83),BR,("pertolongan",84,1),("daripada",85),("Dia.",86,1)],
   [("Walaupun",87),("dia",88),BR,("tak",89),("ada",90),("nama,",91,1)],
   [("bukan",92),("siapa-siapa,",93)],
   [("tapi",95),("dengan",96),BR,("pertolongan Allah,",97,1)],
   [("dia",99),("boleh",100),("menang",101,1)],
   [("dengan",102),("majoriti",103,1),BR,("yang",104),("agak",105),("besar.",106)],
   [("Dengan",107),("orang",108),BR,("yang",109),("ada",110),("nama.",111,1)],
   [("So,",112),("macam",113),("tu",114),("kita,",116)],
   [("terutama",117),("yang",118),("dalam",119),BR,("dunia",120),("sales.",121,1)],
   [("Hari",122),("ini",123),("kita",124),("keluar,",125)],
   [("kita",126),("tak",127),("tahu",128),("lagi",129),BR,("rezeki",130,1),("kita",131),("kat",132),("mana.",133)]]
caps_html=[];caps_js=[]
for gi,g in enumerate(G):
    ws=[w for w in g if w[0]!="|"]
    s=T(ws[0][1])[0]-0.08
    nxt=T([w for w in G[gi+1] if w[0]!="|"][0][1])[0]-0.08 if gi+1<len(G) else 50.38
    e=min(T(ws[-1][1])[1]+0.6,nxt)
    rows=[[]];k=0
    for w in g:
        if w[0]=="|": rows.append([]);continue
        key=len(w)>2
        rows[-1].append(f'<span class="{"w k" if key else "w"}" id="c{gi}w{k}"><span class="in">{w[0]}</span></span>')
        caps_js.append(f'word("#c{gi}w{k}",{T(w[1])[0]-0.06:.2f},{1 if key else 0});');k+=1
    caps_html.append(f'<div class="cap clip" id="cap{gi}" data-start="{s:.2f}" data-duration="{e-s:.2f}" data-track-index="3"><div class="line">{"".join("<span class=row>"+" ".join(r)+"</span>" for r in rows)}</div></div>')
    caps_js.append(f'capOut("#cap{gi}",{e-s:.2f},{s:.2f});')
AUD=[("music","pad",0,0.1,DUR),("sfx-hook","impact",0,0.55,4.2),("sfx-wh1","whoosh",1.0,0.38,1.7),("sfx-sig","shimmer",1.95,0.22,4.0),
 ("sfx-t1","tick",1.76,0.2,0.52),("sfx-t2","tick",4.2,0.2,0.52),("sfx-wh2","whoosh_soft",4.62,0.26,1.3),("sfx-t3","tick",6.88,0.2,0.52),
 ("sfx-t4","tick",10.2,0.2,0.52),("sfx-t5","tick",12.0,0.2,0.52),("sfx-t6","tick",15.1,0.22,0.52),("sfx-t7","tick",16.5,0.2,0.52),
 ("sfx-t8","tick",19.15,0.2,0.52),("sfx-t9","tick",24.78,0.2,0.52),("sfx-t10","tick",26.7,0.2,0.52),("sfx-drop1","subdrop",30.7,0.35,1.5),
 ("sfx-wh3","whoosh_soft",31.6,0.26,1.3),("sfx-t11","tick",35.34,0.2,0.52),("sfx-t12","tick",37.34,0.2,0.52),("sfx-allah","shimmer",39.42,0.3,4.0),
 ("sfx-t13","tick",40.86,0.22,0.52),("sfx-t14","tick",41.38,0.2,0.52),("sfx-wh4","whoosh_soft",44.6,0.26,1.3),("sfx-t15","tick",47.1,0.2,0.52),
 ("sfx-t16","tick",49.32,0.2,0.52),("sfx-rise","riser",48.85,0.22,1.6),("sfx-hit","impact",50.42,0.5,4.2),("sfx-jamin","shimmer",52.26,0.32,4.0),
 ("sfx-wh5","whoosh_soft",53.0,0.3,1.3),("sfx-end","shimmer",53.45,0.34,4.0)]
aud="\n".join(f'      <audio id="{i}" src="assets/sfx/{f}.wav" data-start="{st}" data-duration="{min(d,DUR-st):.2f}" data-volume="{v}"{" data-fade-out=\"1.5\"" if i=="music" else ""} data-track-index="{10+k}"></audio>' for k,(i,f,st,v,d) in enumerate(AUD))
s=open(f"{R}/src/tools/index.tpl.html").read()
def IX(m): return s.index(m, s.index("const tl ="))
def rep(a,b):
    global s
    assert a in s, a[:60]; s=s.replace(a,b)
rep('data-duration="24.5" data-width',f'data-duration="{DUR}" data-width')
rep('data-start="0" data-duration="20.28" data-track-index="0"',f'data-start="0" data-duration="{VID}" data-track-index="0"')
rep('{ y: -6, duration: 1.4, ease: "none" }, 0);','{ y: -6, duration: 1.08, ease: "none" }, 0);')
rep('{ y: 6, duration: 1.4, ease: "none" }, 0);','{ y: 6, duration: 1.08, ease: "none" }, 0);')
rep('<span class="l1" id="h1">Siapa yang paling</span>','<span class="l1" id="h1">Kata-kata hari ini 🤲</span>')
rep('<span class="l2 gold" id="h2">jujur</span>','<span class="l2 gold" id="h2">Rezeki Dah Dijamin</span>')
rep('<span class="l3" id="h3">tentang dirimu?</span>','<span class="l3" id="h3">✨ 🗳️ 🙏</span>')
rep('#hook .l2 { display: inline-block; font-family: "Playfair Display"; font-style: italic; font-weight: 800; font-size: 200px;','#hook .l2 { display: inline-block; font-family: "Playfair Display"; font-style: italic; font-weight: 800; font-size: 80px;')
rep('#hook .l1, #hook .l3 { display: block; font-family: "Montserrat";','#hook .l1, #hook .l3 { display: block; font-family: "Montserrat", "EmojiColor";')
rep('<div id="badge" class="clip" data-start="1.5" data-duration="14.2"','<div id="badge" class="clip" data-start="1.1" data-duration="49.1"')
# quote
rep('''<div id="bars" class="clip" data-start="15.6" data-duration="4.3"''','''<div id="bars" class="clip" data-start="50.32" data-duration="2.9"''')
rep('''<div id="quote" class="clip" data-start="15.68" data-duration="4.2" data-track-index="5" data-track-kind="graphics"><div id="quoteInner">
        <div class="q" id="q0"><span class="gold">YANG PENTING</span></div>
        <div class="q" id="q1"><span class="gold">di mata Allah SWT,</span></div>
        <div class="q" id="q2">kita hamba-Nya</div>
        <div class="q" id="q3">yang macam mana?</div>
      </div></div>''','''<div id="quote" class="clip" data-start="50.38" data-duration="2.82" data-track-index="5" data-track-kind="graphics"><div id="quoteInner">
        <div class="q" id="q0"><span class="gold">TAPI YANG PENTING</span></div>
        <div class="q" id="q1">rezeki kita</div>
        <div class="q" id="q2"><span class="gold">dah dijamin.</span></div>
      </div></div>''')
rep('''      #q0 { top: 232px; font-family: "Montserrat"; font-weight: 600; font-size: 30px; letter-spacing: .5em; padding-left: .5em; }
      #q1 { top: 286px; font-family: "Playfair Display"; font-style: italic; font-weight: 700; font-size: 92px; }
      #q2 { top: 410px; font-family: "Playfair Display"; font-weight: 600; font-size: 74px; color: #fff; text-shadow: 0 5px 26px rgba(0,0,0,.8); }
      #q3 { top: 506px; font-family: "Playfair Display"; font-style: italic; font-weight: 600; font-size: 74px; color: #fff; text-shadow: 0 5px 26px rgba(0,0,0,.8); }
      #q1 .gold { padding: 0 14px; filter: drop-shadow(0 6px 24px rgba(0,0,0,.7)); }''','''      #q0 { top: 200px; font-family: "Montserrat"; font-weight: 600; font-size: 34px; letter-spacing: .5em; padding-left: .5em; }
      #q1 { top: 262px; font-family: "Playfair Display"; font-weight: 600; font-size: 70px; color: #fff; text-shadow: 0 5px 26px rgba(0,0,0,.8); }
      #q2 { top: 346px; font-family: "Playfair Display"; font-style: italic; font-weight: 800; font-size: 120px; line-height: 1.15; }
      #q3 { top: 350px; font-family: "Playfair Display"; font-style: italic; font-weight: 600; font-size: 66px; color: #fff; text-shadow: 0 5px 26px rgba(0,0,0,.8); }
      #q2 .gold { padding: 0 16px; filter: drop-shadow(0 6px 24px rgba(0,0,0,.7)); }''')
rep('<div id="sign" class="clip" data-start="1.7" data-duration="18.2"','<div id="sign" class="clip" data-start="1.7" data-duration="51.4"')
rep('<div id="endcard" class="clip" data-start="19.75" data-duration="4.75"',f'<div id="endcard" class="clip" data-start="{END}" data-duration="4.75"')
# JS: camera
a=IX("      tl.fromTo(cam, { scale: 1.14 }");b=IX("      /* ---------- light leaks")
s=s[:a]+'''      tl.fromTo(cam, { scale: 1.14 }, { scale: 1.08, duration: 1.21, ease: "power2.out" }, 0);
      const cuts = [[1.21, 1.00, 1.025], [4.81, 1.06, 1.085], [6.08, 1.00, 1.025], [7.57, 1.06, 1.085], [9.38, 1.00, 1.025], [13.12, 1.06, 1.085], [14.42, 1.00, 1.025], [21.94, 1.06, 1.085], [23.34, 1.00, 1.025], [26.92, 1.06, 1.085], [29.15, 1.00, 1.025], [31.57, 1.06, 1.085], [32.47, 1.00, 1.025], [34.57, 1.06, 1.085], [38.05, 1.00, 1.025], [40.6, 1.06, 1.085], [44.63, 1.00, 1.025], [46.15, 1.06, 1.085], [47.74, 1.00, 1.025], [50.49, 1.06, 1.085], [53.14, 1.00, 1.025]];
      const punches = [39.44, 40.86];
      cuts.forEach(([t, a, b], i) => {
        const end = i + 1 < cuts.length ? cuts[i + 1][0] : 53.96;
        tl.set(cam, { scale: a }, t);
        tl.to(cam, { scale: b, duration: Math.min(end, ...punches.filter(p => p > t).concat([end])) - t, ease: "none" }, t);
      });
      tl.to(cam, { scale: 1.12, duration: 0.22, ease: "power3.out" }, 39.44);
      tl.to(cam, { scale: 1.09, duration: 0.6, ease: "power2.inOut" }, 39.66);
      tl.to(cam, { scale: 1.13, duration: 0.2, ease: "power3.out" }, 40.86);
      tl.to(cam, { scale: 1.10, duration: 0.5, ease: "power2.inOut" }, 41.06);
      tl.to(cam, { scale: 1.16, duration: 2.5, ease: "power1.inOut" }, 50.49);

'''+s[b:]
a=IX("      leak(1.40, -500");b=IX("      /* ---------- hook")
s=s[:a]+'''      leak(1.0, -500, 400, 0.45);
      leak(4.6, 500, -400, 0.28);
      leak(31.55, -400, 500, 0.3);
      leak(44.6, 500, -400, 0.28);
      leak(50.35, -400, 500, 0.5);
      leak(53.05, 300, -300, 0.4);
      tl.to("#flash", { opacity: 0.35, duration: 0.06 }, 50.42);
      tl.to("#flash", { opacity: 0, duration: 0.4 }, 50.48);
      tl.to("#flash", { opacity: 0.2, duration: 0.05 }, 39.44);
      tl.to("#flash", { opacity: 0, duration: 0.35 }, 39.49);

'''+s[b:]
rep('tl.to(["#h1", "#h3", "#hrule"], { opacity: 0, y: -30, duration: 0.25, ease: "power2.in" }, 1.42);','tl.to(["#h1", "#h3", "#hrule"], { opacity: 0, y: -30, duration: 0.25, ease: "power2.in" }, 1.1);')
rep('tl.to("#h2", { opacity: 0, scale: 0.7, y: -120, duration: 0.3, ease: "power2.in" }, 1.42);','tl.to("#h2", { opacity: 0, scale: 0.7, y: -120, duration: 0.3, ease: "power2.in" }, 1.1);')
rep('{ opacity: 1, scale: 1, duration: 0.7, ease: E }, 1.55);','{ opacity: 1, scale: 1, duration: 0.7, ease: E }, 1.15);')
rep('tl.to("#badgeInner", { opacity: 0, y: -16, duration: 0.25, ease: "power2.in" }, 15.42);','tl.to("#badgeInner", { opacity: 0, y: -16, duration: 0.25, ease: "power2.in" }, 50.1);')
rep('{ attr: { x: 900 }, duration: 1.0, ease: "power2.inOut" }, 10.2);','{ attr: { x: 900 }, duration: 1.0, ease: "power2.inOut" }, 26.0);')
rep('tl.to("#signBox", { opacity: 0, y: 10, duration: 0.3, ease: "power2.in" }, 19.55);','tl.to("#signBox", { opacity: 0, y: 10, duration: 0.3, ease: "power2.in" }, 52.95);')
a=IX('      tl.fromTo("#barT"');b=IX("      /* ---------- end card")
s=s[:a]+'''      tl.fromTo("#barT", { yPercent: -100 }, { yPercent: 0, duration: 0.45, ease: "power3.inOut" }, 50.32);
      tl.fromTo("#barB", { yPercent: 100 }, { yPercent: 0, duration: 0.45, ease: "power3.inOut" }, 50.32);
      tl.to("#dim", { opacity: 0.32, duration: 0.5, ease: "power2.out" }, 50.32);
      tl.fromTo("#q0", { opacity: 0, scale: 1.15 }, { opacity: 1, scale: 1, duration: 0.5, ease: E }, 50.44);
      tl.fromTo("#q1", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.45, ease: E }, 51.52);
      tl.fromTo("#q2", { opacity: 0, y: 40, scale: 1.3 }, { opacity: 1, y: 0, scale: 1, duration: 0.6, ease: "back.out(1.8)" }, 52.24);
      tl.to("#quoteInner", { opacity: 0, duration: 0.15, ease: "power2.in" }, 53.0);

'''+s[b:]
off=END-19.75
def shift(m): return f"{float(m.group(1))+off:.2f})"
a=IX("      /* ---------- end card");b=IX("      window.__timelines =")
blk=re.sub(r"(\d+\.\d+)\)(;?)$",lambda m:shift(m)+m.group(2),s[a:b],flags=re.M)
blk=re.sub(r'sigDraw\("B", [^)]*\)',f'sigDraw("B", {20.05+off:.2f}, 1.25)',blk)
s=s[:a]+blk+s[b:]
out=s.replace("%%SIG_D%%",sig["d"]).replace("%%SIG_VB%%",sig["vb"]).replace("%%CAPS%%","\n      ".join(caps_html)).replace("%%CAPS_JS%%","\n      ".join(caps_js)).replace("%%AUDIO%%",aud)
open(f"{R}/pilihan-raya/index.html","w").write(out); print("ok",DUR)
