# CECS 385 — ETF QAOA Initialization Study and Remaining Experiment Plan

## Result: first nine trials (November 23, 2026)

The original 20 ETF / choose 3 January 2025 objective was evaluated using Qiskit Aer, depth 3, cost-phase scale 30, COBYLA maximum 50 evaluations, 128 shots during optimization, 1024 final shots, and the exact classical score **0.044302285979401675** (XLF, XLE, SPY).

One algorithm parameter was changed: **the location of the three 1-bits in the computational basis initial state**. The classical portfolio objective, circuit depth, XY mixer, optimization budget and final sampling budget were held fixed. Initial states were selected without consulting the exact optimum.

| Initial state family | Starting selection for tested seed(s) | Exact hits / 3 | Mean gap to exact |
|---|---|---:|---:|
| Original evenly spaced | XLK, SPY, HYG | 0 / 3 | 0.004606 |
| Rotate initial indices by 4 | XLE, XLI, TLT | **1 / 3** | **0.001670** |
| Seeded uniform-random feasible 3-subset | Varies by seed | **1 / 3** | **0.002103** |

The rotated start at seed 2 and seeded-random start at seed 2 **both found XLF, XLE, SPY**, with score **0.044302285979401675**, identical to exhaustive search. Neither initial state started at the optimal portfolio. All nine trials had 1,024 valid final samples. Most depth-3 optimizers reached the 50-evaluation cap without reporting successful termination: an exact sampled portfolio does not imply that the continuous optimizer converged.

**Interpretation:** At fixed other settings, changing the initial feasible state produced exact-optimum hits that the original initial state missed. This is evidence that initialization affects QAOA's result on this instance, NOT evidence of a quantum advantage: exhaustive and greedy search also found this exact optimum, at far lower simulated computation cost.

Source: [run 45262610625](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/45262610625) and `scripts/qaoa_initial_state_experiment.py`.

## Statistical confirmation — prespecified new seeds

The next separate experiment is predeclared before viewing its results: seeds **3, 4, 5, 6, 7, 8, 9** for **each** of the same three initialization methods, 21 additional trials, with no stopping based on score. Include every successful or unsuccessful run. Combine with the nine exploratory trials for descriptive overall hit rates while clearly marking the first nine as exploratory.

Sources: `scripts/qaoa_initial_state_confirm.py`, `.github/workflows/qaoa-initial-confirm.yml`.

## How much more testing is necessary?

**Core scope (three remaining evidence packages):**

1. **Initialization confirmation (in progress):** 21 additional 20-ETF QAOA trials. Conclude if the two exact hits generalize beyond seed 2; summarize mean/median exact gap and runtime, not just the best hit.
2. **Across-market validation:** Repeat the strongest predeclared settings on several past months using only data available at each decision date. At a minimum 6 distinct months with exact optimum benchmarks and repeated seeds; compare with exhaustive and greedy. More dates are better evidence than more cherry-picked January settings.
3. **Fair large-scale assessment:** Use ONE frozen ETF price/forecast/covariance snapshot for each 6/40, 12/80 and 24/160 problem. Compare greedy and stronger multistart classical references against QAOA where computationally feasible. For 80/160, if a matched QAOA budget is infeasible, report the resource limit and don't substitute the short six-iteration pilots as equivalent trials.

**Optional extension if time permits:** a full cardinality-preserving **Dicke-state** initial superposition or alternative mixer, with a formal gate/resource budget. This may improve search diversity but requires new circuit-validation tests; do not add just to chase a desirable score.

After those three evidence packages and a polished limitations/discussion section, additional tuning is optional and should be guided by explicit unanswered hypotheses, not indefinite reruns.

## Key research controls and caveats

- **Same dataset/score per comparison.** The earlier expanded Yahoo Finance universe is different from the original 20-ETF marketdata dataset; never compare scores across unrelated universes as if they were direct algorithm rankings.
- **Exact hits vs. investment returns.** A hit is agreement with the best *predicted return-minus-risk objective*, not evidence of actual profit.
- **No quantum hardware speedup.** Qiskit Aer runs on classical compute resources.
- **Multiple comparisons.** Nine initial exploratory trials reveal two promising hits; confirm with unseen random seeds and additional market dates rather than making broad superiority claims.

## Confirmation results: 21 additional unseen-seed trials — completed

The predeclared 21-trial confirmation finished successfully. This included each starting strategy at seeds 3–9, with the same exact 20-ETF January 2025 objective and depth-3/phase-scale-30/50-evaluation/1024-final-shot settings.

| Initial state | Exact hits on NEW seeds 3–9 | Mean QAOA score on new seeds | Mean gap on new seeds | Mean simulator seconds |
|---|---:|---:|---:|---:|
| Spaced | 2 / 7 | 0.041586 | 0.002716 | 12.12 |
| Rotated | **3 / 7** | **0.042300** | **0.002002** | 11.35 |
| Random feasible | 1 / 7 | 0.037055 | 0.007248 | 8.90 |

**On the independent confirmation seeds**, the rotated initial state had the highest exact-hit count and the smallest mean score gap; however, only seven seeds per approach were tested, so the observed differences are uncertain.

When combining all ten tested seeds per method (first 3 exploratory plus 7 confirmation):

| Initial state | Exact hits in all 10 | Combined approximate mean gap |
|---|---:|---:|
| Spaced | 2 / 10 | 0.003283 |
| Rotated | **4 / 10** | **0.001902** |
| Random feasible | 2 / 10 | 0.005705 |

Those combined mean gaps are calculated from the rounded per-group means; use the artifact's raw trial scores to report additional precision. **Do not claim that 4/10 reliably beats 2/10 without more markets and uncertainty analysis.**

Importantly, none of the tested initial portfolios was already the exact optimum. The exact QAOA hits were reached after applying the quantum circuit and optimization/sampling. A hit here refers to the exact *model objective* under simulation, **not a proven quantum speedup over greedy/exhaustive**, which also locate the optimum.

Evidence: [21-trial confirmation GitHub Actions run 45263040991](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/45263040991) and its `qaoa-initialization-confirm-21` CSV artifact; code `scripts/qaoa_initial_state_confirm.py`.

**Decision:** Circuit-initialization experimentation is sufficiently mature for a CECS 385 proof-of-concept. The next test should **not** be more seed-chasing on January 2025; it should validate the selected configurations across new market dates or objective settings.
