"""Re-matte the speaker with MediaPipe's multiclass selfie segmenter.

The generic matting model kept the dark car headliner and headrest as
foreground in this night-time clip. The selfie segmenter knows what a
person is, so it is used as the alpha, with three fixes:
  - the bottom of the frame (the shirt) is forced opaque, since the
    segmenter leaves holes in large dark clothing,
  - an exponential moving average across frames stops the edge flickering,
  - a small blur feathers the edge so it sits on the blurred studio set.

Usage: python3 -I refine_matte.py <tight.mp4> <model.tflite> <out.webm>
"""

import subprocess
import sys

import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision
from PIL import Image, ImageFilter

W, H = 1080, 1920
SRC, MODEL, OUT = sys.argv[1:4]

seg = vision.ImageSegmenter.create_from_options(
    vision.ImageSegmenterOptions(
        base_options=mpt.BaseOptions(model_asset_path=MODEL),
        output_confidence_masks=True,
    )
)

# Opaque floor for the shirt: 0 above y=1380, ramping to 1 at y=1560.
ramp = np.clip((np.arange(H) - 1380) / 180.0, 0, 1)[:, None].astype(np.float32)

dec = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
    stdout=subprocess.PIPE,
)
enc = subprocess.Popen(
    [
        "ffmpeg", "-v", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
        "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "24",
        "-deadline", "good", "-cpu-used", "5", "-row-mt", "1", "-auto-alt-ref", "0",
        OUT,
    ],
    stdin=subprocess.PIPE,
)

prev = None
n = 0
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3:
        break
    rgb = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    res = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
    person = 1.0 - np.squeeze(res.confidence_masks[0].numpy_view())
    alpha = np.maximum(np.clip(person, 0, 1), ramp)
    alpha = alpha if prev is None else 0.55 * alpha + 0.45 * prev
    prev = alpha
    a8 = Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.5))
    # crush the faint halo, keep the soft edge
    a = np.asarray(a8, np.float32) / 255.0
    a = np.clip((a - 0.12) / 0.76, 0, 1)
    rgba = np.dstack([rgb, (a * 255).astype(np.uint8)])
    enc.stdin.write(rgba.tobytes())
    n += 1
    if n % 300 == 0:
        print(f"{n} frames", flush=True)

enc.stdin.close()
enc.wait()
dec.wait()
seg.close()
print(f"done: {n} frames")
