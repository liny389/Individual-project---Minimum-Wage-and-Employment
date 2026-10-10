"""Replicate Figure 1: distribution of starting wages in NJ and PA.

Figure 1 shows the distribution of starting wages before the increase
(February 1992) and after (November 1992), separately for NJ and PA. In wave 1
the two states' distributions look alike; by wave 2 nearly all NJ stores that
had been below $5.05 report the new $5.05 rate (a mass point at 5.05).

Spec: two panels (before / after). Each panel plots a histogram (or step plot)
of starting wages (WAGE_ST for wave 1, WAGE_ST2 for wave 2) for NJ and PA,
with wage on the x-axis and the share of stores on the y-axis.

Output: output/figures/figure1.png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd  # noqa: E402
from config import ANALYSIS_SAMPLE, FIGURES_DIR  # noqa: E402


def run() -> None:
    df = pd.read_csv(ANALYSIS_SAMPLE)
    # TODO(fill-in): build the two-panel histogram/step plot described above.
    #   Use matplotlib directly (seaborn is not required). Pick sensible bins
    #   (e.g. $4.00-5.75 by $0.25) and label axes.
    raise NotImplementedError("Figure 1 not yet implemented.")


if __name__ == "__main__":
    run()
