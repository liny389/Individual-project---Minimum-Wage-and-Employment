"""Replicate Table 3: average FTE employment per store before and after.

Table 3 presents mean FTE employment by state [PA (i), NJ (ii), NJ-PA (iii)] and
by NJ wave-1 wage range [low = $4.25 (iv), mid = $4.26-$4.99 (v), high >= $5.00
(vi)], plus within-NJ differences [low-high (vii), mid-high (viii)]. Rows:

  1. FTE before, all available observations
  2. FTE after, all available observations
  3. Change in mean FTE (row 2 - row 1)
  4. Change in mean FTE, balanced sample (valid employment in both waves)
  5. Change in mean FTE, setting wave-2 FTE at temporarily-closed stores to 0

Standard-error convention (documented; see report):
  * rows 1-2: SE of the mean = sd / sqrt(n) over available observations;
  * row 3:    unpaired difference of means, SE = sqrt(se_before^2 + se_after^2);
  * rows 4-5: paired change, SE = sd(diff) / sqrt(n) over the balanced panel.

The paired (row 4) SE is the correct within-store standard error and reproduces
the paper's headline t ~ 2.03 for the NJ-PA diff-in-diff; the small remaining
gap traces to a data-version difference (see docs/plan.md "Open items").

Output: output/tables/table3.csv (wide: rows 1-5, mean + SE per column).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd

from config import ANALYSIS_SAMPLE, TABLES_DIR, TEMPORARILY_CLOSED

# The 8 table columns: 5 base groups + 3 differences.
BASE_COLS = ["PA", "NJ", "low", "mid", "high"]
DIFF_COLS = [("NJ-PA", "NJ", "PA"), ("low-high", "low", "high"), ("mid-high", "mid", "high")]


def _mean_se(s: pd.Series):
    s = s.dropna()
    return s.mean(), s.std() / np.sqrt(len(s)), len(s)


def _paired(before: pd.Series, after: pd.Series):
    m = before.notna() & after.notna()
    d = (after - before)[m]
    return d.mean(), d.std() / np.sqrt(len(d)), len(d)


def _group_frame(df: pd.DataFrame) -> dict:
    """Return {col: (before, after)} for the five base groups."""
    return {
        "PA": (df.loc[df.STATE == 0, "fte1"], df.loc[df.STATE == 0, "fte2"]),
        "NJ": (df.loc[df.STATE == 1, "fte1"], df.loc[df.STATE == 1, "fte2"]),
        "low": (df.loc[df.wage_cat == "low", "fte1"], df.loc[df.wage_cat == "low", "fte2"]),
        "mid": (df.loc[df.wage_cat == "mid", "fte1"], df.loc[df.wage_cat == "mid", "fte2"]),
        "high": (df.loc[df.wage_cat == "high", "fte1"], df.loc[df.wage_cat == "high", "fte2"]),
    }


def run() -> None:
    df = pd.read_csv(ANALYSIS_SAMPLE)

    # Wave-2 FTE with temporarily-closed stores set to 0 (for row 5)
    fte2_t0 = df["fte2"].copy()
    fte2_t0[df["STATUS2"].isin(TEMPORARILY_CLOSED)] = 0.0

    # Build a table of (mean, se) per base column per row.
    mean = pd.DataFrame(index=BASE_COLS, columns=["before", "after", "chg", "chg_bal", "chg_t0"], dtype=float)
    se = mean.copy()

    for col, (before, after) in _group_frame(df).items():
        b_m, b_se, _ = _mean_se(before)
        a_m, a_se, _ = _mean_se(after)
        mean.loc[col, "before"], se.loc[col, "before"] = b_m, b_se
        mean.loc[col, "after"], se.loc[col, "after"] = a_m, a_se

        # Row 3: unpaired change
        mean.loc[col, "chg"] = a_m - b_m
        se.loc[col, "chg"] = np.sqrt(b_se**2 + a_se**2)

        # Row 4: paired (balanced) change
        p_m, p_se, _ = _paired(before, after)
        mean.loc[col, "chg_bal"], se.loc[col, "chg_bal"] = p_m, p_se

        # Row 5: paired change with temp-closed -> 0
        b2, a2 = before, fte2_t0.loc[before.index]
        p_m, p_se, _ = _paired(b2, a2)
        mean.loc[col, "chg_t0"], se.loc[col, "chg_t0"] = p_m, p_se

    # Add the three difference columns.
    for label, col_a, col_b in DIFF_COLS:
        mean.loc[label] = mean.loc[col_a] - mean.loc[col_b]
        se.loc[label] = np.sqrt(se.loc[col_a] ** 2 + se.loc[col_b] ** 2)

    # Reorder columns into the paper's layout: PA, NJ, NJ-PA, low, mid, high, low-high, mid-high.
    order = ["PA", "NJ", "NJ-PA", "low", "mid", "high", "low-high", "mid-high"]
    mean, se = mean.loc[order], se.loc[order]

    # Long-format CSV for the report.
    rows = ["before", "after", "chg", "chg_bal", "chg_t0"]
    out = pd.DataFrame(
        {
            "stat": np.repeat(["mean", "se"], len(order) * len(rows)),
            "row": np.tile(np.repeat(rows, len(order)), 2),
            "column": np.tile(list(order) * len(rows), 2),
            "value": np.concatenate([mean.T.values.ravel(), se.T.values.ravel()]),
        }
    )
    out.to_csv(TABLES_DIR / "table3.csv", index=False)

    # Human-readable wide print.
    print("Table 3 — mean FTE employment per store (SE in parentheses)")
    for r in rows:
        line = f"{r:>10s} | " + " | ".join(f"{mean.loc[c, r]:6.2f} ({se.loc[c, r]:.2f})" for c in order)
        print(line)

    did = mean.loc["NJ-PA", "chg"]
    did_se = se.loc["NJ-PA", "chg"]
    print(f"\nRow-3 (unpaired) NJ-PA DID = {did:.3f}  SE = {did_se:.3f}  t = {did / did_se:.3f}")
    did_bal = mean.loc["NJ-PA", "chg_bal"]
    did_bal_se = se.loc["NJ-PA", "chg_bal"]
    print(f"Row-4 (balanced) NJ-PA DID = {did_bal:.3f}  SE = {did_bal_se:.3f}  t = {did_bal / did_bal_se:.3f}")
    print(f"Wrote {TABLES_DIR / 'table3.csv'}")


if __name__ == "__main__":
    run()
