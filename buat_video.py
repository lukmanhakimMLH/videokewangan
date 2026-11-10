#!/usr/bin/env python3
"""
buat_video.py — Enjin video jualan gaya TikTok affiliate (9:16).

Guna:
    python3 buat_video.py projek/contoh            # baca projek/contoh/skrip.json
    python3 buat_video.py projek/contoh --pratonton # render 480p laju untuk semak

Apa enjin ni buat:
  1. Tukar setiap babak skrip jadi suara AI Bahasa Melayu (edge-tts) + masa setiap perkataan
  2. Lukis video 1080x1920: latar gelap, produk terapung + zoom, gambar kau, infografik
     (angka, senarai, harga, CTA beg kuning) & caption SATU PERKATAAN macam video rujukan
  3. Campur suara + muzik beat + bunyi "whoosh" setiap tukar babak
  4. Keluarkan  <projek>/keluaran/video.mp4,  skrip_teleprompter.txt,  caption_tiktok.txt
"""
import argparse, asyncio, hashlib, json, math, os, re, ssl, subprocess, sys, wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

AKAR = Path(__file__).resolve().parent
FON_HITAM = str(AKAR / "aset/font/Montserrat-900.ttf")
FON_TEBAL = str(AKAR / "aset/font/Montserrat-700.ttf")
SR = 44100

KUNING = (255, 214, 10)
MERAH = (255, 59, 48)
HIJAU = (52, 230, 120)
PUTIH = (255, 255, 255)


# ───────────────────────── util ─────────────────────────
def lerp(a, b, t): return a + (b - a) * t
def kepit(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(t): t = kepit(t); return 1 - (1 - t) ** 3
def ease_back(t):
    t = kepit(t); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

_fon_cache = {}
def fon(saiz, berat=FON_HITAM):
    k = (saiz, berat)
    if k not in _fon_cache: _fon_cache[k] = ImageFont.truetype(berat, saiz)
    return _fon_cache[k]

def teks_img(teks, saiz, warna=PUTIH, stroke=0, stroke_warna=(0, 0, 0), berat=FON_HITAM, bayang=True):
    """Render teks jadi RGBA (siap stroke + bayang lembut)."""
    f = fon(saiz, berat)
    x0, y0, x1, y1 = f.getbbox(teks, stroke_width=stroke)
    pad = stroke + 30
    w, h = x1 - x0 + pad * 2, y1 - y0 + pad * 2
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if bayang:
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((pad - x0 + 4, pad - y0 + 8), teks, font=f, fill=(0, 0, 0, 170),
                                stroke_width=stroke, stroke_fill=(0, 0, 0, 170))
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(10)))
    ImageDraw.Draw(img).text((pad - x0, pad - y0), teks, font=f, fill=warna,
                             stroke_width=stroke, stroke_fill=stroke_warna)
    return img

def tampal(dasar, img, cx, cy, skala=1.0, alpha=1.0, putar=0.0):
    """Tampal RGBA di tengah (cx,cy) dengan skala/alpha/putaran."""
    if img is None or skala <= 0.01 or alpha <= 0.01: return
    if abs(skala - 1) > 0.001:
        img = img.resize((max(1, int(img.width * skala)), max(1, int(img.height * skala))), Image.BILINEAR)
    if abs(putar) > 0.05:
        img = img.rotate(putar, resample=Image.BICUBIC, expand=True)
    if alpha < 0.999:
        a = img.getchannel("A").point(lambda v: int(v * alpha)); img = img.copy(); img.putalpha(a)
    dasar.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))

def isi_bingkai(img, w, h):
    return ImageOps.fit(img, (w, h), Image.LANCZOS, centering=(0.5, 0.45))

def bucu_bulat(img, r):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, img.width - 1, img.height - 1), r, fill=255)
    out = img.convert("RGBA"); out.putalpha(m); return out

def pil(teks, saiz, latar, warna=(0, 0, 0), padx=40, pady=22, r=None, glow=None):
    """Label bentuk pil (rounded)."""
    f = fon(saiz)
    x0, y0, x1, y1 = f.getbbox(teks)
    w, h = x1 - x0 + padx * 2, y1 - y0 + pady * 2
    g = 40 if glow else 0
    img = Image.new("RGBA", (w + g * 2, h + g * 2), (0, 0, 0, 0))
    if glow:
        gl = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(gl).rounded_rectangle((g, g, g + w, g + h), r or h // 2, fill=glow + (200,))
        img = Image.alpha_composite(img, gl.filter(ImageFilter.GaussianBlur(22)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((g, g, g + w, g + h), r or h // 2, fill=latar)
    d.text((g + padx - x0, g + pady - y0), teks, font=f, fill=warna)
    return img


# ───────────────────────── suara (TTS) ─────────────────────────
def _ssl_ctx():
    ca = os.environ.get("SSL_CERT_FILE") or ("/root/.ccr/ca-bundle.crt" if Path("/root/.ccr/ca-bundle.crt").exists() else None)
    return ssl.create_default_context(cafile=ca) if ca else None

async def _tts(teks, suara, laju, pic, mp3):
    import edge_tts
    import edge_tts.communicate as cm
    ctx = _ssl_ctx()
    if ctx: cm._SSL_CTX = ctx
    c = edge_tts.Communicate(teks, suara, rate=laju, pitch=pic, boundary="WordBoundary")
    kata = []
    with open(mp3, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                kata.append({"t": ch["offset"] / 1e7, "d": ch["duration"] / 1e7, "w": ch["text"]})
    return kata

def baca_audio(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()

def suara_babak(teks, cfg, cache):
    k = hashlib.md5(f"{teks}|{cfg['suara']}|{cfg['laju']}|{cfg['pic']}".encode()).hexdigest()[:12]
    mp3, js = cache / f"{k}.mp3", cache / f"{k}.json"
    if not (mp3.exists() and js.exists()):
        kata = asyncio.run(_tts(teks, cfg["suara"], cfg["laju"], cfg["pic"], mp3))
        js.write_text(json.dumps(kata, ensure_ascii=False))
    return baca_audio(mp3), json.loads(js.read_text())


# ───────────────────────── muzik & SFX (dijana sendiri) ─────────────────────────
def jana_beat(saat, bpm=102):
    n = int(saat * SR); out = np.zeros(n, np.float32)
    beat = 60 / bpm; rng = np.random.default_rng(7)
    tk = np.arange(int(0.35 * SR)) / SR
    kick = np.sin(2 * np.pi * (45 * tk + 90 * (1 - np.exp(-tk * 30)) / 30)) * np.exp(-tk * 9)
    th = np.arange(int(0.05 * SR)) / SR
    hat = rng.standard_normal(len(th)) * np.exp(-th * 90); hat = np.diff(hat, prepend=0) * 0.5
    ts = np.arange(int(0.18 * SR)) / SR
    snap = rng.standard_normal(len(ts)) * np.exp(-ts * 28) * 0.5
    # akord pad lembut (Am - F - C - G)
    akord = [[220, 261.6, 329.6], [174.6, 220, 261.6], [261.6, 329.6, 392], [196, 246.9, 293.7]]
    bar = beat * 4; t = np.arange(n) / SR
    pad = np.zeros(n, np.float32)
    for i in range(int(saat / bar) + 1):
        a, b = int(i * bar * SR), min(n, int((i + 1) * bar * SR))
        if a >= n: break
        tt = t[a:b] - i * bar
        env = np.minimum(1, tt / 0.4) * np.minimum(1, (bar - tt) / 0.4)
        for fq in akord[i % 4]:
            pad[a:b] += (np.sin(2 * np.pi * fq * tt) + 0.3 * np.sin(2 * np.pi * fq * 2 * tt)) * env * 0.06
        bass = akord[i % 4][0] / 2
        pad[a:b] += np.sin(2 * np.pi * bass * tt) * env * 0.12
    def letak(sampel, saat_mula, vol):
        a = int(saat_mula * SR); b = min(n, a + len(sampel))
        if a < n: out[a:b] += sampel[: b - a] * vol
    k = 0
    while k * beat < saat:
        letak(kick, k * beat, 0.9)
        if k % 2 == 1: letak(snap, k * beat, 0.35)
        letak(hat, k * beat + beat / 2, 0.25)
        k += 1
    return out + pad

def whoosh():
    d = 0.45; t = np.arange(int(d * SR)) / SR
    n = np.random.default_rng(3).standard_normal(len(t))
    k = 30; n = np.convolve(n, np.ones(k) / k, "same") * 4
    env = np.sin(np.pi * np.minimum(1, t / d)) ** 2
    return (n * env * 0.5).astype(np.float32)

def pop():
    t = np.arange(int(0.12 * SR)) / SR
    return (np.sin(2 * np.pi * (900 - 2500 * t) * t) * np.exp(-t * 35) * 0.5).astype(np.float32)


# ───────────────────────── visual ─────────────────────────
class Aset:
    def __init__(self, cfg, folder, W, H):
        self.W, self.H = W, H
        self.produk = []
        for p in cfg["gambar_produk"]:
            spec = p if isinstance(p, dict) else {"fail": p}
            img = Image.open(folder / spec["fail"]).convert("RGB")
            if "potong" in spec:  # [x0,y0,x1,y1] pecahan 0..1
                x0, y0, x1, y1 = spec["potong"]
                img = img.crop((int(x0 * img.width), int(y0 * img.height), int(x1 * img.width), int(y1 * img.height)))
            self.produk.append(img)
        self.aku = Image.open(folder / cfg["gambar_aku"]).convert("RGB") if cfg.get("gambar_aku") else None
        if self.aku: self.aku = ImageOps.exif_transpose(self.aku)
        # latar gelap: produk kabur + vignette (macam suasana kereta malam)
        s = 1.15
        bw, bh = int(W * s), int(H * s)
        bg = isi_bingkai(self.produk[0], bw, bh).filter(ImageFilter.GaussianBlur(int(45 * W / 1080)))
        bg = Image.blend(bg, Image.new("RGB", bg.size, (8, 8, 12)), 0.72)
        vig = Image.new("L", (bw, bh), 0)
        ImageDraw.Draw(vig).ellipse((-bw * 0.3, -bh * 0.15, bw * 1.3, bh * 1.15), fill=255)
        vig = vig.filter(ImageFilter.GaussianBlur(int(180 * W / 1080)))
        self.latar = Image.composite(bg, Image.new("RGB", bg.size, (0, 0, 0)), vig).convert("RGBA")
        self._kad = {}
        self._aku_cache = None

    def kad(self, i, lebar, maxh_pecahan=0.42):
        """Gambar produk jadi 'kad' bucu bulat + bingkai + bayang."""
        k = (i, lebar, maxh_pecahan)
        if k not in self._kad:
            img = self.produk[i]
            h = int(img.height * lebar / img.width)
            maxh = int(self.H * maxh_pecahan)
            if h > maxh: lebar, h = int(lebar * maxh / h), maxh
            u = int(14 * self.W / 1080)
            im = bucu_bulat(img.resize((lebar, h), Image.LANCZOS), int(36 * self.W / 1080))
            g = int(70 * self.W / 1080)
            kad = Image.new("RGBA", (lebar + g * 2, h + g * 2), (0, 0, 0, 0))
            d = ImageDraw.Draw(kad)
            d.rounded_rectangle((g - u, g - u + 30, g + lebar + u, g + h + u + 30), 46, fill=(0, 0, 0, 220))
            kad = kad.filter(ImageFilter.GaussianBlur(g // 2))
            ImageDraw.Draw(kad).rounded_rectangle((g - u, g - u, g + lebar + u, g + h + u), int(46 * self.W / 1080),
                                                  fill=(255, 255, 255, 235))
            kad.alpha_composite(im, (g, g))
            self._kad[k] = kad
        return self._kad[k]


def lukis_latar(a, t):
    W, H = a.W, a.H
    dx = (a.latar.width - W) / 2 * (1 + math.sin(t * 0.25))
    dy = (a.latar.height - H) / 2 * (1 + math.cos(t * 0.2))
    return a.latar.crop((int(dx), int(dy), int(dx) + W, int(dy) + H))


def lukis_cahaya(fr, t, W, H):
    """Garis cahaya bergerak — bagi rasa 'mahal'."""
    lap = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lap)
    for i in range(3):
        x = ((t * 140 * (1 + i * 0.4) + i * 420) % (W + 900)) - 450
        d.line((x, 0, x + 500, H), fill=(255, 255, 255, 18), width=int(60 * W / 1080) + i * 30)
    fr.alpha_composite(lap.filter(ImageFilter.GaussianBlur(25)))


def lukis_visual(fr, a, b, lt, dur):
    W, H = a.W, a.H; u = W / 1080
    jenis = b.get("visual", "produk"); gi = b.get("gambar", 0)
    p = lt / max(dur, 0.01)
    if jenis in ("aku", "aku+produk") and a.aku is not None:
        z = lerp(1.0, 1.12, p) * (1 + 0.06 * (1 - ease_out(lt / 0.35)))
        bw, bh = int(W * z), int(H * z)
        if a._aku_cache is None: a._aku_cache = isi_bingkai(a.aku, int(W * 1.2), int(H * 1.2))
        im = a._aku_cache.resize((bw, bh), Image.BILINEAR)
        ox, oy = (bw - W) // 2, int((bh - H) * 0.35)
        fr.paste(im.crop((ox, oy, ox + W, oy + H)), (0, 0))
        grad = Image.linear_gradient("L").resize((W, H)).point(lambda v: int(max(0, v - 90) * 1.4))
        fr.alpha_composite(Image.merge("RGBA", (*[Image.new("L", (W, H), 0)] * 3, grad)))
        if jenis == "aku+produk":
            masuk = ease_back(kepit((lt - 0.15) / 0.45))
            k = a.kad(gi, int(420 * u), 0.26)
            tampal(fr, k, W * 0.7, H * 0.42 + math.sin(lt * 2.4) * 14 * u, skala=masuk, putar=-6 + math.sin(lt * 1.3) * 2)
        return
    fr.alpha_composite(lukis_latar(a, lt + hash(str(b.get("teks"))) % 10))
    lukis_cahaya(fr, lt, W, H)
    if jenis == "zoom":  # zoom ke bahagian produk (fokus = [x,y] pecahan)
        fx, fy = b.get("fokus", [0.5, 0.5])
        img = a.produk[gi]
        z = lerp(1.25, 1.7, ease_out(p))
        lw = int((760 if b.get("overlay") else 900) * u); lh = int(lw * (0.75 if b.get("overlay") else 1.1))
        cw, ch = img.width / z, img.width / z * lh / lw
        cx = kepit(fx * img.width, cw / 2, img.width - cw / 2); cy = kepit(fy * img.height, ch / 2, img.height - ch / 2)
        crop = img.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((lw, lh), Image.BILINEAR)
        crop = bucu_bulat(crop, int(40 * u))
        g = Image.new("RGBA", (lw + 24, lh + 24), (0, 0, 0, 0))
        ImageDraw.Draw(g).rounded_rectangle((0, 0, lw + 23, lh + 23), int(48 * u), fill=(255, 255, 255, 235))
        g.alpha_composite(crop, (12, 12))
        tampal(fr, g, W / 2, H * (0.47 if b.get("overlay") else 0.40), skala=lerp(0.9, 1, ease_back(lt / 0.4)))
        return
    # produk terapung (default)
    ada_ov = bool(b.get("overlay"))
    lebar = int((b.get("saiz", 0.72 if ada_ov else 0.8)) * W)
    k = a.kad(gi, lebar, 0.30 if ada_ov else 0.42)
    masuk = ease_back(kepit(lt / 0.42))
    hembus = 1 + 0.025 * math.sin(lt * 1.8) + 0.04 * p
    putar = math.sin(lt * 1.2) * 2.5 + (1 - masuk) * 10
    tampal(fr, k, W / 2, H * b.get("y", 0.48 if ada_ov else 0.40) + math.sin(lt * 2.2) * 16 * u, skala=lerp(0.6, 1, masuk) * hembus, putar=putar)


def lukis_overlay(fr, b, lt, dur, cfg):
    o = b.get("overlay")
    if not o: return
    W, H = fr.size; u = W / 1080
    j = o.get("jenis")
    if j == "angka":
        # Angka besar bercahaya + count-up. {"teks":"10,000","unit":"mAh","label":"KAPASITI"}
        teks = o["teks"]; m = re.search(r"[\d,.]+", teks)
        p = ease_out(lt / 0.9)
        if m:
            sasaran = float(m.group().replace(",", ""))
            nil = sasaran * p
            fmt = f"{nil:,.0f}" if "," in m.group() else (f"{nil:.1f}" if "." in m.group() else f"{nil:.0f}")
            teks = teks[:m.start()] + fmt + teks[m.end():]
        y = H * o.get("y", 0.155)
        if o.get("label"):
            tampal(fr, pil(o["label"], int(40 * u), (255, 255, 255, 235), padx=int(28 * u), pady=int(14 * u)),
                   W / 2, y - 125 * u, alpha=kepit(lt / 0.3))
        sk = ease_back(lt / 0.45)
        tampal(fr, teks_img(teks, int(170 * u), KUNING, stroke=int(10 * u)), W / 2 - (90 * u if o.get("unit") else 0), y + 30 * u, skala=sk)
        if o.get("unit"):
            tampal(fr, teks_img(o["unit"], int(80 * u), PUTIH, stroke=int(7 * u)), W * 0.5 + 330 * u, y + 60 * u, skala=sk)
    elif j == "senarai":
        # Senarai tick muncul satu-satu. {"item":["...","..."]}
        items = o["item"]; y0 = H * o.get("y", 0.10)
        jarak = dur * 0.75 / max(1, len(items))
        for i, it in enumerate(items):
            tt = lt - 0.15 - i * jarak
            if tt < 0: continue
            e = ease_back(tt / 0.35)
            img = pil("✓  " if False else it, int(52 * u), (20, 20, 24, 235), warna=PUTIH, padx=int(34 * u), pady=int(20 * u), r=int(26 * u))
            tik = Image.new("RGBA", (int(78 * u), int(78 * u)), (0, 0, 0, 0))
            d = ImageDraw.Draw(tik); d.ellipse((0, 0, tik.width - 1, tik.height - 1), fill=HIJAU)
            s = tik.width
            d.line((s * .25, s * .52, s * .43, s * .7, s * .76, s * .32), fill=(0, 0, 0), width=int(10 * u), joint="curve")
            x = lerp(-W * 0.4, W * 0.08, e)
            yy = y0 + i * 125 * u
            fr.alpha_composite(tik, (int(x), int(yy - tik.height / 2)))
            fr.alpha_composite(img, (int(x + tik.width + 14 * u), int(yy - img.height / 2)))
    elif j == "harga":
        # {"asal":"RM59","baru":"RM29.90","label":"11.11 PROMO"}
        y = H * o.get("y", 0.12)
        if o.get("label"):
            tampal(fr, pil(o["label"], int(50 * u), MERAH, warna=PUTIH, glow=MERAH), W / 2, y - 40 * u,
                   skala=ease_back(lt / 0.4), putar=-3)
        if o.get("asal"):
            ia = teks_img(o["asal"], int(80 * u), (220, 220, 220), stroke=int(6 * u))
            tampal(fr, ia, W / 2, y + 95 * u, alpha=kepit((lt - 0.2) / 0.3))
            pc = kepit((lt - 0.5) / 0.35)
            if pc > 0:
                d = ImageDraw.Draw(fr)
                x0 = W / 2 - ia.width / 2 + 30 * u
                d.line((x0, y + 100 * u, x0 + (ia.width - 60 * u) * pc, y + 90 * u), fill=MERAH, width=int(12 * u))
        if o.get("baru"):
            tt = lt - 0.85
            if tt > 0:
                nadi = 1 + 0.04 * math.sin(tt * 7)
                tampal(fr, teks_img(o["baru"], int(170 * u), KUNING, stroke=int(11 * u)), W / 2, y + 245 * u,
                       skala=ease_back(tt / 0.4) * nadi)
    elif j == "cta":
        # Butang beg kuning + anak panah ke bakul TikTok (kiri bawah)
        teks = o.get("teks", "TEKAN BEG KUNING")
        y = H * o.get("y", 0.17)
        nadi = 1 + 0.06 * abs(math.sin(lt * 5))
        tampal(fr, pil(teks, int(64 * u), KUNING, glow=KUNING, padx=int(50 * u), pady=int(30 * u)), W / 2, y,
               skala=ease_back(lt / 0.4) * nadi)
        if o.get("sub"):
            tampal(fr, teks_img(o["sub"], int(46 * u), PUTIH, stroke=int(5 * u), berat=FON_TEBAL), W / 2, y + 110 * u,
                   alpha=kepit((lt - 0.3) / 0.3))
        # anak panah berdenyut ke bawah-kiri
        lantun = math.sin(lt * 6) * 25 * u
        ax, ay = W * 0.16, H * 0.80 + lantun
        d = ImageDraw.Draw(fr)
        for i in range(3):
            yy = ay - 180 * u + i * 60 * u
            al = int(255 * (0.4 + 0.6 * ((math.sin(lt * 6 - i) + 1) / 2)))
            d.line((ax - 45 * u, yy, ax, yy + 45 * u, ax + 45 * u, yy), fill=KUNING + (al,), width=int(16 * u), joint="curve")
    elif j == "tag":
        warna = {"merah": MERAH, "kuning": KUNING, "hijau": HIJAU}.get(o.get("warna", "kuning"), KUNING)
        tw = PUTIH if warna == MERAH else (0, 0, 0)
        tampal(fr, pil(o["teks"], int(56 * u), warna, warna=tw, glow=warna), W / 2, H * o.get("y", 0.12),
               skala=ease_back(lt / 0.4), putar=o.get("putar", -3))


def bersih(w): return re.sub(r"[^\w%.,+\-/]", "", w, flags=re.UNICODE)

def lukis_caption(fr, kata_aktif, lt_kata, sorot, cache):
    """Caption SATU perkataan, huruf besar, pop — macam video rujukan."""
    if not kata_aktif: return
    W, H = fr.size; u = W / 1080
    w = bersih(kata_aktif).upper()
    if not w: return
    if w not in cache:
        kuning = bool(re.search(r"\d|RM", w)) or bersih(kata_aktif).lower() in sorot
        saiz = int(118 * u)
        img = teks_img(w, saiz, KUNING if kuning else PUTIH, stroke=int(11 * u))
        while img.width > W * 0.86 and saiz > 50:
            saiz -= 8; img = teks_img(w, saiz, KUNING if kuning else PUTIH, stroke=int(11 * u))
        cache[w] = img
    sk = lerp(1.3, 1.0, ease_out(lt_kata / 0.12))
    tampal(fr, cache[w], W / 2, H * 0.70, skala=sk)


# ───────────────────────── utama ─────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("projek")
    ap.add_argument("--pratonton", action="store_true", help="render 540x960 laju")
    ap.add_argument("--fps", type=int, default=30)
    arg = ap.parse_args()

    folder = Path(arg.projek).resolve()
    cfg = json.loads((folder / "skrip.json").read_text())
    cfg.setdefault("suara", "ms-MY-OsmanNeural"); cfg.setdefault("laju", "+12%"); cfg.setdefault("pic", "+0Hz")
    W, H = (540, 960) if arg.pratonton else (1080, 1920)
    FPS = 24 if arg.pratonton else arg.fps
    keluar = folder / "keluaran"; keluar.mkdir(exist_ok=True)
    cache = folder / ".cache"; cache.mkdir(exist_ok=True)

    # 1) suara
    print("🎙  Jana suara AI...")
    babak, audio_bah, t = [], [], 0.0
    sorot = set()
    for b in cfg["babak"]:
        for m in re.findall(r"\*([^*]+)\*", b["teks"]):
            sorot.update(bersih(x).lower() for x in m.split())
        teks_tts = b["teks"].replace("*", "")
        aud, kata = suara_babak(teks_tts, cfg, cache)
        jeda = b.get("jeda", 0.12)
        dur = len(aud) / SR + jeda
        for k in kata: k["t"] += t
        babak.append({**b, "mula": t, "dur": dur, "kata": kata})
        audio_bah.append((t, aud)); t += dur
    jumlah = t + 0.4
    print(f"   {len(babak)} babak, {jumlah:.1f} saat")

    # 2) audio campur
    n = int(jumlah * SR)
    vokal = np.zeros(n, np.float32)
    for mula, aud in audio_bah:
        a = int(mula * SR); vokal[a:a + len(aud)] += aud[: n - a]
    sfx = np.zeros(n, np.float32)
    wh = whoosh(); pp = pop()
    for i, b in enumerate(babak):
        a = int(max(0, b["mula"] - 0.15) * SR)
        s = wh if i else pp
        sfx[a:a + len(s)] += s[: n - a] * 0.6
        if b.get("overlay"):
            a = int((b["mula"] + 0.05) * SR); sfx[a:a + len(pp)] += pp[: n - a] * 0.5
    muzik_cfg = cfg.get("muzik", True)
    if isinstance(muzik_cfg, str) and (folder / muzik_cfg).exists():
        mz = baca_audio(folder / muzik_cfg); mz = np.tile(mz, int(n / len(mz)) + 1)[:n]
        mz = mz / (np.abs(mz).max() + 1e-6) * 0.18
    elif muzik_cfg:
        mz = jana_beat(jumlah); mz = mz / (np.abs(mz).max() + 1e-6) * 0.13
    else:
        mz = np.zeros(n, np.float32)
    fade = np.minimum(1, np.arange(n) / (0.3 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.8 * SR))
    vokal = vokal / (np.abs(vokal).max() + 1e-6) * 0.92
    camp = vokal + sfx + mz * fade
    camp = np.tanh(camp * 1.1) * 0.95
    wav = cache / "campur.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((camp * 32767).astype(np.int16).tobytes())

    # 3) visual
    aset = Aset(cfg, folder, W, H)
    nama = "pratonton.mp4" if arg.pratonton else "video.mp4"
    out = keluar / nama
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", str(wav), "-c:v", "libx264", "-preset",
                           "veryfast" if arg.pratonton else "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)],
                          stdin=subprocess.PIPE)
    semua_kata = [k for b in babak for k in b["kata"]]
    cap_cache = {}
    nf = int(jumlah * FPS)
    print(f"🎬 Render {nf} frame ({W}x{H})...")
    for f in range(nf):
        tm = f / FPS
        bi = max(i for i, b in enumerate(babak) if b["mula"] <= tm + 1e-6) if tm >= babak[0]["mula"] else 0
        b = babak[min(bi, len(babak) - 1)]
        lt = tm - b["mula"]
        fr = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        lukis_visual(fr, aset, b, lt, b["dur"])
        lukis_overlay(fr, b, lt, b["dur"], cfg)
        # perkataan aktif
        aktif, lk = None, 0
        for i, k in enumerate(semua_kata):
            tamat = semua_kata[i + 1]["t"] if i + 1 < len(semua_kata) else k["t"] + k["d"] + 0.4
            tamat = min(tamat, k["t"] + k["d"] + 0.35)
            if k["t"] - 0.03 <= tm < tamat: aktif, lk = k["w"], tm - k["t"]; break
        lukis_caption(fr, aktif, lk, sorot, cap_cache)
        # bar progres atas
        d = ImageDraw.Draw(fr)
        d.rectangle((0, 0, int(W * tm / jumlah), int(8 * W / 1080)), fill=KUNING)
        # kilat putih bila tukar babak
        if bi > 0 and lt < 0.1:
            fr.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(150 * (1 - lt / 0.1)))))
        ff.stdin.write(fr.convert("RGB").tobytes())
        if f % (FPS * 5) == 0: print(f"   {tm:5.1f}s / {jumlah:.1f}s", flush=True)
    ff.stdin.close(); ff.wait()

    # 4) fail sokongan
    (keluar / "skrip_teleprompter.txt").write_text(
        f"{cfg.get('nama_produk', '')}\n\n" + "\n\n".join(
            f"[{i + 1}] ({b.get('peranan', '')}) {b['teks'].replace('*', '')}" for i, b in enumerate(cfg["babak"])) + "\n")
    if cfg.get("caption_tiktok"):
        (keluar / "caption_tiktok.txt").write_text(cfg["caption_tiktok"] + "\n")
    print(f"✅ Siap: {out}")


if __name__ == "__main__":
    main()
