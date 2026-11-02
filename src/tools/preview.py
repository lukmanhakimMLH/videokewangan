import re,subprocess,json,sys
R="/home/user/videokewangan"
PROJ=sys.argv[1] if len(sys.argv)>1 else "kata-kata"; OUT=sys.argv[2] if len(sys.argv)>2 else "preview"; TITLE=sys.argv[3] if len(sys.argv)>3 else "Kata-kata Hari Ini"
import os; os.makedirs(f"{R}/{OUT}",exist_ok=True)
html=open(f"{R}/{PROJ}/index.html").read()
DUR=float(re.search(r'data-composition-id="main" data-start="0" data-duration="([\d.]+)"',html).group(1))
VD=float(re.search(r'id="a-roll"[^>]*data-duration="([\d.]+)"',html,re.S).group(1))
aud=re.findall(r'<audio id="([^"]+)" src="([^"]+)" data-start="([\d.]+)" data-duration="([\d.]+)" data-volume="([\d.]+)"',html)
# mix: a-roll audio + sfx, padded video to 23s
inp=["-i",f"{R}/{PROJ}/assets/graded.mp4"];fl=[];lab=["[0:a]"]
for k,(i,src,st,d,v) in enumerate(aud):
    inp+=["-i",f"{R}/{PROJ}/{src}"];ms=int(float(st)*1000)
    fade=f",afade=t=out:st={DUR-1.5}:d=1.5" if i=="music" else ""
    fl.append(f"[{k+1}:a]atrim=0:{d},volume={v}{fade},adelay={ms}|{ms}[s{k}]");lab.append(f"[s{k}]")
fl.append(f"{''.join(lab)}amix=inputs={len(lab)}:normalize=0:duration=longest,atrim=0:{DUR},alimiter=limit=0.95[a]")
fl.append(f"[0:v]scale=720:1280,fps=30,tpad=stop_mode=add:stop_duration={DUR-VD+0.5}:color=black[v]")
subprocess.run(["ffmpeg","-v","error","-y",*inp,"-filter_complex",";".join(fl),"-map","[v]","-map","[a]","-t",str(DUR),"-c:v","libx264","-crf","25","-preset","medium","-threads","3","-c:a","aac","-b:a","160k","-movflags","+faststart",f"{R}/{OUT}/preview.mp4"],check=True)
# page
h=re.sub(r'\s*<audio [^>]*></audio>','',html)
h=h.replace('src="assets/graded.mp4"','src="preview.mp4"').replace('data-has-audio="true"','')
h=h.replace('<html lang="ms" data-resolution="portrait">','<html lang="ms">')
h=h.replace('<title>','')
h=h.replace('<meta name="viewport" content="width=1080, height=1920" />','''<meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>'''+TITLE+'''</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@500;600&family=Montserrat:wght@500;600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,600;1,700;1,800&display=swap" rel="stylesheet">''')
css=open(f"{R}/src/tools/preview.css").read();js=open(f"{R}/src/tools/preview.js").read().replace("__DUR__",str(DUR))
h=h.replace("html, body { margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #000; }",css)
h=h.replace('<div id="root"','<div id="app"><div id="stagewrap"><div id="stage"><div id="root"',1)
h=re.sub(r'(<div id="flash"></div>)\s*<!-- MUSIC \+ SFX -->\s*</div>',r'''\1
    </div></div>
      <button id="play" aria-label="Main">▶</button>
    </div>
    <div id="bar"><button id="pp" aria-label="Main/Jeda">▶</button><input id="seek" type="range" min="0" max="'''+str(DUR)+'''" step="0.01" value="0"><span id="tc">0.0</span></div>
    </div>''',h)
h=h.replace("    </script>\n  </body>","    </script>\n    <script>\n"+js+"\n    </script>\n  </body>")
open(f"{R}/{OUT}/index.html","w").write(h)
print("ok",len(aud))
# artifact page contract: no document skeleton of our own
h=open(f"{R}/{OUT}/index.html").read()
for pat in [r'<!doctype html>\s*',r'<html[^>]*>\s*',r'</html>\s*',r'<head>\s*',r'</head>\s*',r'<body>\s*',r'</body>\s*',r'<meta charset="UTF-8" />\s*',r'<meta name="viewport"[^>]*>\s*']:
    h=re.sub(pat,'',h,flags=re.I)
t=re.search(r'<title>.*?</title>\s*',h).group(0);h=t+h.replace(t,'',1)
h=h.replace(":root { color-scheme: dark;",":root { color-scheme: dark;",1)
open(f"{R}/{OUT}/index.html","w").write(h)
