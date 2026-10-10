"""Reproducible workflow: regenerate every table and figure from raw data.

Single entry point for reproducibility. Run from the project root:

    python src/run_all.py

It (re)builds the processed sample and runs each replication/extension step in
order. Steps that are not yet implemented are reported as SKIPPED so the
pipeline is runnable while the project is still being filled in.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_sample  # noqa: E402
import extension  # noqa: E402
import figure1  # noqa: E402
import table2  # noqa: E402
import table3  # noqa: E402
import table4  # noqa: E402

STEPS = [
    ("build_sample", build_sample.run),
    ("table2", table2.run),
    ("figure1", figure1.run),
    ("table3", table3.run),
    ("table4", table4.run),
    ("extension", extension.run),
]


def main() -> None:
    for name, fn in STEPS:
        print(f"\n=== {name} ===")
        try:
            fn()
            print(f"{name}: OK")
        except NotImplementedError:
            print(f"{name}: SKIPPED (not yet implemented)")
        except Exception as exc:  # noqa: BLE001
            print(f"{name}: FAILED -> {exc!r}")


if __name__ == "__main__":
    main()
