# November 21: QAOA validation, optimizer budget and stronger classical benchmarks

## Verified checks

The QAOA cost encoding was checked independently on a fixed six-asset covariance problem using four unit tests:

1. Polynomial binary score equals the classical equal-weight score for all 20 feasible 3-of-6 choices.
2. Every possible one-asset-swap gain matches the difference from directly recomputing the objective.
3. Greedy and one-swap results respect the known exhaustive optimum.
4. The RZ/RZZ layer's **relative phases** match expected differences in the portfolio objective on all feasible 3-of-6 selections.

All four passed in GitHub Actions [run 44923326171](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/44923326171). These tests verify this part of the circuit, **not** optimizer performance, the full mixer or correctness for arbitrary 160-qubit calculations.

## Experiment A: COBYLA cap of 50 versus 150 (20 ETFs, selecting 3)

Existing original adjusted-price data and the same QAOA setup from Notebook 4, with QAOA depth 2 and identical seeds 0, 1, 2 for both caps. All results are recorded, including failures and optimizer status.

| Seed | Score with limit 50 | Score with limit 150 | Actual evaluations |
|---:|---:|---:|---:|
| 0 | 0.026444 | 0.026444 | 39 |
| 1 | 0.037831 | 0.037831 | 47 |
| 2 | 0.026444 | 0.026444 | 39 |

The exact optimum for the fixed objective is **0.0443022829**. All six runs missed it. Each seed produced the same portfolio/score at both optimization limits, because COBYLA finished before reaching the 50-evaluation maximum. Average gap to the exact optimum at either cap: approximately **0.014063**. Raising only the cap did not improve this experiment.

Verified [run 44923446089](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/44923446089). Do not claim this proves that additional optimization never helps: an alternative optimizer, parameter initialization, scaling or depth could behave differently.

## Experiment B: 25-start classical one-swap optimization

Used a separately downloaded single real-price data snapshot for all four sizes, with checksum `4ee33b8c76860330e51a4218fd6f3b203c26ff608c6251ebd182be19b0617454`. There were 315 usable Random Forest forecasts. Each size used the greedy solution plus 24 seeded random portfolios, with iterative best-improvement one-asset swaps.

| Selected / available | Greedy score | Best of 25 local searches | Distinct final local optima | Seconds for all 25 |
|---|---:|---:|---:|---:|
| 3 / 20 | 0.074451492 | 0.074451492 | 1 | 0.0372 |
| 6 / 40 | 0.071264629 | 0.071264629 | 1 | 0.2370 |
| 12 / 80 | 0.065307489 | 0.065307489 | 1 | 1.8432 |
| 24 / 160 | 0.062451777 | 0.062451777 | 1 | 14.9005 |

**No improvement over greedy** was found, even with varied starting portfolios. The 3/20 result matched the exact optimum by exhaustive search. For the larger three problems, the repeated agreement strengthens the evidence that the local solution is stable **but is not an exact global-optimum certificate**; more powerful global optimizers could find higher scores.

Verified [run 44923326162](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/44923326162); artifact `stronger-multistart-classical` includes the price snapshot and trial summary.

## Important cross-experiment cautions

- The 20-ETF QAOA iteration-budget experiment reuses the *original* market-data source, whose exact score is 0.044302; the expanded 3/20 classical experiment uses an expanded adjusted-price source and different ETF order, whose exact score is 0.074451. **Do not directly compare their scores.**
- Across separate Github Actions runs, downloading adjusted prices from the provider may give slightly different numbers. Use saved price snapshots for tightly controlled repeated comparisons.
- No result here establishes real hardware quantum advantage, profitable investment returns, or global optimality for 6/40, 12/80, or 24/160.
- A scientifically useful next step is an optimizer-method comparison on the *same frozen dataset* and a small/medium-size case with a known exact reference.

## What changed in the code

- `tests/test_large_portfolio_qaoa.py`
- `scripts/multistart_classical_benchmark.py`
- `scripts/qaoa_optimizer_budget.py`
- GitHub Actions workflows for each reproducible experiment

This is an experiment log, not a claim that new QAOA settings beat the classical methods.

## Experiment C: COBYLA versus Powell (20 ETFs, same three seeds)

[GitHub Actions run 44923636158](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/44923636158) passed. Both optimizers used the original January 2025 ETF inputs, QAOA depth 2, three fixed random seeds (0–2), and the same exact optimal score **0.0443022829**. Powell had a maximum of 100 function evaluations; COBYLA had a limit of 50. This is a *comparison of optimizer methods, not matched optimization budgets*. In all cases optimizer.success was true.

| Seed | COBYLA QAOA score | Powell QAOA score | COBYLA evaluations | Powell evaluations |
|---:|---:|---:|---:|---:|
| 0 | 0.026444 | 0.026444 | 39 | 41 |
| 1 | 0.037831 | 0.026444 | 47 | 47 |
| 2 | 0.026444 | 0.026444 | 39 | 82 |

Neither method found the exact optimum in any of the three runs. COBYLA's mean gap was **0.014063**; Powell's mean gap was **0.017858**. Powell did **not** improve the tested outcomes; at seed 1, it produced a worse portfolio. Three seeds are preliminary evidence, and no general optimizer ranking is justified.

**Takeaway:** The QAOA gap cannot be remedied simply by extending the COBYLA evaluation cap from 50 to 150 or swapping to this Powell configuration. The next controlled intervention should investigate circuit depth and initialization or phase-scale sensitivity, keeping the exact classical reference and reporting all seeds.
