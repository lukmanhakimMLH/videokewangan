"""
Adegan: produk (dipotong dari screenshot) diletak dalam suasana — default
"kereta_malam": atas dashboard, cermin depan penuh lampu bandar (bokeh),
pantulan & bayang, kamera goyang macam dipegang tangan.

Latar lain: "studio", atau fail gambar sendiri (cth "latar": "kereta_aku.jpg").
"""
import hashlib, math, urllib.request
from pathlib import Path
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

from .grafik import bucu_bulat, ease_back, ease_out, kepit, lerp, tampal

AKAR = Path(__file__).resolve().parent.parent
MODEL = AKAR / "aset/model/birefnet_lite.onnx"
MODEL_URL = "https://huggingface.co/onnx-community/BiRefNet_lite-ONNX/resolve/main/onnx/model.onnx"


# ───────────── potong produk dari screenshot ─────────────
_sesi = None
def potong_latar(img, cache):
    """Buang latar belakang produk (BiRefNet, lesen MIT). Pulang RGBA dipangkas."""
    k = hashlib.md5(img.tobytes()).hexdigest()[:14]
    f = cache / f"potong_{k}.png"
    if f.exists(): return Image.open(f).convert("RGBA")
    global _sesi
    if _sesi is None:
        if not MODEL.exists():
            print("   muat turun model potong latar (~220MB, sekali sahaja)...")
            MODEL.parent.mkdir(parents=True, exist_ok=True)
            import ssl, os
            ca = "/root/.ccr/ca-bundle.crt"
            ctx = ssl.create_default_context(cafile=ca) if os.path.exists(ca) else None
            with urllib.request.urlopen(MODEL_URL, context=ctx) as r: MODEL.write_bytes(r.read())
        import onnxruntime as ort
        _sesi = ort.InferenceSession(str(MODEL), providers=["CPUExecutionProvider"])
    x = np.asarray(img.convert("RGB").resize((1024, 1024), Image.BILINEAR), np.float32) / 255
    x = (x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
    inp = _sesi.get_inputs()[0].name
    o = _sesi.run(None, {inp: x.transpose(2, 0, 1)[None].astype(np.float32)})[-1][0, 0]
    m = 1 / (1 + np.exp(-o))
    alpha = Image.fromarray((m * 255).astype(np.uint8)).resize(img.size, Image.BILINEAR)
    # buang serpihan kecil (teks/harga) — simpan blob terbesar sahaja
    try:
        from scipy import ndimage
        lab, n = ndimage.label(np.asarray(alpha) > 128)
        if n > 1:
            saiz = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
            simpan = np.isin(lab, 1 + np.where(saiz >= saiz.max() * 0.15)[0])
            simpan = ndimage.binary_dilation(simpan, iterations=6)
            alpha = Image.fromarray((np.asarray(alpha) * simpan).astype(np.uint8))
    except ImportError:
        pass
    out = img.convert("RGB").copy(); out.putalpha(alpha)
    bbox = alpha.point(lambda v: 255 if v > 20 else 0).getbbox()
    if bbox: out = out.crop(bbox)
    out.save(f)
    return out


# ───────────── bina set dalam kereta ─────────────
def _bokeh(w, h, u, seed=11):
    rng = np.random.default_rng(seed)
    lap = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    palet = [(255, 170, 70), (255, 120, 40), (255, 210, 150), (255, 60, 50), (120, 200, 255), (255, 240, 220)]
    for lapis, (n, rmin, rmax, blur, al) in enumerate([(55, 40, 110, 14, 110), (70, 18, 55, 6, 170)]):
        L = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        for _ in range(n):
            r = rng.uniform(rmin, rmax) * u
            x = rng.uniform(0, w); y = rng.normal(h * 0.62, h * 0.18)
            c = palet[rng.integers(len(palet))]
            d.ellipse((x - r, y - r, x + r, y + r), fill=c + (int(al * rng.uniform(0.5, 1)),),
                      outline=c + (min(255, al + 60),), width=max(1, int(3 * u)))
        lap = Image.alpha_composite(lap, L.filter(ImageFilter.GaussianBlur(blur * u)))
    # langit malam
    langit = Image.linear_gradient("L").resize((w, h)).point(lambda v: int(v * 0.25))
    base = Image.merge("RGBA", (langit.point(lambda v: v // 3), langit.point(lambda v: v // 2), langit, Image.new("L", (w, h), 255)))
    base.alpha_composite(lap)
    # sambung hujung supaya boleh 'bergerak' tanpa putus
    return base


def _kabin(W, H, u, bokeh):
    """Dashboard + tiang A + bumbung (RGBA, cermin depan lutsinar)."""
    kab = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    xs = np.arange(W)
    tepi = H * 0.565 + ((xs / W - 0.5) ** 2) * H * 0.10          # lengkung atas dashboard
    yy = np.arange(H)[:, None]
    dalam = yy >= tepi[None, :]
    jarak = np.clip((yy - tepi[None, :]) / (H * 0.45), 0, 1)
    rng = np.random.default_rng(5)
    tekstur = rng.normal(0, 3.5, (H, W))
    v = 34 * (1 - jarak) ** 1.4 + 6 + tekstur
    kilat = np.exp(-np.clip(yy - tepi[None, :], 0, None) / (14 * u)) * 55 * dalam   # garis kilat di bibir dashboard
    v = v + kilat
    rgb = np.stack([v, v, v * 1.08], -1).clip(0, 255).astype(np.uint8)
    a = (dalam * 255).astype(np.uint8)
    dash = Image.fromarray(np.dstack([rgb, a]), "RGBA")
    # pantulan lampu bandar pada dashboard berkilat
    pant = ImageOps.flip(bokeh.resize((W, int(H * 0.5)))).filter(ImageFilter.GaussianBlur(18 * u))
    pl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); pl.paste(pant, (0, int(H * 0.56)))
    pa = Image.fromarray((dalam * np.clip(1 - jarak * 2.2, 0, 1) * 70).astype(np.uint8))
    pl.putalpha(ImageChops.multiply(pl.getchannel("A"), pa))
    dash = Image.alpha_composite(dash, pl)
    # jahitan
    d = ImageDraw.Draw(dash)
    for x in range(0, W, int(26 * u)):
        y = tepi[min(x, W - 1)] + 38 * u
        d.line((x, y, x + 13 * u, y + ((x / W - 0.5) * 2) * 2.6 * u), fill=(70, 70, 76, 200), width=max(1, int(3 * u)))
    kab.alpha_composite(dash)
    # tiang A & bumbung
    t = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(t)
    gelap = (6, 6, 8, 255)
    d.polygon([(0, 0), (W * 0.20, 0), (W * 0.035, H * 0.60), (0, H * 0.60)], fill=gelap)
    d.polygon([(W, 0), (W * 0.80, 0), (W * 0.965, H * 0.60), (W, H * 0.60)], fill=gelap)
    d.rectangle((0, 0, W, H * 0.07), fill=gelap)
    d.polygon([(W * 0.40, H * 0.07), (W * 0.60, H * 0.07), (W * 0.57, H * 0.115), (W * 0.43, H * 0.115)], fill=gelap)  # cermin pandang belakang
    t = t.filter(ImageFilter.GaussianBlur(5 * u))
    kab.alpha_composite(t)
    return kab, tepi


class Pentas:
    def __init__(self, W, H, cfg, folder, cache):
        self.W, self.H, self.u = W, H, W / 1080
        self.cfg = cfg
        self.latar = cfg.get("latar", "kereta_malam")
        self.ss, self.produk = [], []
        for p in cfg["gambar_produk"]:
            spec = p if isinstance(p, dict) else {"fail": p}
            img = ImageOps.exif_transpose(Image.open(folder / spec["fail"])).convert("RGB")
            self.ss.append(img)
            if "potong" in spec:
                x0, y0, x1, y1 = spec["potong"]
                img = img.crop((int(x0 * img.width), int(y0 * img.height), int(x1 * img.width), int(y1 * img.height)))
            self.produk.append(potong_latar(img, cache) if spec.get("buang_latar", True) else img.convert("RGBA"))
        u = self.u
        if self.latar == "kereta_malam":
            self.bokeh = _bokeh(int(W * 2.2), int(H * 0.62), u)
            self.kabin, self.tepi = _kabin(W, H, u, self.bokeh)
            self.lantai = H * 0.66
        elif self.latar == "studio":
            g = Image.radial_gradient("L").resize((W, H)).point(lambda v: int(255 - v * 0.9))
            self.bg = Image.merge("RGBA", (g.point(lambda v: v * 34 // 255), g.point(lambda v: v * 32 // 255),
                                           g.point(lambda v: v * 40 // 255), Image.new("L", (W, H), 255)))
            self.lantai = H * 0.64
        else:
            img = ImageOps.exif_transpose(Image.open(folder / self.latar)).convert("RGB")
            self.bg = ImageOps.fit(img, (int(W * 1.12), int(H * 1.12)), Image.LANCZOS).convert("RGBA")
            self.lantai = H * cfg.get("lantai", 0.66)
        self._skala = {}
        self._kad = {}

    # ── produk ──
    def _produk_saiz(self, gi, tinggi):
        k = (gi, int(tinggi))
        if k not in self._skala:
            p = self.produk[gi]
            lebar = p.width * tinggi / p.height
            if lebar > self.W * 0.8: tinggi = tinggi * self.W * 0.8 / lebar; lebar = self.W * 0.8
            self._skala[k] = p.resize((max(1, int(lebar)), max(1, int(tinggi))), Image.LANCZOS)
        return self._skala[k]

    def _kilau(self, img, fasa):
        """Jalur cahaya melintas atas produk."""
        w, h = img.size
        x = (np.arange(w)[None, :] + np.arange(h)[:, None] * 0.5) / (w + h * 0.5)
        band = np.exp(-((x - fasa) / 0.07) ** 2) * 0.45
        a = (np.asarray(img.getchannel("A"), np.float32) / 255 * band * 255).astype(np.uint8)
        lap = Image.new("RGBA", (w, h), (255, 255, 255, 0)); lap.putalpha(Image.fromarray(a))
        return Image.alpha_composite(img, lap)

    def _letak_produk(self, fr, gi, cx, dasar_y, tinggi, putar=0.0, skala_x=1.0, terapung=0.0, fasa_kilau=None):
        p = self._produk_saiz(gi, tinggi)
        if abs(skala_x - 1) > 0.01:
            p = p.resize((max(1, int(p.width * skala_x)), p.height), Image.BILINEAR)
        if fasa_kilau is not None and -0.2 < fasa_kilau < 1.2:
            p = self._kilau(p, fasa_kilau)
        u = self.u
        # bayang di lantai
        lb = p.width * 0.95
        sh = Image.new("RGBA", (int(lb + 160 * u), int(120 * u)), (0, 0, 0, 0))
        al = int(230 * (1 - kepit(terapung / (self.H * 0.25))))
        ImageDraw.Draw(sh).ellipse((80 * u, 40 * u, 80 * u + lb, 80 * u), fill=(0, 0, 0, al))
        sh = sh.filter(ImageFilter.GaussianBlur(16 * u))
        fr.alpha_composite(sh, (int(cx - sh.width / 2), int(dasar_y - sh.height / 2)))
        # pantulan
        if terapung < self.H * 0.05 and self.latar != "gambar":
            ref = ImageOps.flip(p)
            g = Image.linear_gradient("L").resize(ref.size).point(lambda v: int(max(0, 70 - v * 0.5)))
            ref.putalpha(ImageChops.multiply(ref.getchannel("A"), g))
            ref = ref.filter(ImageFilter.GaussianBlur(3 * u))
            fr.alpha_composite(ref, (int(cx - ref.width / 2), int(dasar_y + 4 * u)))
        y = dasar_y - p.height / 2 - terapung
        tampal(fr, p, cx, y, putar=putar)

    # ── latar ──
    def _latar(self, tm):
        W, H = self.W, self.H
        fr = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        if self.latar == "kereta_malam":
            bw = self.bokeh.width
            x = int((tm * 38 * self.u) % (bw - W))       # kereta 'bergerak' perlahan
            fr.paste(self.bokeh.crop((x, 0, x + W, self.bokeh.height)), (0, 0))
            # lampu kereta lain lalu sekali-sekala
            fasa = (tm % 7.0) / 7.0
            if fasa < 0.35:
                gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                cx = lerp(-W * 0.3, W * 1.3, fasa / 0.35)
                ImageDraw.Draw(gl).ellipse((cx - 260 * self.u, H * 0.25, cx + 260 * self.u, H * 0.50),
                                           fill=(255, 190, 120, 70))
                fr.alpha_composite(gl.filter(ImageFilter.GaussianBlur(70 * self.u)))
            fr.alpha_composite(self.kabin)
        else:
            dx = (self.bg.width - W) / 2 * (1 + math.sin(tm * 0.2))
            dy = (self.bg.height - H) / 2 * (1 + math.cos(tm * 0.17))
            fr.paste(self.bg.crop((int(dx), int(dy), int(dx) + W, int(dy) + H)), (0, 0))
        return fr

    def _kad_ss(self, gi, lebar):
        k = (gi, lebar)
        if k not in self._kad:
            img = self.ss[gi]
            h = int(img.height * lebar / img.width)
            if h > self.H * 0.42: lebar = int(lebar * self.H * 0.42 / h); h = int(self.H * 0.42)
            im = bucu_bulat(img.resize((lebar, h), Image.LANCZOS), int(30 * self.u))
            g = int(14 * self.u)
            kad = Image.new("RGBA", (lebar + g * 2, h + g * 2), (0, 0, 0, 0))
            ImageDraw.Draw(kad).rounded_rectangle((0, 0, kad.width - 1, kad.height - 1), int(40 * self.u), fill=(255, 255, 255, 240))
            kad.alpha_composite(im, (g, g))
            self._kad[k] = kad
        return self._kad[k]

    # ── lukis satu frame ──
    def lukis(self, b, lt, dur, tm):
        W, H, u = self.W, self.H, self.u
        jenis = b.get("visual", "hero")
        gi = b.get("gambar", 0)
        p = lt / max(dur, 0.01)
        ada_ov = bool(b.get("overlay"))
        fr = self._latar(tm)
        tinggi = H * (b.get("saiz") or (0.31 if ada_ov else 0.40))
        cx, dasar = W / 2, self.lantai
        kilau = (lt - 0.3) / 1.1
        zoom, fx, fy = 1.0 + 0.07 * p, 0.5, 0.55

        if jenis == "hero":
            masuk = ease_out(lt / 0.5)
            self._letak_produk(fr, gi, cx, dasar, tinggi * lerp(0.9, 1, masuk), putar=math.sin(lt * 0.9) * 1.2,
                               fasa_kilau=kilau)
        elif jenis == "angkat":       # produk 'diangkat' dari bawah, terapung
            naik = ease_back(lt / 0.55)
            terapung = lerp(-H * 0.5, H * 0.07, naik) + math.sin(lt * 2.2) * 10 * u
            self._letak_produk(fr, gi, cx, dasar - min(0, terapung), tinggi, putar=math.sin(lt * 1.4) * 4 * (1 - p * 0.5),
                               terapung=max(0, terapung), fasa_kilau=kilau)
        elif jenis == "putar":        # pusing 3D palsu
            sx = 0.72 + 0.28 * math.cos(lt * 2.4)
            self._letak_produk(fr, gi, cx, dasar, tinggi, skala_x=sx, fasa_kilau=kilau)
        elif jenis == "dekat":        # close-up
            self._letak_produk(fr, gi, cx, dasar, tinggi, fasa_kilau=kilau)
            fokus = b.get("fokus", [0.5, 0.4])
            ph = self._produk_saiz(gi, tinggi)
            fx = (cx - ph.width / 2 + fokus[0] * ph.width) / W
            fy = (dasar - ph.height + fokus[1] * ph.height) / H
            zoom = lerp(1.55, 1.85, ease_out(p))
        elif jenis == "screenshot":   # tunjuk screenshot asal (harga/review) atas latar kabur
            fr = fr.filter(ImageFilter.GaussianBlur(10 * u))
            k = self._kad_ss(gi, int(W * 0.78))
            tampal(fr, k, W / 2, H * (0.46 if ada_ov else 0.42), skala=lerp(0.85, 1, ease_back(lt / 0.4)),
                   putar=math.sin(lt * 1.1) * 1.5)
            zoom = 1.0 + 0.03 * p

        # transisi: tumbukan zoom masa masuk babak
        zoom += 0.10 * (1 - ease_out(lt / 0.28))
        # kamera dipegang tangan
        zoom = max(zoom, 1.035)
        gx = (5 * math.sin(tm * 1.3) + 3 * math.sin(tm * 2.9 + 1)) * u
        gy = (4 * math.sin(tm * 1.7 + 2) + 3 * math.sin(tm * 3.3)) * u
        cw, ch = W / zoom, H / zoom
        x0 = kepit(fx * W - cw / 2 + gx, 0, W - cw); y0 = kepit(fy * H - ch / 2 + gy, 0, H - ch)
        fr = fr.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
        return fr
