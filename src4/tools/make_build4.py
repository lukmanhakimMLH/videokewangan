import re
s=open("/home/user/videokewangan/src3/build3.py").read()
def R(a,b):
    global s
    assert a in s,a[:80]; s=s.replace(a,b)
R('src3/cutwords.json','src4/cutwords.json')
R('END=13.85; DUR=round(END+4.75,2); VID=14.3','END=8.55; DUR=round(END+4.75,2); VID=8.9')
R('''G=[[("Teruskan",4),("perjuangan",5,1),BR,("sampai",6),("ke",7),("destinasi.",8,1)],
   [("Dalam",9),("perjalanan",10,1),BR,("tersebut,",11)],
   [("pasti",12),("ada",13),BR,("onak",14,1),("dan",15),("duri.",16,1)],
   [("Harunginya.",17,1)]]''','''G=[[("Bila",4),("orang",5),("bercakap",6,1),BR,("pasal",7),("kita,",8)],
   [("jangan",9),("berlawan",10,1),BR,("dengan",11),("kata-kata.",12,1)],
   [("sebab",14),("dia",16),("pasti",17),BR,("nak",18),("menang",19,1),("juga.",20)]]''')
R('else 9.30','else 6.84')
a=s.index('AUD=[');b=s.index('aud="\\n"')
s=s[:a]+'''AUD=[("music","pad",0,0.11,DUR),("sfx-hook","impact",0,0.55,4.2),("sfx-wh1","whoosh",1.1,0.38,1.7),("sfx-sig","shimmer",1.95,0.22,4.0),
 ("sfx-t1","tick",2.08,0.2,0.52),("sfx-t2","tick",3.68,0.2,0.52),("sfx-t3","tick",4.32,0.2,0.52),("sfx-t4","tick",6.26,0.22,0.52),
 ("sfx-rise","riser",5.25,0.24,1.6),("sfx-hit","impact",6.84,0.5,4.2),("sfx-drop","subdrop",7.9,0.42,1.5),("sfx-res","shimmer",7.92,0.32,4.0),
 ("sfx-wh3","whoosh_soft",8.4,0.32,1.3),("sfx-end","shimmer",8.85,0.34,4.0)]
'''+s[b:]
R('<span class="l1" id="h1">Kata-kata hari ini 🔥</span>','<span class="l1" id="h1">Kata-kata hari ini 🗣️</span>')
R('<span class="l2 gold" id="h2">Teruskan Berjuang</span>','<span class="l2 gold" id="h2">Lawan Dengan Result</span>')
R('<span class="l3" id="h3">💪 🏁 ✨</span>','<span class="l3" id="h3">🤫 📈 🏆</span>')
R('font-weight: 800; font-size: 96px;','font-weight: 800; font-size: 88px;')
R('data-start="1.3" data-duration="8.0"','data-start="1.25" data-duration="5.5"')
R('data-start="9.22" data-duration="4.7"','data-start="6.76" data-duration="1.84"')
R('''<div id="quote" class="clip" data-start="9.3" data-duration="4.6" data-track-index="5" data-track-kind="graphics"><div id="quoteInner">
        <div class="q" id="q0"><span class="gold">SEBAB APA?</span></div>
        <div class="q" id="q1">bila sampai satu titik,</div>
        <div class="q" id="q3">anda akan rasa</div>
        <div class="q" id="q2"><span class="gold">kemanisannya.</span></div>''','''<div id="quote" class="clip" data-start="6.82" data-duration="1.78" data-track-index="5" data-track-kind="graphics"><div id="quoteInner">
        <div class="q" id="q0"><span class="gold">TAPI</span></div>
        <div class="q" id="q1">lawan dengan</div>
        <div class="q" id="q2"><span class="gold">result.</span></div>''')
R('#q1 { top: 262px;','#q1 { top: 250px;')
R('#q2 { top: 418px; font-family: "Playfair Display"; font-style: italic; font-weight: 800; font-size: 112px;','#q2 { top: 340px; font-family: "Playfair Display"; font-style: italic; font-weight: 800; font-size: 132px;')
R('#q0 { top: 200px;','#q0 { top: 192px;')
R('data-start="1.7" data-duration="12.2"','data-start="1.7" data-duration="6.9"')
R('#cam { position: absolute; inset: 0; overflow: hidden; transform-origin: 50% 56%; }','#cam { position: absolute; inset: 0; overflow: hidden; transform-origin: 50% 30%; }') if '#cam {' in s else None
a=s.index("s=s[:a]+'''      tl.fromTo(cam")+len("s=s[:a]+'''");b=s.index("'''+s[b:]",a)
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
a=s.index("s=s[:a]+'''      leak(1.2")+len("s=s[:a]+'''");b=s.index("'''+s[b:]",a)
s=s[:a]+'''      leak(1.15, -500, 400, 0.45);
      leak(3.34, 500, -400, 0.3);
      leak(6.78, -400, 500, 0.5);
      leak(8.45, 300, -300, 0.4);
      tl.to("#flash", { opacity: 0.35, duration: 0.06 }, 6.84);
      tl.to("#flash", { opacity: 0, duration: 0.4 }, 6.9);
      tl.to("#flash", { opacity: 0.25, duration: 0.05 }, 7.94);
      tl.to("#flash", { opacity: 0, duration: 0.35 }, 7.99);

'''+s[b:]
R(', 1.16);',', 1.1);')
R('ease: E }, 1.35);','ease: E }, 1.28);')
R('ease: "power2.in" }, 9.08);','ease: "power2.in" }, 6.55);')
R('ease: "power2.inOut" }, 6.6);','ease: "power2.inOut" }, 5.2);')
R('ease: "power2.in" }, 13.6);','ease: "power2.in" }, 8.3);')
a=s.index("s=s[:a]+'''      tl.fromTo(\"#barT\"")+len("s=s[:a]+'''");b=s.index("'''+s[b:]",a)
s=s[:a]+'''      tl.fromTo("#barT", { yPercent: -100 }, { yPercent: 0, duration: 0.4, ease: "power3.inOut" }, 6.76);
      tl.fromTo("#barB", { yPercent: 100 }, { yPercent: 0, duration: 0.4, ease: "power3.inOut" }, 6.76);
      tl.to("#dim", { opacity: 0.34, duration: 0.5, ease: "power2.out" }, 6.76);
      tl.fromTo("#q0", { opacity: 0, scale: 1.2 }, { opacity: 1, scale: 1, duration: 0.45, ease: E }, 6.86);
      tl.fromTo("#q1", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.4, ease: E }, 7.16);
      tl.fromTo("#q2", { opacity: 0, y: 40, scale: 1.35 }, { opacity: 1, y: 0, scale: 1, duration: 0.6, ease: "back.out(1.8)" }, 7.92);
      tl.to("#quoteInner", { opacity: 0, duration: 0.15, ease: "power2.in" }, 8.42);

'''+s[b:]
R("teruskan-berjuang/index.html","lawan-result/index.html")
k=s.index("rep('<span class=\"l1\"")
s=s[:k]+"rep('overflow: hidden; transform-origin: 50% 56%; }','overflow: hidden; transform-origin: 50% 30%; }')\nrep('.cap { position: absolute; left: 0; right: 0; top: 290px;','.cap { position: absolute; left: 0; right: 0; top: 262px;')\n"+s[k:]
open("/home/user/videokewangan/src4/build4.py","w").write(s); print("written")
