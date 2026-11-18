"""Run the scaling notebook in GitHub Actions and save the measured results."""
import argparse
import json
import os
import sys
import traceback
from pathlib import Path

from IPython.display import display

NOTEBOOK = Path("data/04 QAOA ETF Scaling Test.ipynb")
CELL_NUMBERS = (4, 5, 7, 9, 11, 13, 15)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--counts", default="6", help="Comma-separated ETF counts")
    parser.add_argument("--seeds", type=int, default=1)
    parser.add_argument("--iterations", type=int, default=8)
    parser.add_argument("--opt-shots", type=int, default=64)
    parser.add_argument("--final-shots", type=int, default=256)
    args = parser.parse_args()

    counts = tuple(int(n) for n in args.counts.split(","))
    assert counts and set(counts).issubset({6, 10, 15, 20})
    assert 1 <= args.seeds <= 10
    assert args.iterations >= 6

    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    scope = {"__name__": "__main__", "display": display}

    print("Actual market-price experiment, not synthetic test data", flush=True)
    print("ETF counts:", counts, "| Seeds:", args.seeds, "| Iterations:", args.iterations, flush=True)

    try:
        for index in CELL_NUMBERS:
            if index == 11:
                scope["ETF_COUNTS"] = counts
                scope["TRIAL_SEEDS"] = tuple(range(args.seeds))
                scope["QAOA_ITERATIONS"] = args.iterations
                scope["OPTIMIZATION_SHOTS"] = args.opt_shots
                scope["FINAL_SHOTS"] = args.final_shots
            cell = notebook["cells"][index]
            code = "".join(cell["source"])
            print("Executing code cell", index, flush=True)
            exec(compile(code, f"{NOTEBOOK}:cell{index}", "exec"), scope)
    except Exception:
        traceback.print_exc()
        raise

    trials = scope["trials_df"]
    expected = len(counts) * args.seeds
    assert len(trials) == expected
    assert set(trials["etfs"]) == set(counts)
    assert trials["valid_shots"].eq(args.final_shots).all()
    assert trials["score"].notna().all()

    print("\nVERIFIED COMPLETE: ", len(trials), "real-price QAOA trials", flush=True)
    print(trials[["etfs", "seed", "score", "gap", "runtime_seconds"]].to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
