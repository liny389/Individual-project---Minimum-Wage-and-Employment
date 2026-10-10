"""Independent extension: does the positive DID estimate survive modern inference?

Economic question. The paper's headline result (a ~2.76-FTE relative employment
gain in NJ, t = 2.03) rests on conventional OLS standard errors that ignore
within-group correlation. Neumark & Wascher (2000) later argued the paper's
standard errors were too small. This extension asks: is the result still
statistically credible under (i) cluster-robust standard errors and (ii) an
exact store-level randomization / permutation test?

Two parts:
  1. Cluster-robust SEs for the five Table 4 models, clustering by restaurant
     chain (4 clusters) and by region (6 clusters). Few clusters -> the cluster
     SEs are a rough guide, not a fix (documented in the report).
  2. Randomization inference on the NJ-PA diff-in-diff. Hold each store's
     employment change (dFTE = FTE2 - FTE1) fixed and shuffle the NJ/PA
     treatment label across stores; recompute the DID = mean(dFTE | NJ) -
     mean(dFTE | PA) on each shuffle to build the null distribution. The
     permutation p-value is the share of |placebo DID| >= |observed DID|.

Outputs:
  - output/tables/extension_clustered_se.csv
  - output/tables/extension_permutation.csv
  - output/figures/extension_permutation.png  (null distribution + observed)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import matplotlib  # noqa: E402

matplotlib.use("Agg")  # headless backend
import matplotlib.pyplot as plt  # noqa: E402
from statsmodels.regression.linear_model import OLS  # noqa: E402
from statsmodels.tools import add_constant  # noqa: E402

from config import ANALYSIS_SAMPLE, TABLES_DIR, FIGURES_DIR  # noqa: E402

CHAIN_OWN = ["kfc", "roy_rogers", "wendys", "co_owned"]
REGION = ["nj_central", "nj_south", "pa_ne_philly", "pa_easton"]

# (model label, key regressor, control groups) — mirrors table4.py
SPECS = [
    ("(i)", "STATE", []),
    ("(ii)", "STATE", [CHAIN_OWN]),
    ("(iii)", "gap", []),
    ("(iv)", "gap", [CHAIN_OWN]),
    ("(v)", "gap", [CHAIN_OWN, REGION]),
]

# Palette / ink (validated default).
NJ_BLUE = "#2a78d6"
OBSERVED_COLOR = "#e34948"   # red slot 8, reserved as the "observed" marker
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"

N_PERM = 10_000
SEED = 20240401


def _region_id(df: pd.DataFrame) -> pd.Series:
    """6 region clusters: NJ north(0)/central(1)/south(2); PA other(3)/PA1(4)/PA2(5)."""
    state = df.STATE.to_numpy()
    rid = np.zeros(len(df), dtype=int)
    rid[state == 1] = np.where(
        df.CENTRALJ.to_numpy()[state == 1] == 1, 1,
        np.where(df.SOUTHJ.to_numpy()[state == 1] == 1, 2, 0),
    )
    rid[state == 0] = np.where(
        df.PA1.to_numpy()[state == 0] == 1, 4,
        np.where(df.PA2.to_numpy()[state == 0] == 1, 5, 3),
    )
    return pd.Series(rid, index=df.index)


def _fit(frame: pd.DataFrame, y: pd.Series, cols: list[str]):
    X = frame[cols] if cols else pd.DataFrame(index=frame.index)
    return OLS(y, add_constant(X)).fit()


def _did(dfte: np.ndarray, treat: np.ndarray) -> float:
    """DID = mean(dFTE | NJ) - mean(dFTE | PA)."""
    return float(dfte[treat == 1].mean() - dfte[treat == 0].mean())


def _cluster_se(frame: pd.DataFrame, y: pd.Series, cols: list[str],
                groups: np.ndarray, key: str):
    """OLS with cluster-robust SEs; return (coef, se, n)."""
    res = _fit(frame, y, cols)
    cres = res.get_robustcov_results(cov_type="cluster", groups=groups)
    # get_robustcov_results exposes params/bse as plain arrays -> index by position.
    pos = list(res.params.index).index(key)
    return float(res.params.iloc[pos]), float(np.asarray(cres.bse)[pos]), int(cres.nobs)


def run() -> None:
    df = pd.read_csv(ANALYSIS_SAMPLE)
    df["region_id"] = _region_id(df)

    # --- Part 1: cluster-robust SEs for the Table 4 models -----------------
    # Same balanced sample as Table 4: employment AND starting wage in both waves.
    bal4 = df[df.fte1.notna() & df.fte2.notna()
              & df.WAGE_ST.notna() & df.WAGE_ST2.notna()].copy()
    y4 = bal4["dfte"]

    records = []
    for label, key, control_groups in SPECS:
        cols = [key] + [c for g in control_groups for c in g]

        # Cluster by chain (drop any missing CHAIN codes).
        chain = bal4.dropna(subset=["CHAIN"])
        yc = chain["dfte"]
        coef_c, se_c, n_c = _cluster_se(chain, yc, cols, chain["CHAIN"].to_numpy(), key)

        # Cluster by region (6 clusters, no missing).
        coef_r, se_r, n_r = _cluster_se(bal4, y4, cols, bal4["region_id"].to_numpy(), key)

        # Conventional OLS SE for reference.
        ols_res = _fit(bal4, y4, cols)

        records.append({
            "model": label,
            "regressor": "NJ dummy" if key == "STATE" else "wage gap",
            "coef": float(ols_res.params[key]),
            "se_ols": float(ols_res.bse[key]),
            "se_cluster_chain": se_c,
            "t_cluster_chain": coef_c / se_c,
            "se_cluster_region": se_r,
            "t_cluster_region": coef_r / se_r,
            "n_chain": n_c,
            "n_region": n_r,
        })

    out = pd.DataFrame(records)
    out.to_csv(TABLES_DIR / "extension_clustered_se.csv", index=False)

    # --- Part 2: permutation test of the DID -------------------------------
    # Paired (balanced) sample: stores with an observed employment change.
    bal = df[df.dfte.notna()].copy()
    dfte = bal["dfte"].to_numpy()
    state = bal["STATE"].to_numpy()

    obs = _did(dfte, state)
    rng = np.random.default_rng(SEED)
    null = np.empty(N_PERM)
    for i in range(N_PERM):
        null[i] = _did(dfte, rng.permutation(state))

    p_two = float((np.abs(null) >= np.abs(obs)).mean())
    p_greater = float((null >= obs).mean())
    p_less = float((null <= obs).mean())

    perm = pd.DataFrame([{
        "observed_did": obs,
        "n_stores": int(len(bal)),
        "n_nj": int((state == 1).sum()),
        "n_pa": int((state == 0).sum()),
        "n_permutations": N_PERM,
        "p_value_two_sided": p_two,
        "p_value_greater": p_greater,
        "p_value_less": p_less,
        "null_mean": float(null.mean()),
        "null_sd": float(null.std()),
        "seed": SEED,
    }])
    perm.to_csv(TABLES_DIR / "extension_permutation.csv", index=False)

    # --- Plot: null distribution + observed DID ----------------------------
    fig, ax = plt.subplots(figsize=(8, 4.2))
    counts, edges = np.histogram(null, bins=60)
    width = np.diff(edges)
    ax.bar(edges[:-1], counts, width=width, align="edge",
           color=NJ_BLUE, alpha=0.85, edgecolor="none")

    tail = np.abs(null) >= np.abs(obs)
    tail_counts, _ = np.histogram(null[tail], bins=edges)
    ax.bar(edges[:-1], tail_counts, width=width, align="edge",
           color=OBSERVED_COLOR, alpha=0.9, edgecolor="none")

    ax.axvline(obs, color=OBSERVED_COLOR, linewidth=2)
    ax.axvline(-obs, color=OBSERVED_COLOR, linewidth=2, linestyle="--")

    ax.annotate(
        f"observed DID = {obs:.2f}\np (two-sided) = {p_two:.3f}",
        xy=(obs, 0.0), xycoords="data",
        xytext=(0.02, 0.94), textcoords="axes fraction",
        ha="left", va="top",
        fontsize=10, color=INK_SECONDARY,
        arrowprops=dict(arrowstyle="->", color=INK_MUTED, lw=0.9),
    )

    ax.set_xlabel("Placebo DID (FTE employment)", fontsize=10, color=INK_SECONDARY)
    ax.set_ylabel("Number of permutations", fontsize=10, color=INK_SECONDARY)
    ax.set_title(
        f"Permutation test of the NJ–PA diff-in-diff ({N_PERM:,} shuffles)",
        fontsize=12, color=INK_PRIMARY, pad=8,
    )
    ax.tick_params(colors=INK_MUTED, labelsize=9)
    ax.grid(axis="y", color=GRIDLINE, linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color("#c3c2b7")

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "extension_permutation.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # --- Console summary ---------------------------------------------------
    print("Extension — modern inference robustness")
    print("\nCluster-robust SEs (Table 4 models):")
    print(out.to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    print(f"\nPermutation test: observed DID = {obs:.3f}, N = {len(bal)} "
          f"(NJ {int((state==1).sum())}, PA {int((state==0).sum())})")
    print(f"  two-sided p = {p_two:.4f} | P(DID* >= obs) = {p_greater:.4f} | "
          f"P(DID* <= obs) = {p_less:.4f}")
    print(f"Wrote {TABLES_DIR / 'extension_clustered_se.csv'}")
    print(f"Wrote {TABLES_DIR / 'extension_permutation.csv'}")
    print(f"Wrote {FIGURES_DIR / 'extension_permutation.png'}")


if __name__ == "__main__":
    run()
