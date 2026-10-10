"""Central configuration and constants for the Card & Krueger (1994) replication.

All paths and economic constants are single-sourced here. If you move files or
want to tweak a parameter, change it here rather than in the individual scripts.

Card & Krueger (1994), "Minimum Wages and Employment," American Economic
Review 84(4), 772-793. Replication target: Tables 2-4 and Figure 1.
"""
from pathlib import Path

# --- Paths -----------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA = PROJECT_ROOT / "01_DID" / "data" / "public.csv"   # restricted raw input

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
ANALYSIS_SAMPLE = PROCESSED_DIR / "analysis_sample.csv"      # built by build_sample.py

TABLES_DIR = PROJECT_ROOT / "output" / "tables"
FIGURES_DIR = PROJECT_ROOT / "output" / "figures"

for _d in (PROCESSED_DIR, TABLES_DIR, FIGURES_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# --- Economic constants ----------------------------------------------------
OLD_MINIMUM_WAGE = 4.25     # minimum wage before April 1, 1992 (federal/NJ/PA)
NEW_MINIMUM_WAGE = 5.05     # NJ minimum wage on/after April 1, 1992

PART_TIME_FTE_WEIGHT = 0.5  # part-time worker counts as half a full-time worker (FTE)

# --- Categorical codes (from 01_DID/DATA_DICTIONARY.md) --------------------
CHAIN_LABELS = {1: "Burger King", 2: "KFC", 3: "Roy Rogers", 4: "Wendy's"}

# Second-wave status (STATUS2)
STATUS_REFUSED = 0          # refused wave-2 interview
STATUS_ANSWERED = 1         # answered
STATUS_RENOVATION = 2       # temporarily closed: under renovation
STATUS_PERM_CLOSED = 3      # permanently closed
STATUS_HIGHWAY_CLOSED = 4   # temporarily closed: highway construction
STATUS_FIRE_CLOSED = 5      # temporarily closed: mall fire

# Statuses treated as "temporarily closed" -> wave-2 employment set to missing
TEMPORARILY_CLOSED = {STATUS_RENOVATION, STATUS_HIGHWAY_CLOSED, STATUS_FIRE_CLOSED}
