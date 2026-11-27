"""Bina versi web (Firebase) ke ../docs untuk GitHub Pages.
Sumber: index.html + apa.js (sama dengan versi Claude) + web/fb.js. Jalankan: python3 build_web.py"""
import pathlib, shutil
here = pathlib.Path(__file__).parent
out = here.parent / 'docs'
out.mkdir(exist_ok=True)
html = (here / 'index.html').read_text()
head = """<script>window.__HOSTED=true;window.__REKRUT_COL='rekrut';window.__fbReady=new Promise(r=>window.__fbResolve=r);window.claude={use:async n=>(await window.__fbReady).use(n)};</script>
<script type="module" src="fb.js"></script>
<link rel="manifest" href="manifest.json">
<link rel="icon" href="icon-192.png">
<link rel="apple-touch-icon" href="icon-192.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="QAIZER">
"""
assert '<meta name="theme-color"' in html
html = html.replace('<meta name="theme-color"', head + '<meta name="theme-color"', 1)
(out / 'index.html').write_text(html)
shutil.copy(here / 'apa.js', out / 'apa.js')
shutil.copy(here / 'mapa.js', out / 'mapa.js')
shutil.copy(here / 'pasukan.js', out / 'pasukan.js')
shutil.copy(here / 'klien.js', out / 'klien.js')
shutil.copy(here / 'web' / 'fb.js', out / 'fb.js')
for f in ['manifest.json', 'icon-192.png', 'icon-512.png']:
    shutil.copy(here / 'web' / f, out / f)
(out / '.nojekyll').write_text('')
print('OK ->', out)
