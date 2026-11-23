# CECS 385 — QAOA Circuit Depth and Phase-Scale Study

**Run date:** November 23, 2026  
**Status:** All 27 predeclared trials completed, workflow passed.

[Verified GitHub Actions run 45260005221](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/45260005221)

## Research question

Does increasing QAOA circuit depth or changing the return-to-quantum phase scale improve solution quality for the original 20-ETF / select-3 January 2025 problem, holding data, optimizer and shot counts fixed?

## Methods and controls

- Same 20 ETFs, original marketdata monthly historical prices, Random Forest forecast and December 2024 covariance inputs as existing Notebook 4
- Exact exhaustive score: **0.044302285979**; portfolio **XLF, XLE, SPY**; greedy matched exact
- Input forecast/covariance SHA256: `91d07c161420af9fa435421008df7756084fe1b59eec3b73851b2c37a3184b62`
- QAOA depth: **1, 2, 3**
- Portfolio-cost phase scale: **30, 100, 300**
- Three random seeds per configuration: **0, 1, 2**
- 27 total QAOA simulations using Qiskit Aer MPS
- COBYLA max evaluations: **50**, optimization shots **128**, final shots **1,024**
- Each final result is the highest-scoring feasible portfolio found among final samples
- The scale values multiply the circuit's cost-phase angles; the underlying classical portfolio scoring formula stays unchanged

## Verified results

| Circuit depth | Phase scale | Trials | Exact hits | Mean QAOA score | Mean gap to exact | Best QAOA score | Mean simulator seconds |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 30 | 3 | 0 | 0.026444 | 0.017858 | 0.026444 | 1.23 |
| 1 | 100 | 3 | 0 | 0.026444 | 0.017858 | 0.026444 | 1.22 |
| 1 | 300 | 3 | 0 | 0.026444 | 0.017858 | 0.026444 | 1.22 |
| 2 | 30 | 3 | 0 | 0.034924 | 0.009378 | 0.040498 | 3.64 |
| 2 | 100 | 3 | 0 | 0.028918 | 0.015385 | 0.033865 | 3.87 |
| 2 | 300 | 3 | 0 | 0.031391 | 0.012911 | 0.033865 | 3.99 |
| 3 | 30 | 3 | 0 | 0.039696 | 0.004606 | 0.043425 | 10.57 |
| 3 | 100 | 3 | 0 | 0.039343 | 0.004959 | 0.040099 | 11.36 |
| 3 | 300 | 3 | 0 | 0.038100 | 0.006202 | 0.042605 | 11.41 |

The best observed trial was **depth 3, scale 30, seed 2**, selecting **XLF, XLE, XLU** with score **0.0434252678**, a gap of **0.0008770182** below exhaustive. None of the 27 trials found the exact best combination.

## Interpretation

At fixed phase scale 30, increasing depth from 1 to 3 reduced the mean gap from **0.017858** to **0.004606**, roughly a **74% reduction**. Simulator runtime increased from ~1.23 to ~10.57 seconds per run. Depth 3 improved the average scores but most depth-3 optimizations reached 50 evaluations without reporting convergence. Thus the next question is whether a larger *actual* optimization budget would close the gap further.

Phase scaling was **not consistently beneficial** across depths and seeds: for depth 1, all tested scales yielded the same portfolios; at depth 2 and 3, scale 30 had the lowest observed mean gap in these small samples. Changing the scale does not alter the classical objective, only how circuit phases represent it.

This is **small-sample, simulator-specific evidence**, not a statistical demonstration of an effect across market dates, asset sets, hardware, or optimizer settings. The best configuration was chosen after examining results; a subsequent larger-budget depth-3 experiment must be described as **exploratory**, not as confirmation of a pre-registered hypothesis.

## What this contributes to the professor's feedback

The verified QAOA cost-encoding tests and dual Aer backend agreement already argued against a basic score-encoding error as the simple explanation for lower QAOA scores. The new factorial experiment shows that **circuit depth and phase settings affect solution quality** for this problem. This is a more informative answer than blaming Qiskit itself; however neither test proves all Qiskit implementation choices are correct.

## Reproducibility and sources

- Runner: `scripts/qaoa_depth_scale_experiment.py`
- Workflow: `.github/workflows/qaoa-depth-scale.yml`
- Raw/summary CSV files: uploaded artifact `qaoa-depth-phase-27-trials` on [run 45260005221](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/45260005221)
- Original notebook: `data/04 QAOA ETF Scaling Test.ipynb`
- Compare with earlier [November 21 validation, COBYLA cap and classical tests](November%2021%20QAOA%20Validation%20and%20Optimizer%20Tests.md)

**Presentation-safe takeaway:** “On the same 20-ETF test problem, increasing QAOA circuit depth from one to three improved the forecast-based objective score, though simulation time rose, and no configuration found the exact optimum. The evidence suggests circuit settings are consequential; it does not prove the Qiskit software is inaccurate or that quantum hardware has an advantage.”

## Exploratory follow-up: depth-3 COBYLA maximum 50 versus 120

After the depth/phase experiment, we selected depth 3 and scale 30 for a *post-hoc* optimization-budget comparison. The same original forecast/covariance, seeds 0–2, Qiskit Aer MPS simulator, 128 optimization shots and 1,024 final shots were used.

| Maximum optimizer evaluations | Trials | Mean score gap | Best QAOA score | Exact hits | Mean simulator runtime | Mean actual evaluations |
|---:|---:|---:|---:|---:|---:|---:|
| 50 | 3 | 0.004606 | 0.043425 | 0/3 | 10.80 s | 50.0 |
| 120 | 3 | 0.004606 | 0.043425 | 0/3 | 11.75 s | 54.7 |

All three seeds produced **identical final portfolios and score gaps** at both iteration caps. With limit 120, COBYLA reported successful termination after 51–61 evaluations, but the final measured solution did not improve.

**Conclusion:** More optimizer evaluations alone did not improve these depth-3 trials. The higher circuit depth itself appears to matter more than simply raising the iteration limit for the tested settings. This is exploratory and based on three paired starts; it does not prove convergence to a global circuit optimum.

Source: [verified follow-up GitHub Actions run 45260714321](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/45260714321). Script `scripts/qaoa_depth3_followup.py`; artifact `depth3-budget-exploratory-results`.
