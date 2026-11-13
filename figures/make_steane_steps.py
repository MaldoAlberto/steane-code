"""Beginner figure "Steane code, step by step": six visual steps, minimal text, footer with the code link.
Blue = beginner category. Step 6 data: ~/steane-code/steane.json from ~/steane-code/steane_sim.py
(stim, depolarizing noise on each qubit, perfect checks, lookup decoder).
Code: A. M. Steane, Phys. Rev. Lett. 77, 793 (1996).
Usage: python3 make_steane_steps.py <output folder>  (in the steane-code repo: python3 figures/make_steane_steps.py out)
"""
import json, pathlib, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Polygon
from PIL import Image

OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "out").resolve()
OUT.mkdir(parents=True, exist_ok=True)
MASCOT = pathlib.Path.home() / "Downloads/QalyCat_character/qaly_happy.png"
# steane.json: next to the repo copy (figures/ -> repo root), else the local ~/steane-code checkout
DATA = pathlib.Path(__file__).resolve().parents[1] / "steane.json"
if not DATA.exists():
    DATA = pathlib.Path.home() / "steane-code/steane.json"
S = json.loads(DATA.read_text())

INK, MUTED = "#13203A", "#5B6475"
TEAL, CORAL, GRAY, GREEN = "#0A9396", "#C94A45", "#B7BDC8", "#1F6FB2"  # blue fix: safe next to red
BG = "#EAF1FA"  # blue = beginner category
FACE_COL = {4: "#9FD8D3", 2: "#F3D29B", 1: "#C9C3EA"}

plt.rcParams.update({"font.family": ["Helvetica Neue", "DejaVu Sans"], "font.size": 10, "text.color": INK,
                     "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.facecolor": BG,
                     "xtick.labelsize": 9.5, "ytick.labelsize": 9.5, "axes.labelsize": 10})

POS = {4: (0.5, 0.866), 2: (0.0, 0.0), 1: (1.0, 0.0), 6: (0.25, 0.433), 5: (0.75, 0.433), 3: (0.5, 0.0),
       7: (0.5, 0.289)}
FACES = {4: [4, 6, 7, 5], 2: [2, 3, 7, 6], 1: [1, 5, 7, 3]}
for bit, qs in FACES.items():                       # the drawing must match the simulated code
    assert sorted(qs) == S["checks"][{4: 0, 2: 1, 1: 2}[bit]]


def triangle(ax, tiles=True, error=None, lit=False, fixed=None, labels=True):
    on = {b for b, qs in FACES.items() if error in qs} if lit else set()
    for b, qs in FACES.items():
        fc = CORAL if b in on else (FACE_COL[b] if tiles else "#DCE5F2")
        ax.add_patch(Polygon([POS[q] for q in qs], closed=True, fc=fc, alpha=0.6 if b in on else 0.95,
                             ec="white", lw=2.5, zorder=1))
        if tiles and labels:
            cx, cy = np.mean([POS[q] for q in qs], axis=0)
            cx, cy = 0.5 + (cx - 0.5) * 1.12, 0.289 + (cy - 0.289) * 1.12
            ax.text(cx, cy, f"+{b}", ha="center", va="center", fontsize=10, fontweight="bold",
                    color="white" if b in on else INK, zorder=4,
                    bbox=dict(boxstyle="round,pad=0.2", fc=CORAL if b in on else "white", ec="none"))
    for q, (x, y) in POS.items():
        c, t = INK, str(q)
        if q == error:
            c, t = CORAL, "×"
        if q == fixed:
            c, t = GREEN, "✓"
        ax.scatter(x, y, s=330, color=c, zorder=3, edgecolor="white", lw=1.8)
        ax.text(x, y, t, ha="center", va="center", color="white", fontsize=10, fontweight="bold", zorder=5)
    ax.set_xlim(-0.15, 1.15); ax.set_ylim(-0.15, 1.0); ax.set_aspect("equal"); ax.axis("off")


def step1(ax):
    ax.scatter(0.0, 0.43, s=900, color=TEAL, zorder=3)
    ax.text(0.0, 0.43, "ψ", ha="center", va="center", color="white", fontsize=17, fontweight="bold")
    ax.add_patch(FancyArrowPatch((0.25, 0.43), (0.62, 0.43), arrowstyle="-|>", mutation_scale=22, color=MUTED, lw=2))
    sub = ax.inset_axes([0.42, 0.0, 0.6, 1.0])
    triangle(sub, tiles=False)
    ax.set_xlim(-0.25, 1.5); ax.set_ylim(-0.1, 1.0); ax.axis("off")


def step6(ax):
    p = np.array([r["p"] for r in S["rows"]]); pl = np.array([r["p_logical"] for r in S["rows"]])
    be = S["break_even"]
    ax.axvspan(1.5e-3, be, color=TEAL, alpha=0.10, lw=0)
    ax.axvspan(be, 0.4, color=CORAL, alpha=0.10, lw=0)
    ax.text(0.0045, 0.35, "code helps", color=TEAL, fontsize=9, ha="center", fontweight="bold")
    ax.text(np.sqrt(be * 0.4), 2.2e-4, "code\nhurts", color=CORAL, fontsize=8.5, ha="center", linespacing=1.1)
    ax.loglog(p, p, color=GRAY, lw=2, ls="--")
    ax.loglog(p, pl, "o-", color=TEAL, lw=2.4, ms=5)
    ax.text(0.0018, 0.025, "without code", color=MUTED, fontsize=9.5)
    ax.text(0.011, 5e-4, "with Steane", color=TEAL, fontsize=9.5, fontweight="bold")
    ax.set_xlim(1.5e-3, 0.4); ax.set_ylim(3e-5, 0.8)
    ax.set_xticks([2e-3, 1e-2, 1e-1], ["0.2 %", "1 %", "10 %"]); ax.minorticks_off()
    ax.set_yticks([1e-4, 1e-3, 1e-2, 1e-1], ["0.01 %", "0.1 %", "1 %", "10 %"])
    ax.set_xlabel("noise (checks assumed perfect)"); ax.set_ylabel("failures")


STEPS = [
    ("Spread 1 qubit over 7", step1),
    ("Group them in 3 tiles of 4", lambda ax: triangle(ax)),
    ("An error hits qubit 5", lambda ax: triangle(ax, error=5)),
    ("Tiles +4 and +1 light up", lambda ax: triangle(ax, error=5, lit=True)),
    ("4 + 1 = 5: fix qubit 5", lambda ax: triangle(ax, fixed=5)),
    ("Fewer failures (simulated)", step6),
]


def render(footer, name):
    fig = plt.figure(figsize=(7.2, 9.0), dpi=300, facecolor=BG)
    fig.text(0.06, 0.955, "Steane code,\nstep by step", fontsize=24, fontweight="bold", va="top", linespacing=1.1)
    if MASCOT.exists():
        w = 0.13
        cax = fig.add_axes([0.82, 0.855, w, w * (396 / 439) * (7.2 / 9.0)])
        cax.imshow(np.asarray(Image.open(MASCOT))); cax.axis("off")
    fig.text(0.80, 0.915, "Ask, don't look!", fontsize=10, ha="right", va="center", color=INK,
             bbox=dict(boxstyle="round,pad=0.45,rounding_size=0.9", fc="white", ec=TEAL, lw=1.5))

    col_x = [0.06, 0.54]
    row_y = [0.835, 0.555, 0.28]                       # top of each row
    for i, (cap, draw) in enumerate(STEPS):
        x0, y0 = col_x[i % 2], row_y[i // 2]
        fig.text(x0, y0, str(i + 1), fontsize=13, fontweight="bold", color="white", va="top", ha="left",
                 bbox=dict(boxstyle="circle,pad=0.35", fc=TEAL, ec="none"))
        fig.text(x0 + 0.055, y0 - 0.004, cap, fontsize=12, fontweight="bold", va="top")
        if i == 5:
            ax = fig.add_axes([x0 + 0.09, y0 - 0.205, 0.31, 0.16])
        else:
            ax = fig.add_axes([x0, y0 - 0.25, 0.42, 0.215])
        draw(ax)
    fig.text(0.06, 0.015, footer, fontsize=10.5, color=MUTED)
    fig.text(0.95, 0.015, "@qalycat", fontsize=10.5, color=MUTED, ha="right")
    png = OUT / f"{name}.png"
    fig.savefig(png, facecolor=BG); plt.close(fig)
    Image.open(png).convert("RGB").resize((1080, 1350), Image.LANCZOS).save(OUT / f"{name}.jpg", quality=92)
    return png


print(render("Code: link in bio", "steane-steps-en-instagram"))
print(render("Code: github.com/MaldoAlberto/steane-code", "steane-steps-en-linkedin"))
