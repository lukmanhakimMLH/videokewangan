"""Remove the TikTok watermark by inpainting only its own pixels.

ffmpeg's delogo smears the whole box and leaves vertical streaks over the
shirt print. Instead, the watermark's exact shape is learned from the clip
(pixels that stay bright through each placement period), dilated slightly,
and filled with OpenCV's Telea inpainting on every frame of that period.

Usage: python3 -I inpaint_watermark.py <raw.mov> <clean.mp4>
"""

import subprocess
import sys

import cv2
import numpy as np

SRC, OUT = sys.argv[1:3]
W, H, FPS = 540, 960, 30
SWITCH = 3.5  # seconds: top-left placement before, bottom-right after
BOXES = {"L": (0, 425, 180, 530), "R": (360, 710, 540, 815)}


def frames(extra=()):
    p = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", SRC, *extra, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
        stdout=subprocess.PIPE,
    )
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3:
            break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)
    p.wait()


def learn_mask(t0, t1, box):
    x0, y0, x1, y1 = box
    hits, n = None, 0
    for i, f in enumerate(frames(["-vf", "fps=4"])):
        t = i / 4
        if t < t0 or t >= t1:
            continue
        roi = f[y0:y1, x0:x1].max(axis=2) > 150
        hits = roi.astype(np.int32) if hits is None else hits + roi
        n += 1
    static = (hits / n) > 0.7
    m = np.zeros((H, W), np.uint8)
    m[y0:y1, x0:x1] = static * 255
    return cv2.dilate(m, np.ones((3, 3), np.uint8), iterations=2)


mask_l = learn_mask(0.2, SWITCH - 0.2, BOXES["L"])
mask_r = learn_mask(SWITCH + 0.5, 1e9, BOXES["R"])
print("mask pixels", int((mask_l > 0).sum()), int((mask_r > 0).sum()), flush=True)

enc = subprocess.Popen(
    [
        "ffmpeg", "-v", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", SRC, "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "12", "-pix_fmt", "yuv420p",
        "-c:a", "copy", OUT,
    ],
    stdin=subprocess.PIPE,
)
for i, f in enumerate(frames(["-r", str(FPS)])):
    t = i / FPS
    m = mask_l if t < SWITCH else mask_r
    # the handover frame carries both placements
    if abs(t - SWITCH) < 0.1:
        m = cv2.bitwise_or(mask_l, mask_r)
    enc.stdin.write(cv2.inpaint(f, m, 5, cv2.INPAINT_TELEA).tobytes())
enc.stdin.close()
enc.wait()
print("done", flush=True)
