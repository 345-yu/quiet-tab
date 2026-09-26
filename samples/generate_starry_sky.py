"""Generate samples/starry-sky.jpg: an original, procedural starry-sky wallpaper (CC0).

Run:  uv run --with numpy --with scipy --with pillow python generate_starry_sky.py
Same seed -> same image. Design notes: starry-sky.md
"""
import os

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, zoom
from scipy.spatial import cKDTree

W, H = 3840, 2160
SEED = 20260926
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "starry-sky.jpg")

rng = np.random.default_rng(SEED)


def fractal_noise(h, w, beta):
    """1/f^beta noise via FFT, normalised to 0..1."""
    white = rng.standard_normal((h, w)).astype(np.float32)
    spec = np.fft.rfft2(white)
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.rfftfreq(w)[None, :]
    f = np.sqrt(fx * fx + fy * fy)
    f[0, 0] = 1.0
    spec *= f ** (-beta / 2.0)
    spec[0, 0] = 0.0
    n = np.fft.irfft2(spec, s=(h, w)).astype(np.float32)
    n -= n.min()
    return n / n.max()


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


# ---------------- nebula & galactic band (half resolution, smooth) ----------------
h2, w2 = H // 2, W // 2
yy, xx = np.mgrid[0:h2, 0:w2].astype(np.float32)
u, v = xx / w2, yy / h2                                   # 0..1 across the frame

# band spine: quadratic Bezier arcing over the upper third, leaving the centre dark
t = np.linspace(0.0, 1.0, 1500)[:, None]
p0, p1, p2 = np.array([-0.08, 0.16]), np.array([0.48, -0.02]), np.array([1.08, 0.58])
spine = (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2
spine_px = spine * [w2, h2]
dist, idx = cKDTree(spine_px).query(np.stack([xx.ravel(), yy.ravel()], axis=1))
dist = (dist.reshape(h2, w2) / h2).astype(np.float32)   # in screen heights
along = (idx.reshape(h2, w2) / (len(spine_px) - 1)).astype(np.float32)   # 0..1 along the band

n_edge = fractal_noise(h2, w2, 2.6)
n_body = fractal_noise(h2, w2, 2.2)
n_hue = fractal_noise(h2, w2, 3.0)
n_dust = fractal_noise(h2, w2, 1.9)
n_grain = fractal_noise(h2, w2, 1.2)
n_warp = fractal_noise(h2, w2, 3.2)

# break the geometric arc: low-frequency warp of the distance field
dist = np.abs(dist + (n_warp - 0.5) * 0.07)

# brightness along the band: strongest in the upper right, fading at both ends
profile = np.exp(-((along - 0.66) / 0.30) ** 2) * 0.85 + 0.15

core = np.exp(-(dist / (0.055 * (0.6 + 0.8 * n_edge))) ** 2)
halo = np.exp(-(dist / 0.20) ** 2) * 0.28
band = (core * (0.55 + 0.6 * n_body) + halo) * profile

# dust lanes: soft, fine ridged filaments inside the core only
ridge = 1.0 - np.abs(2.0 * n_dust - 1.0)
lanes = gaussian_filter(smoothstep(0.62, 0.92, ridge), 1.5) * core
band *= 1.0 - 0.7 * lanes

# unresolved star cloud: fine granular light inside the band
cloud = band * n_grain ** 3 * 0.9

# counterweight glow, lower-left, very faint
glow = np.exp(-(((u - 0.08) / 0.30) ** 2 + ((v - 0.92) / 0.28) ** 2)) * (0.35 + 0.65 * n_body)

# keep the centre calm: attenuate everything near the middle of the frame
centre = np.sqrt(((u - 0.5) / 0.55) ** 2 + ((v - 0.52) / 0.5) ** 2)
calm = 0.35 + 0.65 * smoothstep(0.15, 0.95, centre)

indigo = np.array([0.20, 0.22, 0.62], np.float32)
violet = np.array([0.42, 0.24, 0.66], np.float32)
magenta = np.array([0.62, 0.26, 0.55], np.float32)
teal = np.array([0.14, 0.42, 0.52], np.float32)

hue = n_hue[..., None]
band_col = indigo * (1 - hue) + violet * hue
# warm magenta breathes through the densest light near the bright segment
warm = (smoothstep(0.45, 0.95, core * profile) * (0.6 + 0.4 * n_body))[..., None] * 0.55
band_col = band_col * (1 - warm) + magenta * warm
# cold teal whisper where the band thins into its halo
thin = (smoothstep(0.02, 0.10, halo * profile) * (1 - smoothstep(0.2, 0.6, core)))[..., None]
band_col = band_col * (1 - 0.45 * thin) + teal * (0.45 * thin)

sky_top = np.array([0.012, 0.014, 0.040], np.float32)
sky_bot = np.array([0.020, 0.016, 0.050], np.float32)
sky = sky_top * (1 - v[..., None]) + sky_bot * v[..., None]

neb = (band[..., None] * band_col * 0.75 + cloud[..., None] * np.array([0.75, 0.72, 0.95]) * 0.35
       + glow[..., None] * violet * 0.16) * calm[..., None]
img_half = sky + neb
img = zoom(img_half, (2, 2, 1), order=3).astype(np.float32)
band_full = zoom(band * calm, 2, order=1)

# ---------------- stars (full resolution) ----------------
def sample_positions(density, n):
    """Rejection-sample n pixel positions proportional to density."""
    pts = []
    dmax = density.max()
    while sum(len(p) for p in pts) < n:
        x = rng.uniform(0, W, n)
        y = rng.uniform(0, H, n)
        keep = rng.uniform(0, dmax, n) < density[y.astype(int), x.astype(int)]
        pts.append(np.stack([x[keep], y[keep]], axis=1))
    return np.concatenate(pts)[:n]


density = 0.35 + 2.8 * band_full
stars_pos = sample_positions(density, 40000)
mag = rng.pareto(2.1, len(stars_pos)) + 1.0            # many faint, few bright
bright = np.clip(0.07 * mag ** 1.5, 0, 1.4).astype(np.float32)

palette = np.array([[0.72, 0.82, 1.00], [0.92, 0.95, 1.00], [1.00, 0.97, 0.92],
                    [1.00, 0.88, 0.74], [1.00, 0.78, 0.62]], np.float32)
colour = palette[rng.choice(5, len(stars_pos), p=[0.25, 0.35, 0.22, 0.12, 0.06])]

layer = np.zeros((H, W, 3), np.float32)
xi = np.clip(stars_pos[:, 0].astype(int), 0, W - 1)
yi = np.clip(stars_pos[:, 1].astype(int), 0, H - 1)
np.add.at(layer, (yi, xi), colour * bright[:, None])
stars = np.stack([gaussian_filter(layer[..., c], 0.75) for c in range(3)], axis=-1) * 2.2

# a few anchor stars: soft halo + faint diffraction, kept away from the centre
anchors = [(0.11, 0.18, 1.00), (0.83, 0.12, 0.85), (0.93, 0.74, 0.70), (0.27, 0.83, 0.60),
           (0.64, 0.08, 0.55), (0.05, 0.55, 0.45)]
ay, ax = np.mgrid[0:H, 0:W].astype(np.float32)
for fx, fy, s in anchors:
    cx, cy = fx * W, fy * H
    col = palette[rng.choice(3)]
    r2 = (ax - cx) ** 2 + (ay - cy) ** 2
    core = np.exp(-r2 / (2 * 2.2 ** 2)) * 1.6
    halo = np.exp(-r2 / (2 * 16.0 ** 2)) * 0.10
    spike = (np.exp(-((ay - cy) ** 2) / (2 * 0.8 ** 2)) * np.exp(-np.abs(ax - cx) / 38.0)
             + np.exp(-((ax - cx) ** 2) / (2 * 0.8 ** 2)) * np.exp(-np.abs(ay - cy) / 38.0)) * 0.07
    stars += (core + halo + spike)[..., None] * col * s

img += stars

# ---------------- finishing ----------------
vig = 1.0 - 0.28 * smoothstep(0.55, 1.25, np.sqrt(((ax / W - 0.5) / 0.5) ** 2 + ((ay / H - 0.5) / 0.5) ** 2))
img *= vig[..., None]
img = 1.0 - np.exp(-img * 1.75)                          # exposure + soft highlight roll-off
img = np.clip(img, 0, 1) ** (1 / 1.08)
img += rng.normal(0, 0.6 / 255, img.shape).astype(np.float32)   # fine grain, prevents banding
out = (np.clip(img, 0, 1) * 255 + rng.uniform(0, 1, img.shape)).astype(np.uint8)

Image.fromarray(out, "RGB").save(OUT, quality=93, subsampling=0, optimize=True)
print("wrote", OUT)
