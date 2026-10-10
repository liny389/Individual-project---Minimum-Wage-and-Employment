"""Replicate Table 2: means of key variables by state (NJ vs PA).

Three sections, each with NJ and PA columns (and a t-statistic for sections 2-3):

  1. Distribution of store types (percentages): chain + company-owned.
  2. Means in wave 1: FTE, % full-time, starting wage, wage=$4.25 (%),
     full-meal price, hours open, recruiting bonus.
  3. Means in wave 2: FTE, % full-time, starting wage, wage=$4.25 (%),
     wage=$5.05 (%), full-meal price, hours open, recruiting bonus.

t-statistics are Welch two-sample t-tests of the NJ-vs-PA mean difference.

Output: output/tables/table2.csv (long: section | variable | NJ | PA | t).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd
from scipy import stats

import common
from config import ANALYSIS_SAMPLE, TABLES_DIR


def _welch(a: pd.Series, b: pd.Series):
    a, b = a.dropna(), b.dropna()
    t = stats.ttest_ind(a, b, equal_var=False).statistic
    return a.mean(), a.std() / np.sqrt(len(a)), b.mean(), b.std() / np.sqrt(len(b)), t


def run() -> None:
    df = pd.read_csv(ANALYSIS_SAMPLE)
    nj = df[df.STATE == 1]
    pa = df[df.STATE == 0]

    # Derived: "% full-time employees" = non-manager full-time workers / FTE
    # (matches the paper's Table 2 definition; NJ wave-1 value = 32.8).
    df["pctft1"] = df["EMPFT"] / df["fte1"] * 100
    df["pctft2"] = df["EMPFT2"] / df["fte2"] * 100
    df["w425_1"] = (df["WAGE_ST"] == 4.25) * 100.0
    df["w425_2"] = (df["WAGE_ST2"] == 4.25) * 100.0
    df["w505_2"] = (df["WAGE_ST2"] == 5.05) * 100.0
    nj, pa = df[df.STATE == 1], df[df.STATE == 0]

    # Section 1: store-type distribution (percentages).
    store_types = {
        "Burger King (%)": (df["CHAIN"] == 1),
        "KFC (%)": (df["CHAIN"] == 2),
        "Roy Rogers (%)": (df["CHAIN"] == 3),
        "Wendy's (%)": (df["CHAIN"] == 4),
        "Company-owned (%)": (df["CO_OWNED"] == 1),
    }

    # Sections 2-3: wave-1 and wave-2 variables.
    waves = {
        "Wave 1": {
            "FTE employment": "fte1",
            "% full-time employees": "pctft1",
            "Starting wage": "WAGE_ST",
            "Wage = $4.25 (%)": "w425_1",
            "Price of full meal": "meal1",
            "Hours open (weekday)": "HRSOPEN",
            "Recruiting bonus (%)": "BONUS",
        },
        "Wave 2": {
            "FTE employment": "fte2",
            "% full-time employees": "pctft2",
            "Starting wage": "WAGE_ST2",
            "Wage = $4.25 (%)": "w425_2",
            "Wage = $5.05 (%)": "w505_2",
            "Price of full meal": "meal2",
            "Hours open (weekday)": "HRSOPEN2",
            "Recruiting bonus (%)": "SPECIAL2",
        },
    }

    records = []
    for label, mask in store_types.items():
        records.append({"section": "Store types", "variable": label,
                        "NJ": mask[nj.index].mean() * 100, "PA": mask[pa.index].mean() * 100,
                        "t": np.nan})

    for section, vars_ in waves.items():
        for label, col in vars_.items():
            nj_m, nj_se, pa_m, pa_se, t = _welch(nj[col], pa[col])
            records.append({"section": section, "variable": label,
                            "NJ": nj_m, "NJ_se": nj_se, "PA": pa_m, "PA_se": pa_se, "t": t})

    out = pd.DataFrame(records)
    out.to_csv(TABLES_DIR / "table2.csv", index=False)

    # Human-readable print.
    print("Table 2 — means by state (SE in parentheses; t = Welch)")
    cur = None
    for r in records:
        if r["section"] != cur:
            cur = r["section"]
            print(f"\n[{cur}]")
        if r["section"] == "Store types":
            print(f"  {r['variable']:<22s} NJ {r['NJ']:6.1f}%   PA {r['PA']:6.1f}%")
        else:
            print(f"  {r['variable']:<22s} NJ {r['NJ']:7.2f} ({r['NJ_se']:.2f})   "
                  f"PA {r['PA']:7.2f} ({r['PA_se']:.2f})   t {r['t']:6.2f}")
    print(f"\nWrote {TABLES_DIR / 'table2.csv'}")


if __name__ == "__main__":
    run()
