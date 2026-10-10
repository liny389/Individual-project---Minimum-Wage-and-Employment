"""Replicate Table 2: means of key variables by state (NJ vs PA).

Table 2 reports, separately for NJ and PA, (1) the distribution of store types
in percentages, (2) wave-1 means of key variables, and (3) wave-2 means, each
with a t-statistic for the null that the two states' means are equal.

Spec (AER Table 2; see docs/plan.md for the exact target numbers):
  * Distribution of store types: CHAIN (Burger King/KFC/Roy Rogers/Wendy's)
    and CO_OWNED (company-owned), as percentages.
  * Wave-1 means: fte1, % full-time workers, WAGE_ST, WAGE_ST == 4.25 (%),
    full-meal price (meal1), HRSOPEN, BONUS.
  * Wave-2 means: fte2 (closure-adjusted), % full-time, WAGE_ST2,
    WAGE_ST2 == 4.25 (%), WAGE_ST2 == 5.05 (%), meal2, HRSOPEN2, SPECIAL2.
  * Two-sample t-test (Welch) for each NJ-vs-PA difference.

Output: output/tables/table2.csv (long format: variable | NJ mean | PA mean |
NJ se | PA se | t-stat).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd  # noqa: E402
from config import ANALYSIS_SAMPLE, TABLES_DIR  # noqa: E402


def run() -> None:
    df = pd.read_csv(ANALYSIS_SAMPLE)
    # TODO(fill-in): implement the means + Welch t-tests described above.
    #   Suggested helper: scipy.stats.ttest_ind(y_nj, y_pa, equal_var=False).
    #   Round to the paper's precision and write the long-format CSV.
    raise NotImplementedError("Table 2 not yet implemented.")


if __name__ == "__main__":
    run()
