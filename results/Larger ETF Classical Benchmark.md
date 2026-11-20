# Larger ETF Selection: Data Audit and Classical Benchmark

**Run date:** November 20, 2026  
**Status:** Completed real-data classical benchmarking. Large-QAOA experiments have **not** been executed.

## Question

How do portfolio-selection methods scale from choosing 3 of 20 ETFs to choosing 6 of 40, 12 of 80, and 24 of 160?

## The data problem and what changed

The original [manisahni/marketdata price file](https://github.com/manisahni/marketdata) has only 27 price columns; the ETF coverage audit found 23 matching candidate ETF histories. That source alone cannot provide 160 different ETFs.

We therefore tested an expanded list of 325 ETF tickers using real dividend/split-adjusted prices downloaded via `yfinance`. The full data workflow recorded **318 complete price histories** and **315 usable Random Forest forecasts** through the December 2024 decision date. The dataset is not synthetic; assets failing the history checks were excluded.

We applied the same basic forecasting design as the original study: Random Forest with recent monthly returns, three- and six-month price changes, and three-month return volatility. The goal was to maximize predicted next-month return minus a covariance-based risk penalty, with **equal weights and exactly k holdings**.

**Important comparability note:** This extended Yahoo Finance data collection uses a different adjusted-price source and a shorter history window from the original Notebook 4. Consequently, its objective scores and ticker selections are **not directly comparable numerically** with the original 3/20 January results. This is a new within-dataset scaling study.

## Benchmark outputs (actual measured results)

| Selected / available | Possible combinations | Greedy score | One-swap improved score | Greedy runtime | One-swap runtime | Is optimum proven? |
|---|---:|---:|---:|---:|---:|---|
| 3 / 20 | 1,140 | 0.074451 | 0.074451 | 0.00041 s | 0.00028 s | Yes, exhaustive check on these 20 |
| 6 / 40 | 3,838,380 | 0.071265 | 0.071265 | 0.00123 s | 0.00103 s | No |
| 12 / 80 | 60,246,643,120,300 | 0.065307 | 0.065307 | 0.00478 s | 0.00455 s | No |
| 24 / 160 | 20,767,445,112,335,933,694,764,617,900 | 0.062452 | 0.062452 | 0.02104 s | 0.02047 s | No |

*Runtimes are measurements from a GitHub Actions runner for these implementations, not hardware-independent speed guarantees. They exclude price downloading and Random Forest model fitting.*

The one-swap local search could not improve greedy's initial choice in these four particular runs. This means a one-asset substitution was not beneficial from those starting solutions; it **does not establish global optimality** for 6/40, 12/80 or 24/160.

Greedy portfolios in the first larger cases:

- **6/40:** XLF, XLE, XLU, XLB, VFH, VDE
- **12/80:** XLF, XLE, XLU, XLB, VFH, VDE, VPU, DIA, IYW, IYF, IYE, IYM
- **24/160:** XLF, XLE, XLU, XLB, IVV, VB, VFH, VDE, VPU, VAW, DIA, IYW, IYF, IYE, IYM, XOP, XME, XES, KIE, SLYG, EWU, EWP, EWY, SLV

These ETF choices depend on forecast values, universe order, and the fixed risk penalty. **The results are research calculations, not investment advice or measured profits.**

## What about running QAOA at these sizes?

With the original one-qubit-per-ETF encoding, the circuits would have 40, 80 or 160 qubits. The original QAOA cost layer has a potentially dense pair interaction for each covariance pair:

| Available assets | Potential pairwise cost gates, per layer |
|---:|---:|
| 40 | 780 |
| 80 | 3,160 |
| 160 | 12,720 |

At depth 2, this can involve up to 1,560, 6,320 and 25,440 pairwise cost operations, before compiler changes and mixer gates. Simulating and repeatedly optimizing these circuits on a normal CPU is not guaranteed to fit the available time or memory. This is a feasibility issue, not proof that QAOA is ineffective.

The next controlled step is a **resource-limited 6/40 QAOA pilot**, then scale farther only if measured simulation costs are acceptable. If 12/80 and 24/160 QAOA jobs cannot be executed, report that fact explicitly rather than inventing scores or comparing unlike algorithms.

## Does Qiskit explain the earlier low QAOA scores?

Qiskit is a published, established quantum software toolkit. The backend check on the identical real-data six-ETF QAOA circuit compared `statevector` against `matrix_product_state` and measured:

- State overlap fidelity: **1.000000000000** (rounded)
- Largest measurement probability difference: **1.59213545126 × 10⁻¹¹**
- Probability of invalid number of selected ETFs: **3.01615872855 × 10⁻²⁰**

The two simulators agreed at this small scale. This argues against a simple backend inconsistency being the cause of low scores on that test. **It does not rule out errors in larger circuits, angle scaling, optimizer convergence, sampling, or QAOA model choices.**

## Evidence

- [Original source feasibility audit](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/44795031480)
- [Expanded real-data RF and classical experiment](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/44795607344)
- [Qiskit backend fidelity test](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/44795973922)
- [Qiskit paper by Javadi-Abhari et al., 2024](https://arxiv.org/abs/2405.08810)
- [IBM Quantum's 40-asset constrained-portfolio QAOA tutorial](https://quantum.cloud.ibm.com/docs/en/tutorials/quantum-approximate-multi-objective-optimization)
- [Qiskit Aer matrix-product-state documentation](https://qiskit.github.io/qiskit-aer/tutorials/7_matrix_product_state_method.html)

**Suggested report wording:** “We extended the classical selection benchmark to 6/40, 12/80 and 24/160 using complete historical ETF price data and matched Random Forest inputs within the expanded study. Classical heuristics ran successfully, but no large-case exact optimum or QAOA comparison has yet been established.”

## Additional 40-qubit QAOA feasibility measurement

In a separate [six-of-forty QAOA pilot](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/44796558632), Qiskit Aer executed a real 40-qubit, 6-selected-ETF circuit at depth 1 with a reduced budget of 6 COBYLA evaluations, 32 optimization shots and 128 final shots.

- QAOA sampled objective score: **0.041604** (rounded)
- Greedy score on the same measured ETF inputs: **0.071265**
- QAOA simulation time: **0.693 seconds**
- Valid final samples: **128/128**
- Optimizer converged: **No** (`success=False`)

This is evidence that a real 6/40 quantum **simulation can execute**, not a fair full-budget QAOA-versus-greedy comparison. Six evaluations were deliberately insufficient to establish QAOA convergence.

## Simulator capacity encountered at 80 and 160

The initial 12/80 and 24/160 pilots did not produce portfolio scores. Qiskit raised `CircuitTooWideForTarget` because the default simulator target advertised 63 qubits. The program now explicitly configures `n_qubits` to the requested size in a separate attempt. A successful configuration is not the same as proof that the full circuit can be simulated efficiently or that QAOA converges.

These backend limits occur at 80/160 and **cannot explain the original low scores measured with 20 qubits**.
