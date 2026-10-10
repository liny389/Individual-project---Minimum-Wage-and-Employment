"""Replicate Figure 1: distribution of starting wages in NJ and PA.

Figure 1 shows the distribution of starting wages before the increase
(February 1992) and after (November 1992), separately for NJ and PA. In wave 1
the two states' distributions look alike; by wave 2 nearly all NJ stores that
had been below $5.05 report the new $5.05 rate (a mass point at 5.05).

Two panels (before / after) share a y-axis (share of stores). Within each
5-cent wage bin, New Jersey and Pennsylvania are plotted side by side so the
overlap stays legible. Colors are the first two slots of the colorblind-safe
categorical palette (NJ blue #2a78d6, PA orange #eb6834).

Output: output/figures/figure1.png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import matplotlib  # noqa: E402

matplotlib.use("Agg")  # headless backend (no display needed)
import matplotlib.pyplot as plt  # noqa: E402

from config import ANALYSIS_SAMPLE, FIGURES_DIR  # noqa: E402

# Colorblind-safe categorical slots (validated default palette).
NJ_BLUE = "#2a78d6"
PA_ORANGE = "#eb6834"

# Ink / chrome (light surface).
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"

BIN_CENTS = 5  # 5-cent wage bins (so $5.05 gets its own bar)


def _cents(wages: pd.Series) -> np.ndarray:
    """Wages rounded to whole cents (avoids float edge-mismatch in binning)."""
    return (wages * 100).round().astype(int)


def _bin_edges(all_wages: pd.Series) -> np.ndarray:
    """5-cent bin edges (in dollars) covering every observed wage."""
    cents = _cents(all_wages)
    cmin = (cents.min() // BIN_CENTS) * BIN_CENTS
    cmax = ((cents.max() + BIN_CENTS - 1) // BIN_CENTS) * BIN_CENTS
    return np.arange(cmin, cmax + BIN_CENTS, BIN_CENTS) / 100.0


def _frac(wages: pd.Series, edges: np.ndarray) -> np.ndarray:
    """Share of stores in each bin."""
    cents = _cents(wages)
    counts, _ = np.histogram(cents, bins=(edges * 100).round().astype(int))
    return counts / len(cents)


def run() -> None:
    df = pd.read_csv(ANALYSIS_SAMPLE)
    nj = df[df.STATE == 1]
    pa = df[df.STATE == 0]

    w1_nj, w1_pa = nj.WAGE_ST.dropna(), pa.WAGE_ST.dropna()
    w2_nj, w2_pa = nj.WAGE_ST2.dropna(), pa.WAGE_ST2.dropna()

    all_w = pd.concat([w1_nj, w1_pa, w2_nj, w2_pa])
    edges = _bin_edges(all_w)
    x = edges[:-1]

    bin_w = BIN_CENTS / 100.0
    bar_w = bin_w * 0.42        # thin bars
    gap = bin_w - 2 * bar_w     # 2px-style surface gap between NJ and PA
    nj_x = x
    pa_x = x + bar_w + gap

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4), sharey=True)

    panels = [
        ("February 1992 (before)", w1_nj, w1_pa),
        ("November 1992 (after)", w2_nj, w2_pa),
    ]

    for ax, (title, wn, wp) in zip(axes, panels):
        ax.bar(nj_x, _frac(wn, edges), width=bar_w, color=NJ_BLUE,
               label="New Jersey", edgecolor="none")
        ax.bar(pa_x, _frac(wp, edges), width=bar_w, color=PA_ORANGE,
               label="Pennsylvania", edgecolor="none")

        ax.set_title(title, fontsize=12, color=INK_PRIMARY, pad=8)
        ax.set_xlabel("Starting wage ($)", fontsize=10, color=INK_SECONDARY)
        ax.tick_params(axis="both", colors=INK_MUTED, labelsize=9)
        ax.grid(axis="y", color=GRIDLINE, linewidth=0.8)
        ax.set_axisbelow(True)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        for spine in ("left", "bottom"):
            ax.spines[spine].set_color("#c3c2b7")

    axes[0].set_ylabel("Fraction of stores", fontsize=10, color=INK_SECONDARY)

    # Annotate the NJ mass point at $5.05 in the after panel.
    axes[1].annotate(
        "NJ mass point at $5.05",
        xy=(5.05, _frac(w2_nj, edges)[np.where(x == 5.05)[0][0]]),
        xytext=(5.28, 0.52), fontsize=9, color=INK_SECONDARY,
        arrowprops=dict(arrowstyle="->", color=INK_MUTED, lw=0.9),
    )

    axes[0].legend(frameon=False, fontsize=10, loc="upper right")

    fig.tight_layout()
    out = FIGURES_DIR / "figure1.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)

    n_nj1, n_pa1 = len(w1_nj), len(w1_pa)
    n_nj2, n_pa2 = len(w2_nj), len(w2_pa)
    print(f"Figure 1 — starting-wage distributions")
    print(f"  Wave 1: NJ {n_nj1} stores, PA {n_pa1} stores")
    print(f"  Wave 2: NJ {n_nj2} stores, PA {n_pa2} stores")
    print(f"  NJ wave-2 share at $5.05 = "
          f"{_frac(w2_nj, edges)[np.where(x == 5.05)[0][0]] * 100:.1f}%")
    print(f"Wrote {out}")


if __name__ == "__main__":
    run()
