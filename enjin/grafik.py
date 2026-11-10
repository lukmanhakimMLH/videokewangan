"""Grafik: util lukisan, infografik (overlay) & caption satu perkataan."""
import math, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

AKAR = Path(__file__).resolve().parent.parent
FON_HITAM = str(AKAR / "aset/font/Montserrat-900.ttf")
FON_TEBAL = str(AKAR / "aset/font/Montserrat-700.ttf")
KUNING = (255, 214, 10)
MERAH = (255, 59, 48)
HIJAU = (52, 230, 120)
PUTIH = (255, 255, 255)

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
            img = pil(it, int(52 * u), (20, 20, 24, 235), warna=PUTIH, padx=int(34 * u), pady=int(20 * u), r=int(26 * u))
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

def lukis_caption(fr, unit, lt, cache, y=0.70):
    """Caption SATU perkataan/frasa, huruf besar, pop — macam video rujukan."""
    if not unit: return
    W, H = fr.size; u = W / 1080
    w = " ".join(bersih(x) for x in unit["w"].split()).upper().strip()
    if not w: return
    kuning = unit.get("sorot") or bool(re.search(r"\d|RM", w))
    k = (w, kuning)
    if k not in cache:
        saiz = int(118 * u)
        img = teks_img(w, saiz, KUNING if kuning else PUTIH, stroke=int(11 * u))
        while img.width > W * 0.88 and saiz > 50:
            saiz -= 8; img = teks_img(w, saiz, KUNING if kuning else PUTIH, stroke=int(11 * u))
        cache[k] = img
    sk = lerp(1.3, 1.0, ease_out(lt / 0.12))
    tampal(fr, cache[k], W / 2, H * y, skala=sk)
