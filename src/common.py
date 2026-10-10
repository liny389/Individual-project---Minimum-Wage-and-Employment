"""Shared data-transform helpers for the Card & Krueger (1994) replication.

Every derived variable used across the tables/figure is defined *once* here so
that the outputs stay mutually consistent. Raw column meanings are documented
in 01_DID/DATA_DICTIONARY.md.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from config import (
    RAW_DATA,
    NEW_MINIMUM_WAGE,
    OLD_MINIMUM_WAGE,
    PART_TIME_FTE_WEIGHT,
    STATUS_PERM_CLOSED,
    TEMPORARILY_CLOSED,
)


def load_raw() -> pd.DataFrame:
    """Load the raw survey data (410 stores x 46 columns)."""
    return pd.read_csv(RAW_DATA)


def _sfx(wave: int) -> str:
    """Column suffix for a survey wave: wave 1 -> '', wave 2 -> '2'."""
    return "" if wave == 1 else "2"


# --- Employment measures ---------------------------------------------------

def full_time_workers(df: pd.DataFrame, wave: int) -> pd.Series:
    """Full-time workers including managers/assistant managers."""
    sfx = _sfx(wave)
    return df[f"EMPFT{sfx}"] + df[f"NMGRS{sfx}"]


def fte(df: pd.DataFrame, wave: int) -> pd.Series:
    """Full-time-equivalent employment = full-time workers + 0.5 * part-time."""
    sfx = _sfx(wave)
    return full_time_workers(df, wave) + PART_TIME_FTE_WEIGHT * df[f"EMPPT{sfx}"]


def fte_with_closure_adjustment(df: pd.DataFrame) -> pd.DataFrame:
    """Add a wave-2 FTE column (`fte2`) that accounts for store closures.

    Rules from the paper (Table 2 notes):
      * permanently closed stores (STATUS2 == 3) -> wave-2 FTE = 0
      * temporarily closed stores -> wave-2 FTE = missing (NaN)
    """
    out = df.copy()
    fte2 = fte(out, 2)
    fte2 = fte2.where(~out["STATUS2"].isin(TEMPORARILY_CLOSED))  # temp -> NaN
    fte2 = fte2.where(out["STATUS2"] != STATUS_PERM_CLOSED, 0.0)  # perm -> 0
    out["fte2"] = fte2
    return out


# --- Wage measures ---------------------------------------------------------

def wage_gap(df: pd.DataFrame) -> pd.Series:
    """Initial wage gap = proportional raise needed to reach the new minimum.

    GAP_i = 0 for PA stores; 0 for NJ stores already at/above $5.05;
            (5.05 - WAGE_ST)/WAGE_ST otherwise.
    """
    w = df["WAGE_ST"]
    gap = np.where(df["STATE"] == 0, 0.0, np.maximum(0.0, (NEW_MINIMUM_WAGE - w) / w))
    return pd.Series(gap, index=df.index)


def nj_wage_category(df: pd.DataFrame) -> pd.Series:
    """Wave-1 starting-wage category for NJ stores (Table 3 classification).

    Returns 'low' ($4.25), 'mid' ($4.26-$4.99), 'high' (>= $5.00), else NaN.
    """
    w = df["WAGE_ST"]
    cat = pd.Series(index=df.index, dtype="object")
    cat[(df["STATE"] == 1) & (w == OLD_MINIMUM_WAGE)] = "low"
    cat[(df["STATE"] == 1) & (w > OLD_MINIMUM_WAGE) & (w < 5.00)] = "mid"
    cat[(df["STATE"] == 1) & (w >= 5.00)] = "high"
    return cat


# --- Prices ----------------------------------------------------------------

def full_meal_price(df: pd.DataFrame, wave: int) -> pd.Series:
    """After-tax 'full meal' price = medium soda + small fries + entree."""
    sfx = _sfx(wave)
    return df[f"PSODA{sfx}"] + df[f"PFRY{sfx}"] + df[f"PENTREE{sfx}"]


# --- Dummies ---------------------------------------------------------------

def region_dummies(df: pd.DataFrame) -> pd.DataFrame:
    """Region dummies for Table 4, col (v).

    NJ: CENTRALJ and SOUTHJ (North NJ is the omitted category).
    PA: PA1 (northeastern Philly suburbs) and PA2 (Easton area); other PA omitted.
    """
    return pd.DataFrame(
        {
            "nj_central": df["CENTRALJ"],
            "nj_south": df["SOUTHJ"],
            "pa_ne_philly": df["PA1"],
            "pa_easton": df["PA2"],
        }
    )


def chain_and_ownership_dummies(df: pd.DataFrame) -> pd.DataFrame:
    """Chain dummies (3 of 4, Burger King omitted) + company-owned indicator."""
    return pd.DataFrame(
        {
            "kfc": (df["CHAIN"] == 2).astype(int),
            "roy_rogers": (df["CHAIN"] == 3).astype(int),
            "wendys": (df["CHAIN"] == 4).astype(int),
            "co_owned": df["CO_OWNED"],
        }
    )
