"""Build the analysis-ready sample from the raw data.

Reads 01_DID/data/public.csv, constructs every derived variable (FTE, wage gap,
meal price, dummies, closure-adjusted employment), and writes
data/processed/analysis_sample.csv. All downstream scripts read that file, so
the data pipeline is a single, auditable step.

Run directly:  python src/build_sample.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd

import common
from config import ANALYSIS_SAMPLE


def build_sample() -> pd.DataFrame:
    """Return the analysis-ready DataFrame with all derived variables."""
    df = common.load_raw()

    # Employment (both waves); closure-adjusted wave-2 FTE
    df["fte1"] = common.fte(df, 1)
    df = common.fte_with_closure_adjustment(df)  # adds 'fte2'

    # Wage gap and wave-1 wage category
    df["gap"] = common.wage_gap(df)
    df["wage_cat"] = common.nj_wage_category(df)

    # Meal prices
    df["meal1"] = common.full_meal_price(df, 1)
    df["meal2"] = common.full_meal_price(df, 2)

    # Dummies
    df = df.join(common.region_dummies(df))
    df = df.join(common.chain_and_ownership_dummies(df))

    # Change in FTE employment (the DID dependent variable)
    df["dfte"] = df["fte2"] - df["fte1"]

    return df


def run() -> None:
    """Rebuild and write the processed sample to disk."""
    sample = build_sample()
    sample.to_csv(ANALYSIS_SAMPLE, index=False)
    print(f"Wrote {ANALYSIS_SAMPLE} with shape {sample.shape}")


if __name__ == "__main__":
    run()
