s=open("/home/user/videokewangan/src2/build2.py").read()
def R(a,b):
    global s
    assert a in s,a[:80]; s=s.replace(a,b)
def block(anchor,new):
    global s
    a=s.index(anchor)+len("s=s[:a]+'''");b=s.index("'''+s[b:]",a)
    s=s[:a]+new+s[b:]
R('src2/cutwords.json','src5/cutwords.json')
R('END=11.5; DUR=round(END+4.75,2); VID=12.03','END=22.75; DUR=round(END+4.75,2); VID=23.43')
R('''G=[[("Bersyukurlah",4,1),("dengan",5),BR,("apa",6),("yang",7),("ada,",8)],
   [("dan",9),("bersabarlah",10,1)],
   [("dengan",11),("apa",12),("yang",13),BR,("belum",14,1),("ada.",15)]]''','''G=[[("Ceritanya,",4),("semalam",6),BR,("saya",7),("set",8)],
   [("untuk",10),("buat",11),("taklimat",12,1),BR,("kepada",13),("client.",14,1)],
   [("Dia",15),("pun",16),("memang",17),BR,("nak",18),("bagi.",19)],
   [("So",20),("bila",21),("tanya,",22),BR,("dia",23),("kata",24),("OK,",25)],
   [("dalam",26),("2",27,1),("orang.",28)],
   [("Tapi",29),("bila",30),("sampai,",31)],
   [("bukan",32),("2",33),("orang,",34),BR,("10",35,1),("orang!",36)],
   [("Dan",37),("ada",38),("lagi",39),BR,("pertambahan.",40,1)],
   [("Yang",41),("mana",42),("saya",43),("perlu",44),BR,("buat",45),("hari",46),("ini",47),("pula,",48)],
   [("untuk",49),("taklimat",50),BR,("yang",51),("kali",52),("kedua.",53,1)]]''')
R('else 5.66','else 18.62')
a=s.index('AUD=[');b=s.index('aud="\\n"')
s=s[:a]+'''AUD=[("music","pad",0,0.1,DUR),("sfx-hook","impact",0,0.55,4.2),("sfx-wh1","whoosh",1.05,0.38,1.7),("sfx-sig","shimmer",1.95,0.22,4.0),
 ("sfx-t1","tick",4.02,0.2,0.52),("sfx-t2","tick",4.9,0.2,0.52),("sfx-t3","tick",8.76,0.22,0.52),("sfx-wh2","whoosh_soft",9.6,0.28,1.3),
 ("sfx-rise","riser",10.3,0.22,1.6),("sfx-drop","subdrop",11.86,0.45,1.5),("sfx-t4","tick",13.74,0.2,0.52),("sfx-t5","tick",18.18,0.2,0.52),
 ("sfx-hit","impact",18.64,0.5,4.2),("sfx-tuhan","shimmer",20.42,0.26,4.0),("sfx-wh3","whoosh_soft",20.95,0.28,1.3),("sfx-redha","shimmer",22.12,0.3,4.0),
 ("sfx-wh4","whoosh_soft",22.62,0.3,1.3),("sfx-end","shimmer",23.05,0.34,4.0)]
'''+s[b:]
R('<span class="l1" id="h1">Kata-kata hari ini 🤲</span>','<span class="l1" id="h1">Kata-kata hari ini 🤲</span>')
R('<span class="l2 gold" id="h2">Syukur &amp; Sabar</span>','<span class="l2 gold" id="h2">Rezeki &amp; Redha</span>')
R('<span class="l3" id="h3">✨ 🤍 ✨</span>','<span class="l3" id="h3">✨ 🙏 ✨</span>')
R("rep('<div id=\"badge\" class=\"clip\" data-start=\"1.5\" data-duration=\"14.2\"','<div id=\"badge\" class=\"clip\" data-start=\"1.4\" data-duration=\"4.3\"')","rep('<div id=\"badge\" class=\"clip\" data-start=\"1.5\" data-duration=\"14.2\"','<div id=\"badge\" class=\"clip\" data-start=\"1.15\" data-duration=\"17.5\"')")
R('data-start="5.55" data-duration="6.1"','data-start="18.6" data-duration="4.3"')
R('''<div id="quote" class="clip" data-start="5.62" data-duration="5.95" data-track-index="5" data-track-kind="graphics"><div id="quoteInner">
        <div class="q" id="q0"><span class="gold">JANJI DIA PASTI</span></div>
        <div class="q" id="q1">tidak akan</div>
        <div class="q" id="q1b">dan</div>
        <div class="q" id="q2"><span class="gold">melambatkan</span></div>
        <div class="q" id="q2b"><span class="gold">mempercepatkan</span></div>
        <div class="q" id="q3">walaupun satu saat.</div>''','''<div id="quote" class="clip" data-start="18.66" data-duration="4.2" data-track-index="5" data-track-kind="graphics"><div id="quoteInner">
        <div class="q" id="q0"><span class="gold">ORANG KATA REZEKI</span></div>
        <div class="q" id="q1">kita jangan buat</div>
        <div class="q" id="q1b">kita hanya mengharapkan</div>
        <div class="q" id="q2"><span class="gold">kerja Tuhan.</span></div>
        <div class="q" id="q2b"><span class="gold">redha-Nya.</span></div>''')
R("data-start=\"1.7\" data-duration=\"9.9\"","data-start=\"1.7\" data-duration=\"21.1\"")
block("s=s[:a]+'''      tl.fromTo(cam",'''      tl.fromTo(cam, { scale: 1.14 }, { scale: 1.08, duration: 1.23, ease: "power2.out" }, 0);
      const cuts = [[1.23, 1.00, 1.02], [5.11, 1.06, 1.07], [5.59, 1.00, 1.03], [9.42, 1.06, 1.08], [12.67, 1.00, 1.03], [18.70, 1.06, 1.10], [21.05, 1.09, 1.14], [22.77, 1.08, 1.09]];
      cuts.forEach(([t, a, b], i) => {
        const end = i + 1 < cuts.length ? cuts[i + 1][0] : 23.43;
        tl.set(cam, { scale: a }, t);
        tl.to(cam, { scale: b, duration: (t === 9.42 ? 11.9 : end) - t, ease: "none" }, t);
      });
      // punch on "10 orang!"
      tl.to(cam, { scale: 1.14, duration: 0.2, ease: "power3.out" }, 11.9);
      tl.to(cam, { scale: 1.11, duration: 0.55, ease: "power2.inOut" }, 12.1);

''')
block("s=s[:a]+'''      leak(1.28",'''      leak(1.1, -500, 400, 0.45);
      leak(9.55, 500, -400, 0.3);
      leak(18.62, -400, 500, 0.5);
      leak(22.7, 300, -300, 0.4);
      tl.to("#flash", { opacity: 0.35, duration: 0.06 }, 18.66);
      tl.to("#flash", { opacity: 0, duration: 0.4 }, 18.72);
      tl.to("#flash", { opacity: 0.2, duration: 0.05 }, 11.9);
      tl.to("#flash", { opacity: 0, duration: 0.3 }, 11.95);

''')
R(", 1.24);'",", 1.1);'")
R("ease: E }, 1.42);')","ease: E }, 1.25);')")
R('ease: "power2.in" }, 5.4);','ease: "power2.in" }, 18.4);')
R('ease: "power2.inOut" }, 8.6);','ease: "power2.inOut" }, 14.0);')
R('ease: "power2.in" }, 11.25);','ease: "power2.in" }, 22.55);')
block("s=s[:a]+'''      tl.fromTo(\"#barT\"",'''      tl.fromTo("#barT", { yPercent: -100 }, { yPercent: 0, duration: 0.5, ease: "power3.inOut" }, 18.6);
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

''')
R("syukur-sabar/index.html","rezeki-redha/index.html")
open("/home/user/videokewangan/src5/build5.py","w").write(s); print("written")
