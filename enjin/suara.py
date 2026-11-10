"""
Suara latar (voice-over) + masa setiap perkataan untuk caption.

Tiga enjin:
  "edge"       — suara neural BM percuma (ms-MY-OsmanNeural / ms-MY-YasminNeural).
                 Untuk kurangkan bunyi robot: setiap AYAT dijana berasingan dengan
                 intonasi berbeza (ikut gaya babak + tanda baca), dan ada jeda semula jadi.
  "elevenlabs" — suara sangat natural (perlu API key ElevenLabs).
  "rakaman"    — suara kau sendiri (fail audio). Caption disegerakkan guna Whisper.

Sintaks teks dalam skrip:
  *perkataan*              → caption kuning
  [10,000mAh|sepuluh ribu em ei ec]  → caption papar "10,000mAh", suara sebut kanan
"""
import asyncio, hashlib, json, os, re, ssl, subprocess
from pathlib import Path
import numpy as np

SR = 44100

# Intonasi ikut gaya babak: (tambah laju %, tambah pic Hz)
GAYA = {
    "teruja": (10, 6),
    "santai": (2, 0),
    "yakin": (0, -3),
    "serius": (-6, -6),
    "mendesak": (14, 4),
}
JEDA_TANDA = {".": 0.22, "!": 0.18, "?": 0.28, "…": 0.45, ",": 0.0}


# ───────────── parse teks skrip ─────────────
TOKEN = re.compile(r"\[([^\]|]+)\|([^\]]+)\]|\S+")

def parse_ayat(teks):
    """Pecah teks babak → senarai ayat. Setiap ayat: {sebut, tanda, unit:[{papar, n, sorot}]}."""
    teks = teks.replace("...", "…")
    ayat, semasa = [], []
    for m in TOKEN.finditer(teks):
        if m.group(1):
            papar, sebut = m.group(1).strip(), m.group(2).strip()
            tanda = ""
            nxt = teks[m.end():m.end() + 1]
            if nxt in ".!?…": tanda = nxt
        else:
            tok = m.group(0)
            sorot = "*" in tok
            tok = tok.replace("*", "")
            tanda = tok[-1] if tok and tok[-1] in ".!?…" else ""
            papar = sebut = tok
        bersih_sebut = sebut.strip(".!?…")
        if bersih_sebut:
            n = len(re.findall(r"[\w%]+", bersih_sebut)) or 1
            semasa.append({"papar": papar.strip(".,!?…;:"), "sebut": sebut, "n": n,
                           "sorot": bool(m.group(1)) or ("*" in m.group(0))})
        if tanda and semasa:
            ayat.append({"unit": semasa, "tanda": tanda}); semasa = []
    if semasa: ayat.append({"unit": semasa, "tanda": "."})
    for a in ayat:
        a["sebut"] = " ".join(u["sebut"] for u in a["unit"]).replace("…", "...")
        if not a["sebut"].rstrip()[-1:] in ".!?": a["sebut"] += a["tanda"].replace("…", "...")
    return ayat


def peta_caption(ayat_unit, kata, t0):
    """Gabungkan WordBoundary TTS ikut unit papar. Kalau tak padan, guna perkataan TTS terus."""
    perlu = sum(u["n"] for u in ayat_unit)
    out = []
    if perlu == len(kata):
        i = 0
        for u in ayat_unit:
            kk = kata[i:i + u["n"]]; i += u["n"]
            out.append({"t": t0 + kk[0]["t"], "d": kk[-1]["t"] + kk[-1]["d"] - kk[0]["t"],
                        "w": u["papar"], "sorot": u["sorot"]})
    else:
        sorot = {re.sub(r"\W", "", w).lower() for u in ayat_unit if u["sorot"] for w in u["papar"].split()}
        for k in kata:
            out.append({"t": t0 + k["t"], "d": k["d"], "w": k["w"], "sorot": re.sub(r"\W", "", k["w"]).lower() in sorot})
    return out


# ───────────── util audio ─────────────
def baca_audio(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()

def potong_senyap(a, ambang=0.012):
    """Buang senyap awal/akhir supaya jeda kita yang kawal."""
    idx = np.where(np.abs(a) > ambang)[0]
    if len(idx) == 0: return a, 0.0
    s = max(0, idx[0] - int(0.03 * SR)); e = min(len(a), idx[-1] + int(0.06 * SR))
    return a[s:e], s / SR

def _ssl_ctx():
    ca = os.environ.get("SSL_CERT_FILE") or ("/root/.ccr/ca-bundle.crt" if Path("/root/.ccr/ca-bundle.crt").exists() else None)
    return ssl.create_default_context(cafile=ca) if ca else None


# ───────────── enjin edge ─────────────
async def _edge(teks, suara, laju, pic, mp3):
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

def _pct(s):
    return int(str(s).replace("%", "").replace("+", "") or 0)

def edge_ayat(ayat, idx, jumlah, gaya, cfg, cache):
    dl, dp = GAYA.get(gaya, GAYA["santai"])
    if ayat["tanda"] == "!": dl += 4; dp += 4
    if ayat["tanda"] == "?": dp += 7
    if idx == jumlah - 1 and jumlah > 1: dl -= 4            # ayat akhir babak: sedikit perlahan
    if len(ayat["unit"]) <= 3: dl -= 6                      # ayat pendek: tekan, jangan laju
    laju = _pct(cfg.get("laju", "+8%")) + dl
    pic = int(str(cfg.get("pic", "+0Hz")).replace("Hz", "").replace("+", "") or 0) + dp
    laju_s, pic_s = f"{laju:+d}%", f"{pic:+d}Hz"
    k = hashlib.md5(f"edge|{ayat['sebut']}|{cfg['suara']}|{laju_s}|{pic_s}".encode()).hexdigest()[:14]
    mp3, js = cache / f"{k}.mp3", cache / f"{k}.json"
    if not (mp3.exists() and js.exists()):
        kata = asyncio.run(_edge(ayat["sebut"], cfg["suara"], laju_s, pic_s, mp3))
        js.write_text(json.dumps(kata, ensure_ascii=False))
    return baca_audio(mp3), json.loads(js.read_text())


# ───────────── enjin elevenlabs ─────────────
def elevenlabs_babak(teks, cfg, cache):
    import urllib.request
    vid = cfg.get("voice_id") or "pNInz6obpgDQGcFmaJgB"
    k = hashlib.md5(f"el|{teks}|{vid}".encode()).hexdigest()[:14]
    mp3 = cache / f"{k}.mp3"
    if not mp3.exists():
        body = json.dumps({"text": teks, "model_id": cfg.get("model_el", "eleven_multilingual_v2"),
                           "voice_settings": {"stability": 0.35, "similarity_boost": 0.8, "style": 0.35,
                                              "use_speaker_boost": True}}).encode()
        req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}?output_format=mp3_44100_128",
                                     data=body, headers={"Content-Type": "application/json",
                                                         "xi-api-key": os.environ.get("ELEVENLABS_API_KEY", "proxy")})
        with urllib.request.urlopen(req, context=_ssl_ctx(), timeout=120) as r:
            mp3.write_bytes(r.read())
    return mp3


# ───────────── Whisper (untuk rakaman / elevenlabs) ─────────────
_whisper = None
def transkrip_kata(path, cache):
    k = hashlib.md5(Path(path).read_bytes()).hexdigest()[:14]
    js = cache / f"w_{k}.json"
    if js.exists(): return json.loads(js.read_text())
    global _whisper
    from faster_whisper import WhisperModel
    if _whisper is None: _whisper = WhisperModel("small", device="cpu", compute_type="int8")
    a = baca_audio(path)
    a16 = np.interp(np.arange(0, len(a), SR / 16000), np.arange(len(a)), a).astype(np.float32)
    segs, _ = _whisper.transcribe(a16, language="ms", word_timestamps=True)
    kata = [{"t": w.start, "d": w.end - w.start, "w": w.word.strip()} for s in segs for w in s.words]
    js.write_text(json.dumps(kata, ensure_ascii=False))
    return kata


# ───────────── utama ─────────────
def jana(cfg, folder, cache):
    """Pulangkan (audio_vokal, senarai_babak_dengan_masa, caption_units)."""
    enjin = cfg.get("enjin_suara", "edge")
    babak_out, caps, potongan, t = [], [], [], 0.0

    if enjin == "rakaman":
        # Satu fail suara untuk semua babak; bahagi babak ikut bilangan perkataan.
        a = baca_audio(folder / cfg["fail_suara"])
        kata = transkrip_kata(folder / cfg["fail_suara"], cache)
        n_babak = [sum(u["n"] for ay in parse_ayat(b["teks"]) for u in ay["unit"]) for b in cfg["babak"]]
        skala = len(kata) / max(1, sum(n_babak))
        i = 0
        for bi, b in enumerate(cfg["babak"]):
            ambil = round(n_babak[bi] * skala) if bi < len(cfg["babak"]) - 1 else len(kata) - i
            kk = kata[i:i + max(1, ambil)]; i += ambil
            mula = 0.0 if bi == 0 else kk[0]["t"] - 0.08 if kk else t
            babak_out.append({**b, "mula": mula})
            t = mula
        for j, b in enumerate(babak_out):
            b["dur"] = (babak_out[j + 1]["mula"] if j + 1 < len(babak_out) else len(a) / SR + 0.4) - b["mula"]
        sorot = {re.sub(r"\W", "", w).lower() for b in cfg["babak"] for ay in parse_ayat(b["teks"])
                 for u in ay["unit"] if u["sorot"] for w in u["papar"].split()}
        caps = [{**k, "sorot": re.sub(r"\W", "", k["w"]).lower() in sorot} for k in kata]
        return a, babak_out, caps

    for b in cfg["babak"]:
        ayat = parse_ayat(b["teks"])
        mula_babak = t
        if enjin == "elevenlabs":
            sebut = " ".join(a["sebut"] for a in ayat)
            mp3 = elevenlabs_babak(sebut, cfg, cache)
            aud, off = potong_senyap(baca_audio(mp3))
            kata = transkrip_kata(mp3, cache)
            semua_unit = [u for a in ayat for u in a["unit"]]
            caps += peta_caption(semua_unit, [{**k, "t": k["t"] - off} for k in kata], t)
            potongan.append((t, aud)); t += len(aud) / SR + 0.15
        else:
            for i, ay in enumerate(ayat):
                aud, kata = edge_ayat(ay, i, len(ayat), b.get("gaya", "santai"), cfg, cache)
                aud, off = potong_senyap(aud)
                caps += peta_caption(ay["unit"], [{**k, "t": k["t"] - off} for k in kata], t)
                potongan.append((t, aud))
                t += len(aud) / SR + JEDA_TANDA.get(ay["tanda"], 0.2)
        t += b.get("jeda", 0.05)
        babak_out.append({**b, "mula": mula_babak, "dur": t - mula_babak})

    n = int((t + 0.5) * SR)
    vokal = np.zeros(n, np.float32)
    for mula, aud in potongan:
        a = int(mula * SR); vokal[a:a + len(aud)] += aud[: n - a]
    return vokal, babak_out, caps


def kemas_suara(vokal):
    """EQ + kompresi ringan supaya suara lebih 'dekat' & hangat (kurang rasa robot)."""
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        i, o = Path(d) / "i.f32", Path(d) / "o.f32"
        vokal.astype(np.float32).tofile(i)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", str(i),
                        "-af", "highpass=f=80,equalizer=f=180:t=q:w=1:g=2.5,equalizer=f=3200:t=q:w=1.2:g=2,"
                               "equalizer=f=7500:t=q:w=1:g=-2,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=3",
                        "-f", "f32le", str(o)], check=True)
        return np.fromfile(o, np.float32)
