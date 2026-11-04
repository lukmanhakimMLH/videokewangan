s=open("/home/user/videokewangan/src2/build2.py").read()
def R(a,b):
    global s
    assert a in s,a[:70]; s=s.replace(a,b)
R('src2/cutwords.json','src3/cutwords.json')
R('END=11.5; DUR=round(END+4.75,2); VID=12.03','END=13.85; DUR=round(END+4.75,2); VID=14.3')
R('''G=[[("Bersyukurlah",4,1),("dengan",5),BR,("apa",6),("yang",7),("ada,",8)],
   [("dan",9),("bersabarlah",10,1)],
   [("dengan",11),("apa",12),("yang",13),BR,("belum",14,1),("ada.",15)]]''','''G=[[("Teruskan",4),("perjuangan",5,1),BR,("sampai",6),("ke",7),("destinasi.",8,1)],
   [("Dalam",9),("perjalanan",10,1),BR,("tersebut,",11)],
   [("pasti",12),("ada",13),BR,("onak",14,1),("dan",15),("duri.",16,1)],
   [("Harunginya.",17,1)]]''')
R('else 5.66','else 9.30')
a=s.index('AUD=[');b=s.index('aud="\\n"')
s=s[:a]+'''AUD=[("music","pad",0,0.11,DUR),("sfx-hook","impact",0,0.55,4.2),("sfx-wh1","whoosh",1.15,0.38,1.7),("sfx-sig","shimmer",1.95,0.22,4.0),
 ("sfx-t1","tick",1.96,0.2,0.52),("sfx-t2","tick",3.66,0.2,0.52),("sfx-wh2","whoosh_soft",4.36,0.28,1.3),("sfx-t3","tick",5.0,0.2,0.52),
 ("sfx-t4","tick",7.46,0.22,0.52),("sfx-t5","tick",8.12,0.22,0.52),("sfx-rise","riser",7.1,0.24,1.6),("sfx-drop","subdrop",8.62,0.45,1.5),
 ("sfx-hit","impact",9.3,0.5,4.2),("sfx-manis","shimmer",12.68,0.32,4.0),("sfx-wh3","whoosh_soft",13.65,0.32,1.3),("sfx-end","shimmer",14.15,0.34,4.0)]
'''+s[b:]
R('<span class="l1" id="h1">Kata-kata hari ini 🤲</span>','<span class="l1" id="h1">Kata-kata hari ini 🔥</span>')
R('<span class="l2 gold" id="h2">Syukur &amp; Sabar</span>','<span class="l2 gold" id="h2">Teruskan Berjuang</span>')
R('<span class="l3" id="h3">✨ 🤍 ✨</span>','<span class="l3" id="h3">💪 🏁 ✨</span>')
R('font-weight: 800; font-size: 118px;','font-weight: 800; font-size: 96px;')
R('''<div id="badge" class="clip" data-start="1.4" data-duration="4.3"''','''<div id="badge" class="clip" data-start="1.3" data-duration="8.0"''')
R('''<div id="bars" class="clip" data-start="5.55" data-duration="6.1"''','''<div id="bars" class="clip" data-start="9.22" data-duration="4.7"''')
R('''<div id="quote" class="clip" data-start="5.62" data-duration="5.95" data-track-index="5" data-track-kind="graphics"><div id="quoteInner">
        <div class="q" id="q0"><span class="gold">JANJI DIA PASTI</span></div>
        <div class="q" id="q1">tidak akan</div>
        <div class="q" id="q1b">dan</div>
        <div class="q" id="q2"><span class="gold">melambatkan</span></div>
        <div class="q" id="q2b"><span class="gold">mempercepatkan</span></div>
        <div class="q" id="q3">walaupun satu saat.</div>
      </div></div>''','''<div id="quote" class="clip" data-start="9.3" data-duration="4.6" data-track-index="5" data-track-kind="graphics"><div id="quoteInner">
        <div class="q" id="q0"><span class="gold">SEBAB APA?</span></div>
        <div class="q" id="q1">bila sampai satu titik,</div>
        <div class="q" id="q3">anda akan rasa</div>
        <div class="q" id="q2"><span class="gold">kemanisannya.</span></div>
      </div></div>''')
R('''      #q1, #q1b { top: 262px;''','''      #q1 { top: 262px;''')
R('''      #q2, #q2b { top: 340px;''','''      #q2 { top: 418px;''')
R('''      #q3 { top: 484px;''','''      #q3 { top: 350px;''')
R('''      #q2 .gold, #q2b .gold {''','''      #q2 .gold {''')
R('data-start="1.7" data-duration="9.9"','data-start="1.7" data-duration="12.2"')
R('''      const cuts = [[1.42, 1.00, 1.02], [3.54, 1.06, 1.08], [5.66, 1.10, 1.13], [6.84, 1.05, 1.07], [11.44, 1.08, 1.09]];''','''      const cuts = [[1.35, 1.00, 1.02], [2.77, 1.06, 1.08], [4.46, 1.00, 1.03], [8.53, 1.08, 1.10], [9.33, 1.05, 1.13], [13.71, 1.08, 1.09]];''')
R('cuts[i + 1][0] : 12.03;','cuts[i + 1][0] : 14.3;')
R('(t === 6.84 ? 7.5 : end)','(t === 8.53 ? 8.66 : (t === 9.33 ? 12.7 : end))')
R('''      tl.to(cam, { scale: 1.12, duration: 0.22, ease: "power3.out" }, 7.5);
      tl.to(cam, { scale: 1.08, duration: 1.4, ease: "power2.inOut" }, 7.72);
      tl.to(cam, { scale: 1.15, duration: 0.22, ease: "power3.out" }, 9.38);
      tl.to(cam, { scale: 1.12, duration: 1.8, ease: "power2.inOut" }, 9.6);''','''      tl.to(cam, { scale: 1.15, duration: 0.22, ease: "power3.out" }, 8.66);
      tl.to(cam, { scale: 1.12, duration: 0.45, ease: "power2.inOut" }, 8.88);
      tl.to(cam, { scale: 1.18, duration: 0.25, ease: "power3.out" }, 12.7);
      tl.to(cam, { scale: 1.16, duration: 0.7, ease: "power2.inOut" }, 12.95);''')
R('''      leak(1.28, -500, 400, 0.45);
      leak(5.58, -400, 500, 0.5);
      leak(9.1, 500, -400, 0.3);
      leak(11.4, 300, -300, 0.4);
      tl.to("#flash", { opacity: 0.35, duration: 0.06 }, 5.64);
      tl.to("#flash", { opacity: 0, duration: 0.4 }, 5.70);''','''      leak(1.2, -500, 400, 0.45);
      leak(4.4, 500, -400, 0.3);
      leak(9.25, -400, 500, 0.5);
      leak(13.75, 300, -300, 0.4);
      tl.to("#flash", { opacity: 0.35, duration: 0.06 }, 9.3);
      tl.to("#flash", { opacity: 0, duration: 0.4 }, 9.36);''')
R(', 1.24);',', 1.16);')
R('{ opacity: 1, scale: 1, duration: 0.7, ease: E }, 1.42);','{ opacity: 1, scale: 1, duration: 0.7, ease: E }, 1.35);')
R('ease: "power2.in" }, 5.4);','ease: "power2.in" }, 9.08);')
R('ease: "power2.inOut" }, 8.6);','ease: "power2.inOut" }, 6.6);')
R('ease: "power2.in" }, 11.25);','ease: "power2.in" }, 13.6);')
a=s.index("s=s[:a]+'''      tl.fromTo(\"#barT\"")+len("s=s[:a]+'''")
b=s.index("'''+s[b:]",a)
s=s[:a]+'''      tl.fromTo("#barT", { yPercent: -100 }, { yPercent: 0, duration: 0.5, ease: "power3.inOut" }, 9.22);
      tl.fromTo("#barB", { yPercent: 100 }, { yPercent: 0, duration: 0.5, ease: "power3.inOut" }, 9.22);
      tl.to("#dim", { opacity: 0.32, duration: 0.6, ease: "power2.out" }, 9.22);
      tl.fromTo("#q0", { opacity: 0, scale: 1.15 }, { opacity: 1, scale: 1, duration: 0.6, ease: E }, 9.38);
      tl.fromTo("#q1", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.5, ease: E }, 9.96);
      tl.fromTo("#q3", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.5, ease: E }, 11.76);
      tl.fromTo("#q2", { opacity: 0, y: 40, scale: 0.88 }, { opacity: 1, y: 0, scale: 1, duration: 0.8, ease: "expo.out" }, 12.68);
      tl.to("#quoteInner", { opacity: 0, duration: 0.2, ease: "power2.in" }, 13.68);

'''+s[b:]
R("syukur-sabar/index.html","teruskan-berjuang/index.html")
open("/home/user/videokewangan/src3/build3.py","w").write(s)
print("written")
