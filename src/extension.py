"""Independent extension: does the positive DID estimate survive modern inference?

Economic question. The paper's headline result (a 2.76-FTE relative employment
gain in NJ, t = 2.03) rests on conventional OLS standard errors that ignore
within-group correlation. Neumark & Wascher (2000) later argued the paper's
standard errors were too small. This extension asks: is the result still
statistically credible under (i) cluster-robust standard errors and (ii) an
exact randomization-inference / permutation test?

Plan:
  1. Re-estimate the Table 4 models (NJ dummy and GAP specifications) with
     cluster-robust standard errors, clustering by chain and by region.
  2. Randomization inference on the NJ-PA diff-in-diff: shuffle the treatment
     assignment (NJ vs PA) across stores, recompute the DID estimate many times
     to form the null distribution, and report the permutation p-value (share of
     |placebo DID| >= |observed DID|).

Outputs:
  - output/tables/extension_clustered_se.csv
  - output/tables/extension_permutation.csv
  - output/figures/extension_permutation.png  (null distribution + observed)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd  # noqa: E402
from config import ANALYSIS_SAMPLE  # noqa: E402


def run() -> None:
    df = pd.read_csv(ANALYSIS_SAMPLE)
    # TODO(fill-in): implement clustered SEs and the permutation test.
    raise NotImplementedError("Extension not yet implemented.")


if __name__ == "__main__":
    run()
