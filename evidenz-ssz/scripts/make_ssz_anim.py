import math
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from typing import List

import site

USER_SITE = Path.home() / "AppData" / "Roaming" / "Python" / "Python310" / "site-packages"
if USER_SITE.exists():
    site.addsitedir(str(USER_SITE))

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.patches import FancyBboxPatch
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from PIL import Image

W, H = 1920, 1080
DPI = 200
SAFE_L = 0.05
SAFE_TB = 0.06
BG = "#050505"
FG = "#f4f6ff"
ACC1, ACC2, ACC3 = "#2ec4f3", "#ffb347", "#89cff0"

TITLE = "Von der Singularität zur Segmentierung — zwei Anfänge des Universums"
LEFT_BULLETS = [
    "Klassisches ΛCDM-Modell",
    "Ursprung als Singularität (∞-Dichte)",
    "„Explosion“ erzeugt Raum, Zeit, Materie",
    "Temperatur fällt mit Expansion",
]
RIGHT_BULLETS = [
    "Segmentierte Raumzeit (SSZ)",
    "Geordnete Ursprungsschicht, keine Singularität",
    "Raum entsteht durch Segmentierung",
    "Expansion = Entfaltung, Resonanz-getrieben",
]
VOICE_LINES = [
    "Links das klassische Bild: ein Universum aus einer unendlichen Singularität geboren.",
    "Rechts die segmentierte Raumzeit: kein Punkt, sondern eine geordnete Ursprungsschicht.",
    "Statt Explosion entsteht Raum durch Segmentierung – Expansion heißt Entfaltung.",
    "Die SSZ erklärt Stabilität ohne unendliche Dichte – ein strukturierter Anfang.",
]

FPS = 30
DUR = 25.0
N = int(DUR * FPS)


def auto_font(ax: plt.Axes, text: str, max_px: float, min_pt: int = 16, max_pt: int = 42, weight: str = "normal") -> int:
    renderer = ax.figure.canvas.get_renderer()
    for pt in range(max_pt, min_pt - 1, -1):
        txt = ax.text(0, 0, text, fontsize=pt, color=FG, weight=weight, family="DejaVu Sans", transform=ax.transAxes)
        bb = txt.get_window_extent(renderer=renderer)
        txt.remove()
        if bb.width <= max_px:
            return pt
    return min_pt


def draw_text_box(ax: plt.Axes, x: float, y: float, w: float, h: float, lines: List[str], title: bool = False) -> None:
    pad = 0.012
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=12", facecolor=(0, 0, 0, 0.28), edgecolor=(1, 1, 1, 0.08), linewidth=1)
    ax.add_patch(box)
    inner_w = (w - 2 * pad) * W
    cursor_y = y + h - pad
    renderer = ax.figure.canvas.get_renderer()
    for i, line in enumerate(lines):
        pt = auto_font(ax, line, inner_w, min_pt=14, max_pt=36, weight="bold" if (title and i == 0) else "normal")
        txt = ax.text(x + pad, cursor_y - 0.04, line, fontsize=pt, color=FG, transform=ax.transAxes, va="top", ha="left", family="DejaVu Sans")
        bb = txt.get_window_extent(renderer=renderer)
        cursor_y -= (bb.height / W) + 0.012


def spiral(t: float, a: float = 2.0, b: float = 0.12, turns: float = 2.0) -> tuple[float, float]:
    ang = turns * 2 * math.pi * t
    r = a * math.exp(b * ang)
    return r * math.cos(ang), r * math.sin(ang)


fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI)
fig.patch.set_facecolor(BG)
gs = fig.add_gridspec(1, 2, left=SAFE_L, right=1 - SAFE_L, top=1 - SAFE_TB, bottom=SAFE_TB, wspace=0.05)
axL = fig.add_subplot(gs[0, 0])
axR = fig.add_subplot(gs[0, 1])
for ax in (axL, axR):
    ax.set_axis_off()
    ax.set_facecolor(BG)

title_ax = fig.add_axes([SAFE_L, 1 - SAFE_TB * 0.9, 1 - 2 * SAFE_L, 0.06], frameon=False)
title_ax.set_axis_off()
title_ax.text(0.5, 0.5, TITLE, ha="center", va="center", color=FG, fontsize=38, family="DejaVu Sans", weight="bold")

rng = np.random.default_rng(7)
stars = rng.uniform(-1, 1, (900, 2))
radii = np.linspace(0.04, 0.9, 13)
hex_bg = np.linspace(0, 1, 10)


def draw_frame(i: int) -> None:
    t = i / (N - 1)
    axL.clear()
    axR.clear()
    axL.set_axis_off()
    axR.set_axis_off()
    axL.set_facecolor(BG)
    axR.set_facecolor(BG)
    for k, r in enumerate(radii):
        phase = 0.5 * np.sin(2 * np.pi * (t * 0.6) + k * 0.35)
        rr = r * (1 + 0.02 * phase)
        circ = plt.Circle((0.5, 0.5), rr, transform=axL.transAxes, edgecolor=(1, 1, 1, 0.1), facecolor="none", lw=2)
        axL.add_patch(circ)
    glow = plt.Circle((0.5, 0.5), 0.06 + 0.08 * np.exp(-6 * (1 - t)), transform=axL.transAxes, color=ACC3, alpha=0.85)
    axL.add_patch(glow)
    pxy = 0.5 + 0.45 * stars * (0.4 + 0.6 * t)
    axL.scatter(pxy[:, 0], pxy[:, 1], s=3, c=(1, 1, 1, 0.22), transform=axL.transAxes)
    draw_text_box(axL, 0.06, 0.53, 0.40, 0.40, LEFT_BULLETS, title=True)
    for h in range(len(hex_bg)):
        axR.add_patch(plt.Rectangle((0.05 * h, 0.05 * h), 1 - 0.1 * h, 1 - 0.1 * h, transform=axR.transAxes, facecolor=(0.18, 0.28, 0.45, 0.07), edgecolor="none"))
    turns = 2.6
    S = int(500 * t) + 10
    xs, ys = [], []
    for s in range(S):
        tt = s / max(1, S - 1)
        x, y = spiral(tt, a=0.02 + 0.08 * t, b=0.13, turns=turns)
        xs.append(0.5 + x)
        ys.append(0.5 + y)
    axR.plot(xs, ys, lw=3, color=ACC2, alpha=0.9, transform=axR.transAxes)
    M = 200
    ang = rng.uniform(0, 2 * np.pi, M)
    rad = (0.03 + 0.10 * t) * np.sqrt(rng.uniform(0, 1, M))
    px = 0.5 + rad * np.cos(ang)
    py = 0.5 + rad * np.sin(ang)
    axR.scatter(px, py, s=6, c=ACC1, alpha=0.75, transform=axR.transAxes)
    draw_text_box(axR, 0.54, 0.53, 0.40, 0.40, RIGHT_BULLETS, title=True)
    sub_ax = fig.add_axes([SAFE_L, SAFE_TB * 0.25, 1 - 2 * SAFE_L, 0.05], frameon=False)
    sub_ax.set_axis_off()
    msg = "Nicht ein Knall, sondern ein Beginn der Ordnung — SSZ-Modell"
    sub_ax.text(0.5, 0.5, msg, ha="center", va="center", color=(1, 1, 1, 0.7), fontsize=20, family="DejaVu Sans")


frames_dir = tempfile.mkdtemp(prefix="ssz_frames_")
for i in range(N):
    draw_frame(i)
    fig.savefig(os.path.join(frames_dir, f"f_{i:05d}.png"), dpi=DPI, facecolor=BG)
plt.close(fig)

wav_path = "voice.wav"


def tts_locally() -> bool:
    try:
        import pyttsx3

        engine = pyttsx3.init()
        engine.setProperty("rate", 168)
        engine.save_to_file(". ".join(VOICE_LINES), wav_path)
        engine.runAndWait()
        return Path(wav_path).exists()
    except Exception:
        return False


if not tts_locally():
    if shutil.which("espeak"):
        txt = ". ".join(VOICE_LINES)
        with open(wav_path, "wb") as fh:
            subprocess.run(["espeak", "-s", "165", "-ven+f3", txt, "--stdout"], stdout=fh, check=True)
    else:
        sr = 44100
        samples = np.zeros(int(sr * (DUR + 1)), dtype=np.int16)
        try:
            from scipy.io.wavfile import write as wavwrite
        except ImportError:
            raise SystemExit("scipy required for silent fallback: pip install scipy")
        wavwrite(wav_path, sr, samples)

frame_files = sorted(Path(frames_dir).glob("f_*.png"))
clip = ImageSequenceClip([str(p) for p in frame_files], fps=FPS)
if Path(wav_path).exists():
    audio = AudioFileClip(wav_path).volumex(0.9)
    clip = clip.set_audio(audio)
clip.write_videofile("ssz_vs_bigbang.mp4", fps=FPS, codec="libx264", audio_codec="aac", bitrate="8M")

try:
    clip.write_gif("ssz_vs_bigbang.gif", fps=20, program="ffmpeg")
except Exception:
    pass

print("Finished rendering")
print("MP4: ssz_vs_bigbang.mp4")
print("GIF : ssz_vs_bigbang.gif (if generated)")
print(f"Frames saved in: {frames_dir}")
