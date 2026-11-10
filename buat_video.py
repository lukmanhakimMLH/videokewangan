#!/usr/bin/env python3
"""
buat_video.py — Screenshot produk ➜ video jualan gaya TikTok affiliate (9:16).

    python3 buat_video.py projek/contoh               # final 1080x1920
    python3 buat_video.py projek/contoh --pratonton   # 540x960 laju untuk semak

Baca <projek>/skrip.json, keluarkan <projek>/keluaran/{video.mp4, skrip_teleprompter.txt, caption_tiktok.txt}
"""
import argparse, json, re, subprocess, wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from enjin import audio, suara
from enjin.adegan import Pentas
from enjin.grafik import KUNING, lukis_caption, lukis_overlay

SR = suara.SR


def campur_audio(vokal, babak, cfg, folder, jumlah):
    n = int(jumlah * SR)
    vok = np.zeros(n, np.float32); vok[: min(n, len(vokal))] = vokal[:n]
    vok = suara.kemas_suara(vok)[:n]
    vok = vok / (np.abs(vok).max() + 1e-6) * 0.9
    sfx = np.zeros(n, np.float32); wh, pp = audio.whoosh(), audio.pop()
    for i, b in enumerate(babak):
        if i:
            a = int(max(0, b["mula"] - 0.18) * SR); sfx[a:a + len(wh)] += wh[: n - a] * 0.45
        if b.get("overlay"):
            a = int((b["mula"] + 0.05) * SR); sfx[a:a + len(pp)] += pp[: n - a] * 0.4
    m = cfg.get("muzik", True)
    if isinstance(m, str) and (folder / m).exists():
        mz = suara.baca_audio(folder / m); mz = np.tile(mz, n // len(mz) + 1)[:n]; vol = 0.16
    elif m:
        mz = audio.jana_beat(jumlah)[:n]; vol = 0.11
    else:
        mz = np.zeros(n, np.float32); vol = 0
    mz = mz / (np.abs(mz).max() + 1e-6) * vol
    # 'ducking': muzik turun bila ada suara
    env = np.convolve(np.abs(vok), np.ones(int(0.25 * SR)) / (0.25 * SR), "same")
    duck = 1 - 0.45 * np.clip(env / (env.max() * 0.25 + 1e-6), 0, 1)
    t = np.arange(n)
    fade = np.minimum(1, t / (0.3 * SR)) * np.minimum(1, (n - t) / (0.8 * SR))
    return np.tanh((vok + sfx + mz * duck * fade) * 1.05) * 0.95


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("projek")
    ap.add_argument("--pratonton", action="store_true")
    ap.add_argument("--fps", type=int, default=30)
    arg = ap.parse_args()

    folder = Path(arg.projek).resolve()
    cfg = json.loads((folder / "skrip.json").read_text())
    cfg.setdefault("suara", "ms-MY-OsmanNeural")
    W, H = (540, 960) if arg.pratonton else (1080, 1920)
    FPS = 24 if arg.pratonton else arg.fps
    keluar = folder / "keluaran"; keluar.mkdir(exist_ok=True)
    cache = folder / ".cache"; cache.mkdir(exist_ok=True)

    print(f"🎙  Suara ({cfg.get('enjin_suara', 'edge')})...")
    vokal, babak, caps = suara.jana(cfg, folder, cache)
    jumlah = max(len(vokal) / SR, babak[-1]["mula"] + babak[-1]["dur"]) + 0.3
    print(f"   {len(babak)} babak, {jumlah:.1f} saat, {len(caps)} caption")

    camp = campur_audio(vokal, babak, cfg, folder, jumlah)
    wav = cache / "campur.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((camp * 32767).astype(np.int16).tobytes())

    print("✂️  Potong produk & bina set...")
    pentas = Pentas(W, H, cfg, folder, cache)

    out = keluar / ("pratonton.mp4" if arg.pratonton else "video.mp4")
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", str(wav), "-c:v", "libx264",
                           "-preset", "veryfast" if arg.pratonton else "medium", "-crf", "19",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
                           "-movflags", "+faststart", str(out)], stdin=subprocess.PIPE)
    # sambung caption: tunjuk sampai caption seterusnya mula (maks +0.35s)
    for i, c in enumerate(caps):
        nxt = caps[i + 1]["t"] if i + 1 < len(caps) else c["t"] + c["d"] + 0.5
        c["tamat"] = min(nxt, c["t"] + c["d"] + 0.35)
    cap_cache, ci = {}, 0
    nf = int(jumlah * FPS)
    print(f"🎬 Render {nf} frame ({W}x{H})...")
    for f in range(nf):
        tm = f / FPS
        bi = max([i for i, b in enumerate(babak) if b["mula"] <= tm + 1e-6] or [0])
        b = babak[bi]; lt = tm - b["mula"]
        fr = pentas.lukis(b, lt, b["dur"], tm)
        lukis_overlay(fr, b, lt, b["dur"], cfg)
        while ci < len(caps) - 1 and caps[ci]["tamat"] <= tm: ci += 1
        c = caps[ci] if caps and caps[ci]["t"] - 0.03 <= tm < caps[ci]["tamat"] else None
        lukis_caption(fr, c, tm - c["t"] if c else 0, cap_cache)
        ImageDraw.Draw(fr).rectangle((0, 0, int(W * tm / jumlah), int(8 * W / 1080)), fill=KUNING)
        if bi > 0 and lt < 0.08:
            fr.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(110 * (1 - lt / 0.08)))))
        ff.stdin.write(fr.convert("RGB").tobytes())
        if f % (FPS * 5) == 0: print(f"   {tm:5.1f}s / {jumlah:.1f}s", flush=True)
    ff.stdin.close(); ff.wait()

    bersih = lambda s: re.sub(r"\[([^\]|]+)\|[^\]]+\]", r"\1", s).replace("*", "")
    (keluar / "skrip_teleprompter.txt").write_text(
        f"{cfg.get('nama_produk', '')}\n\n" + "\n\n".join(
            f"[{i + 1}] {b.get('peranan', '')} ({b.get('gaya', 'santai')})\n{bersih(b['teks'])}"
            for i, b in enumerate(cfg["babak"])) + "\n")
    if cfg.get("caption_tiktok"):
        (keluar / "caption_tiktok.txt").write_text(cfg["caption_tiktok"] + "\n")
    print(f"✅ Siap: {out}")


if __name__ == "__main__":
    main()
