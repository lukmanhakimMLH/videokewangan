"""Audio: muzik beat & SFX dijana sendiri (bebas hak cipta)."""
import numpy as np
SR = 44100

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

