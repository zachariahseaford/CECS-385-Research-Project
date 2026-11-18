# QAOA ETF Scaling Results — November 18, 2026

I compared simulated QAOA with exhaustive search and greedy search using 6, 10, 15, and 20 ETFs. Each test selected 3 ETFs using the same January 2025 Random Forest return estimates and portfolio risk formula.

The simulation ran in [GitHub Actions, run 44225096990](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/44225096990). All four jobs passed, with 10 QAOA trials each. The original CSV files and graphs are saved as four artifacts attached to that run.

## Settings

- **ETF counts:** 6, 10, 15, 20 (nested subsets of the original list)
- **Portfolios:** exactly 3 ETFs, equally weighted
- **Forecasting:** December 2024 information used to predict January 2025 ETF returns
- **Portfolio score:** predicted return minus risk penalty, with lambda = 1.0
- **Simulator:** Qiskit Aer, matrix product state
- **QAOA depth:** 2
- **Optimizer:** COBYLA, maximum 50 iterations
- **Sampling:** 128 shots during optimization, 1,024 shots for final portfolio selection
- **Random starts:** seeds 0 through 9 for each ETF count

## Measured results

| ETFs | Possible portfolios | QAOA found exact best score | Mean QAOA score | Mean absolute score gap | Mean QAOA runtime |
|---:|---:|---:|---:|---:|---:|
| 6 | 20 | 10/10 (100%) | 0.042605 | 0.000000 | 1.04 s |
| 10 | 120 | 8/10 (80%) | 0.044045 | 0.000257 | 1.69 s |
| 15 | 455 | 0/10 (0%) | 0.040440 | 0.003863 | 2.42 s |
| 20 | 1,140 | 0/10 (0%) | 0.029086 | 0.015216 | 3.49 s |

Values are rounded from the printed GitHub Actions run logs; the attached CSV artifacts contain the individual trial data. These are **estimated portfolio objective scores**, not actual investment returns.

## What I found

For the six-ETF problem, simulated QAOA found the exact best score in all ten trials. At ten ETFs it found the exact best score eight times. It did not find the exact best score in any of the fifteen- or twenty-ETF trials. The average score gap increased and simulation runtime also increased with ETF count.

This suggests QAOA became less reliable for finding the exact best portfolio in this experiment as the number of candidate ETFs increased. Exhaustive search is still the reference result because it evaluates every possible three-ETF portfolio. The classical and greedy runtime measurements are recorded in the benchmark CSV files.

## Limitations

- These are **Qiskit Aer simulator runtimes**, not quantum-hardware runtimes or dollar costs.
- Only one January 2025 portfolio decision was tested for QAOA.
- ETF groups are nested and the underlying assets change with each count, so this is not a pure computational scaling study.
- Ten random starts per size are useful preliminary evidence but do not establish general performance.
- The score maximizes a forecast-return-minus-risk objective. It does not measure monthly or yearly realized return.
- A more complete study would test additional dates and ETF groups, including matched returns, transaction costs, and other classical algorithms.

## Where to get the data

Open the [GitHub Actions experiment run](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/44225096990) and download the artifacts named `qaoa-real-data-6-etfs`, `qaoa-real-data-10-etfs`, `qaoa-real-data-15-etfs`, and `qaoa-real-data-20-etfs`. Each contains individual QAOA trial results, classical benchmark values, a summary, and a graph.
