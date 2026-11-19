# QAOA Check with Different ETF Groups

**Measured November 19, 2026 — additional robustness experiment**

The original scaling experiment took the first 6, 10, 15 or 20 ETFs from a fixed list. I wanted to check whether the conclusions were affected by which ETFs were included.

For this test I randomly rearranged the original list of 20 ETFs using NumPy random seed 385, and then selected the first 10 or 15. I used **three different groups per ETF count**, with **three QAOA trials per group** (seeds 0–2). This produced **18 new measured trials**. All runs use the existing January 2025 forecast and covariance inputs. The objective, three-ETF selection rule, QAOA depth 2, 50 COBYLA iterations, 128 optimization shots and 1,024 final shots are unchanged.

## Measured results

| ETF count | Group | Exact optimum found | Mean score gap | Mean simulator time |
|---:|---:|---:|---:|---:|
| 10 | 0 | 2/3 | 0.001464 | 2.32 s |
| 10 | 1 | 0/3 | 0.005200 | 2.59 s |
| 10 | 2 | 3/3 | 0.000000 | 2.77 s |
| 15 | 0 | 0/3 | 0.013464 | 2.06 s |
| 15 | 1 | 0/3 | 0.002297 | 2.07 s |
| 15 | 2 | 0/3 | 0.002505 | 1.92 s |

Overall, QAOA matched the exact optimum in **5 of 9 ten-ETF trials (55.6%)** and **0 of 9 fifteen-ETF trials (0%)**. The exact-hit rate depended on ETF composition at ten ETFs: one group succeeded in all three runs, another in none. At fifteen ETFs QAOA did not hit the exact best score in any of the three groups.

The original fixed-group experiment had an **80% exact-hit rate for ten ETFs** and **0% for fifteen ETFs** across ten seeds each. This new test suggests that ETF selection affects results at ten ETFs, while missing the optimum at fifteen ETFs was consistent across the sampled groups. These are different samples, not matched head-to-head trials, so the difference in rates should not be interpreted as proof of an exact effect size.

## Important limits

- The test uses the **same January 2025 decision date**, not different market periods.
- The groups change the available assets as well as the optimization landscape.
- Nine runs per size is a small sample, not strong statistical evidence.
- Both studies use a **simulated** QAOA circuit. Runtime is simulator-specific, not evidence about quantum hardware.
- Portfolio objective scores are not actual realized returns or yearly profits.

## Evidence and reproducibility

- [Passing GitHub Actions run for the new experiment](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/44537205157)
- Run artifacts `random-etf-groups-10` and `random-etf-groups-15` contain the individual trials, selected ticker groups and CSV summaries.
- [Original 40-trial ETF scaling experiment](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/44225096990)

This validation study adds evidence about ETF composition. A multi-date QAOA comparison would still be useful before drawing a broad conclusion.
