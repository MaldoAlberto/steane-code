"""Beginner figure "How does the Steane code fix errors?": explainer rows (question, plain body,
takeaway) with a diagram or chart each. Blue = beginner category.
Data: ~/steane-code/steane.json from ~/steane-code/steane_sim.py (stim, code-capacity depolarizing noise,
perfect checks, lookup decoder). Code: A. M. Steane, Phys. Rev. Lett. 77, 793 (1996).
Usage: python3 make_steane_beginner.py <output folder>  (in the steane-code repo: python3 figures/make_steane_beginner.py out)
"""
import json, pathlib, sys, textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
from PIL import Image

OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "out").resolve()
OUT.mkdir(parents=True, exist_ok=True)
MASCOT = pathlib.Path.home() / "Downloads/QalyCat_character/qaly_happy.png"
# steane.json: next to the repo copy (figures/ -> repo root), else the local ~/steane-code checkout
DATA = pathlib.Path(__file__).resolve().parents[1] / "steane.json"
if not DATA.exists():
    DATA = pathlib.Path.home() / "steane-code/steane.json"
S = json.loads(DATA.read_text())
P1 = next(r["p_logical"] for r in S["rows"] if r["p"] == 0.01)       # failure rate at 1 % noise

INK, MUTED = "#13203A", "#5B6475"
TEAL, CORAL, GRAY, SAND = "#0A9396", "#C94A45", "#B7BDC8", "#E0A458"
BG = "#EAF1FA"  # blue = beginner category
FACE_COL = {4: "#9FD8D3", 2: "#F3D29B", 1: "#C9C3EA"}

plt.rcParams.update({"font.family": ["Helvetica Neue", "DejaVu Sans"], "font.size": 10, "text.color": INK,
                     "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.facecolor": BG,
                     "xtick.labelsize": 9, "ytick.labelsize": 9.5, "axes.labelsize": 9.5})

# qubit k sits so that the check labelled 4, 2 or 1 contains exactly the qubits whose number has that bit
POS = {4: (0.5, 0.866), 2: (0.0, 0.0), 1: (1.0, 0.0), 6: (0.25, 0.433), 5: (0.75, 0.433), 3: (0.5, 0.0),
       7: (0.5, 0.289)}
FACES = {4: [4, 6, 7, 5], 2: [2, 3, 7, 6], 1: [1, 5, 7, 3]}
for bit, qs in FACES.items():                       # the drawing must match the code
    assert sorted(qs) == S["checks"][{4: 0, 2: 1, 1: 2}[bit]]

ROWS = [
    {"q": "1  What is the Steane code?",
     "body": "It stores 1 reliable (logical) qubit in 7 noisy qubits. Each colored tile groups "
             "4 qubits and checks them twice: once for bit flips, once for phase flips.",
     "take": "It fixes any single error on any of the 7 qubits: a bit flip, a phase flip, or both."},
    {"q": "2  How does it find the error?",
     "body": "Each check answers one question: did anything change among my 4 qubits? "
             "Give the checks the values 4, 2 and 1 and add up the ones that say yes.",
     "take": "The sum is the number of the broken qubit. Here 4 + 1 = 5, so we fix qubit 5."},
    {"q": "3  Does it actually help?",
     "body": "We simulated it with stim: each qubit gets an error with chance p, "
             "the checks find it, we fix it, and we count failures.",
     "take": f"Failures drop like p²: at 1 % noise, the protected qubit fails only {100 * P1:.2f} % of the time."},
    {"q": "4  Why is it famous?",
     "body": "Key gates (H, S, CNOT) are done qubit by qubit across the 7, so one fault cannot spread "
             "inside a block. The T gate needs an extra trick (a magic state).",
     "take": "Small, complete, easy to draw: the classic first code to learn."},
]


def triangle(ax, error=None):
    lit = {b for b, qs in FACES.items() if error in qs}
    for b, qs in FACES.items():
        on = b in lit
        ax.add_patch(Polygon([POS[q] for q in qs], closed=True, fc=CORAL if on else FACE_COL[b],
                             alpha=0.55 if on else 0.9, ec="white", lw=2, zorder=1))
        cx, cy = np.mean([POS[q] for q in qs], axis=0)
        cx, cy = 0.5 + (cx - 0.5) * 1.12, 0.289 + (cy - 0.289) * 1.12
        ax.text(cx, cy, f"+{b}", ha="center", va="center", fontsize=8.5, fontweight="bold",
                color="white" if on else INK, zorder=4,
                bbox=dict(boxstyle="round,pad=0.18", fc=CORAL if on else "white", ec="none"))
    for q, (x, y) in POS.items():
        bad = q == error
        ax.scatter(x, y, s=210, color=CORAL if bad else INK, zorder=3, edgecolor="white", lw=1.5)
        ax.text(x, y, "×" if bad else str(q), ha="center", va="center", color="white", fontsize=8.5,
                fontweight="bold", zorder=5)
    ax.set_xlim(-0.12, 1.12); ax.set_ylim(-0.12, 0.98); ax.set_aspect("equal"); ax.axis("off")


def row1(ax):
    triangle(ax)
    ax.text(1.18, 0.62, "● noisy qubit\n    (numbered 1–7)", fontsize=8.3, color=INK, va="center",
            transform=ax.transData, linespacing=1.2)
    ax.text(1.18, 0.30, "■ tile = 4 qubits\n    checked together", fontsize=8.3, color=MUTED, va="center",
            transform=ax.transData, linespacing=1.2)
    ax.set_xlim(-0.12, 2.15)


def row2(ax):
    triangle(ax, error=5)
    ax.text(1.18, 0.66, "check +4: yes", fontsize=9, color=CORAL, fontweight="bold", va="center")
    ax.text(1.18, 0.47, "check +2: no", fontsize=9, color=MUTED, va="center")
    ax.text(1.18, 0.28, "check +1: yes", fontsize=9, color=CORAL, fontweight="bold", va="center")
    ax.text(1.18, 0.04, "4 + 1 = qubit 5", fontsize=10, color=INK, fontweight="bold", va="center")
    ax.set_xlim(-0.12, 2.15)


def row3(ax):
    p = np.array([r["p"] for r in S["rows"]]); pl = np.array([r["p_logical"] for r in S["rows"]])
    ax.loglog(p, p, color=GRAY, lw=1.8, ls="--")
    ax.loglog(p, pl, "o-", color=TEAL, lw=2, ms=4.5)
    ax.text(0.0019, 0.011, "bare qubit\n(no code)", color=MUTED, fontsize=8.3, linespacing=1.1)
    ax.text(0.012, 6e-4, "Steane code", color=TEAL, fontsize=8.5, fontweight="bold")
    ax.set_xlim(1.5e-3, 0.4); ax.set_ylim(3e-5, 0.8)
    ax.set_xticks([1e-3 * 2, 1e-2, 1e-1], ["0.2 %", "1 %", "10 %"]); ax.minorticks_off()
    ax.set_yticks([1e-4, 1e-3, 1e-2, 1e-1], ["0.01 %", "0.1 %", "1 %", "10 %"])
    ax.set_xlabel("noise per qubit p"); ax.set_ylabel("failure rate")


def row4(ax):
    for q in range(7):
        ax.plot([q, q], [1.0, 0.0], color=SAND, lw=1.6, zorder=1)
        ax.scatter(q, 1.0, s=90, color=TEAL, zorder=3)                                  # control
        ax.scatter(q, 0.0, s=170, facecolor="white", edgecolor=INK, lw=1.5, zorder=3)   # target
        ax.text(q, 0.0, "+", ha="center", va="center", fontsize=11, color=INK, zorder=4)
    ax.text(-0.6, 1.0, "block A", ha="right", va="center", fontsize=8.5, color=TEAL)
    ax.text(-0.6, 0.0, "block B", ha="right", va="center", fontsize=8.5, color=INK)
    ax.text(3.0, -0.55, "logical CNOT = 7 CNOTs, side by side", ha="center", va="top", fontsize=8.5, color=MUTED)
    ax.set_xlim(-2.2, 6.6); ax.set_ylim(-0.95, 1.4); ax.axis("off")


CHARTS = [row1, row2, row3, row4]
BOXES = [[0.57, 0.69, 0.39, 0.13], [0.57, 0.49, 0.39, 0.13], [0.66, 0.305, 0.27, 0.12],
         [0.58, 0.14, 0.38, 0.09]]


def render(footer, name):
    fig = plt.figure(figsize=(7.2, 9.0), dpi=300, facecolor=BG)
    fig.text(0.06, 0.96, "How does the Steane code\nfix errors?", fontsize=21, fontweight="bold", va="top",
             linespacing=1.15)
    fig.text(0.06, 0.875, "7 qubits, 3 checks, 1 error fixed", fontsize=12, color=MUTED, va="top")
    tops = [0.83, 0.645, 0.45, 0.27]
    for i, r in enumerate(ROWS):
        y0 = tops[i]
        fig.text(0.06, y0, r["q"], fontsize=12.5, fontweight="bold", va="top")
        body = textwrap.fill(r["body"], 46)
        fig.text(0.06, y0 - 0.03, body, fontsize=9.4, color=INK, va="top", linespacing=1.35)
        yt = y0 - 0.03 - 0.0195 * (body.count("\n") + 1) - 0.008
        fig.text(0.06, yt, textwrap.fill(r["take"], 48), fontsize=9.2, color=TEAL, va="top",
                 linespacing=1.3, fontweight="bold")
        CHARTS[i](fig.add_axes(BOXES[i]))

    fig.text(0.06, 0.088, "Ask questions, never look at the data.", fontsize=12, fontweight="bold")
    fig.text(0.06, 0.04,
             "Simulation: stim, each qubit depolarized with chance p, perfect checks, lookup decoder; 400k–2M runs\n"
             "per point. Real checks are noisy too, so the noise level where it starts to help is lower on hardware.\n"
             "Code: A. M. Steane, Phys. Rev. Lett. 77, 793 (1996). The checks come from the classical Hamming code.",
             fontsize=7, color=MUTED, linespacing=1.4)
    if MASCOT.exists():
        w = 0.12
        cax = fig.add_axes([0.83, 0.865, w, w * (396 / 439) * (7.2 / 9.0)])
        cax.imshow(np.asarray(Image.open(MASCOT))); cax.axis("off")
    fig.text(0.81, 0.925, "4 + 1 = 5,\nfound it!", fontsize=9.5, ha="right", va="center", color=INK,
             linespacing=1.3, bbox=dict(boxstyle="round,pad=0.45,rounding_size=0.9", fc="white", ec=TEAL, lw=1.5))
    fig.text(0.06, 0.012, footer, fontsize=10.5, color=MUTED)
    fig.text(0.95, 0.012, "@qalycat", fontsize=10.5, color=MUTED, ha="right")
    png = OUT / f"{name}.png"
    fig.savefig(png, facecolor=BG); plt.close(fig)
    Image.open(png).convert("RGB").resize((1080, 1350), Image.LANCZOS).save(OUT / f"{name}.jpg", quality=92)
    return png


print(render("Code: link in bio", "steane-beginner-en-instagram"))
print(render("Code: github.com/MaldoAlberto/steane-code", "steane-beginner-en-linkedin"))
