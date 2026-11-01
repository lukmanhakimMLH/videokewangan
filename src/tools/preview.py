import re,subprocess,json,sys
R="/home/user/videokewangan"
html=open(f"{R}/kata-kata/index.html").read()
aud=re.findall(r'<audio id="([^"]+)" src="([^"]+)" data-start="([\d.]+)" data-duration="([\d.]+)" data-volume="([\d.]+)"',html)
# mix: a-roll audio + sfx, padded video to 23s
inp=["-i",f"{R}/kata-kata/assets/graded.mp4"];fl=[];lab=["[0:a]"]
for k,(i,src,st,d,v) in enumerate(aud):
    inp+=["-i",f"{R}/kata-kata/{src}"];ms=int(float(st)*1000)
    fade=",afade=t=out:st=21.5:d=1.5" if i=="music" else ""
    fl.append(f"[{k+1}:a]atrim=0:{d},volume={v}{fade},adelay={ms}|{ms}[s{k}]");lab.append(f"[s{k}]")
fl.append(f"{''.join(lab)}amix=inputs={len(lab)}:normalize=0:duration=longest,atrim=0:23,alimiter=limit=0.95[a]")
fl.append("[0:v]scale=720:1280,fps=30,tpad=stop_mode=add:stop_duration=3:color=black[v]")
subprocess.run(["ffmpeg","-v","error","-y",*inp,"-filter_complex",";".join(fl),"-map","[v]","-map","[a]","-t","23","-c:v","libx264","-crf","25","-preset","medium","-threads","3","-c:a","aac","-b:a","160k","-movflags","+faststart",f"{R}/preview/preview.mp4"],check=True)
# page
h=re.sub(r'\s*<audio [^>]*></audio>','',html)
h=h.replace('src="assets/graded.mp4"','src="preview.mp4"').replace('data-has-audio="true"','')
h=h.replace('<html lang="ms" data-resolution="portrait">','<html lang="ms">')
h=h.replace('<title>','')
h=h.replace('<meta name="viewport" content="width=1080, height=1920" />','''<meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Kata-kata Hari Ini</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@500;600&family=Montserrat:wght@500;600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,600;1,700;1,800&display=swap" rel="stylesheet">''')
css=open(f"{R}/src/tools/preview.css").read();js=open(f"{R}/src/tools/preview.js").read()
h=h.replace("html, body { margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #000; }",css)
h=h.replace('<div id="root"','<div id="app"><div id="stagewrap"><div id="stage"><div id="root"',1)
h=re.sub(r'(<div id="flash"></div>)\s*<!-- MUSIC \+ SFX -->\s*</div>',r'''\1
    </div></div>
      <button id="play" aria-label="Main">▶</button>
    </div>
    <div id="bar"><button id="pp" aria-label="Main/Jeda">▶</button><input id="seek" type="range" min="0" max="23" step="0.01" value="0"><span id="tc">0.0 / 23.0</span></div>
    </div>''',h)
h=h.replace("    </script>\n  </body>","    </script>\n    <script>\n"+js+"\n    </script>\n  </body>")
open(f"{R}/preview/index.html","w").write(h)
print("ok",len(aud))
# artifact page contract: no document skeleton of our own
h=open(f"{R}/preview/index.html").read()
for pat in [r'<!doctype html>\s*',r'<html[^>]*>\s*',r'</html>\s*',r'<head>\s*',r'</head>\s*',r'<body>\s*',r'</body>\s*',r'<meta charset="UTF-8" />\s*',r'<meta name="viewport"[^>]*>\s*']:
    h=re.sub(pat,'',h,flags=re.I)
t=re.search(r'<title>.*?</title>\s*',h).group(0);h=t+h.replace(t,'',1)
h=h.replace(":root { color-scheme: dark;",":root { color-scheme: dark;",1)
open(f"{R}/preview/index.html","w").write(h)
