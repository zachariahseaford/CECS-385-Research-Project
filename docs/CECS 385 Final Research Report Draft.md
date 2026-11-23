# Quantum Versus Classical ETF Portfolio Selection

**CECS 385 — Final Research Report**  
University of Tennessee, Knoxville · November 23, 2026  
**Project:** Quantum Approximate Optimization Algorithm (QAOA) versus exhaustive and greedy ETF selection

## Abstract

This project investigates whether the Quantum Approximate Optimization Algorithm (QAOA), simulated using IBM's Qiskit Aer software, can select exchange-traded fund (ETF) portfolios as accurately and efficiently as classical search. A Random Forest estimates next-month returns from historical ETF prices, and each method attempts to maximize the same equal-weighted predicted return minus covariance-based risk penalty. The original study selected three ETFs from up to twenty candidates, and compared exhaustive search, greedy search and QAOA. The initial scaling experiment found exact QAOA solutions in 10/10 trials for six ETFs and 8/10 for ten ETFs, but 0/10 for fifteen or twenty ETFs.

Further experiments examined circuit depth, initial states, six historical decision months not used for January 2025 tuning, and portfolios selecting 6 of 40, 12 of 80 and 24 of 160 ETFs. For the January 2025 3-of-20 task, depth-three QAOA with varied initialization sampled the exact optimum in 8 of 30 trials. Across six additional months (36 trials), QAOA reached the exact solution five times. Greedy search equaled exhaustive search on all six historical decisions and the January 2025 decision. Exhaustive evaluation of all 3,838,380 six-of-forty portfolios also confirmed that greedy found the exact optimum for that larger case. A final risk-sensitivity test with two additional risk penalties again found no QAOA win over greedy. Although QAOA sometimes found exact solutions, this work did **not** demonstrate a quantum advantage. All QAOA experiments were classical simulations, and the modeled optimization scores are not realized investment returns.

## 1. Research question and objectives

The main research question is: **Can simulated QAOA find high-scoring ETF portfolios competitively with classical exhaustive and greedy selection as the number of available ETFs and selected holdings increases?**

The objectives were to (1) compare QAOA with an exact benchmark when enumeration is feasible; (2) measure its score gaps and execution time; (3) test sensitivity to problem size, circuit depth, phase scaling and initial state; (4) examine whether promising circuit settings work on different market dates; and (5) investigate feasibility of 40-, 80- and 160-qubit portfolio circuits. A QAOA score *above* the exact exhaustive maximum would indicate an implementation or comparison error, not success. A legitimate possible advantage would instead be beating a **suboptimal classical heuristic**, finding the optimum more reliably, or reducing resource cost in a properly controlled comparison.

## 2. Related work and software validity

Qiskit is an established, open-source quantum software development kit used in academic research; Javadi-Abhari and colleagues documented its quantum-circuit and execution framework in *Quantum computing with Qiskit* (2024). The Qiskit Finance community publishes a portfolio-optimization example using QAOA. Brandhofer and colleagues' peer-reviewed *Benchmarking the performance of portfolio optimization with QAOA* (2023) investigates quantum portfolio optimization and its sensitivity to QAOA configuration. Thus QAOA portfolio selection is **not a newly invented algorithm**, and Qiskit is not an untested software platform.

This project uses **Qiskit** to construct quantum circuits and **Qiskit Aer** with the matrix-product-state method to simulate those circuits on ordinary computing hardware. **SciPy COBYLA** adjusts their parameters. There was no run on IBM quantum hardware. Small-circuit cross-backend testing compared Aer statevector and matrix-product-state simulation, obtaining essentially matching measurement probabilities (fidelity approximately 1). Four separate unit tests checked the portfolio scoring formula, the RZ/RZZ cost phases, one-asset-swap score differences and classical solutions against small exact problems. Those tests found no error in the tested scoring encoding. They do **not** prove that an optimizer converges or that all large-circuit simulations are exact.

## 3. Data and methodology

### 3.1 Data and forecasting

The original 20-ETF study used historical adjusted prices from the public [manisahni/marketdata](https://github.com/manisahni/marketdata) source. The candidate universe includes stock sector and broad-market funds, fixed income, gold and real estate. Daily prices were aggregated to month-end. For each ETF, the Random Forest features were the prior month's return, three- and six-month price changes and three-month return volatility. January 2025 forecasts used information available through December 2024; training labels were restricted to next-month returns known by the decision date. Covariance was estimated from historical monthly returns.

The original six-month forecasting assessment (July–December 2024, 120 ETF-month predictions) measured **mean absolute error 0.03757** for Random Forest and **0.04881** for a simple forecasting baseline. Better predictive MAE alone does not establish better realized investment performance.

For additional 40-, 80- and 160-ETF experiments, the original market data file proved too small (27 price columns, with 23 matching usable ETF candidates). We downloaded a larger universe of **real, adjusted** ETF price histories using yfinance, checked completeness and obtained **315 usable Random Forest forecasts**. The expanded dataset was used consistently within each individual comparison, but **its objective scores are not numerically comparable to the original 20-ETF dataset**, even when the same number of assets is used.

### 3.2 Portfolio scoring and constraints

Each method chooses exactly \(k\) funds from \(n\) candidates. Holdings receive weight \(1/k\), and all other weights are zero. The portfolio objective is

\[
\max_w\quad J(w)=\mu^\mathsf{T}w-\lambda w^\mathsf{T}\Sigma w,
\qquad \sum_i w_i=1, \quad w_i\in\{0,1/k\},
\]

where \(\mu\) is the model's predicted next-month returns, \(\Sigma\) the historical monthly covariance matrix and \(\lambda\) the risk penalty. The primary study uses \(\lambda=1\). The score is **predicted return minus estimated variance risk**, not a realized return, Sharpe ratio, profit, or percentage yield.

For exactly \(k\) selected ETFs, the number of candidate portfolios is \(\binom{n}{k}\). Our problems included:

| Selected / available ETFs | Candidate portfolios | Circuit qubits |
|---|---:|---:|
| 3 / 20 | 1,140 | 20 |
| 6 / 40 | 3,838,380 | 40 |
| 12 / 80 | 60,246,643,120,300 | 80 |
| 24 / 160 | 20,767,445,112,335,933,694,764,617,900 | 160 |

The larger three problems all select 15% of their candidate funds. Exhaustive enumeration was used for the original 3/20 cases and for 6/40, but not for 12/80 or 24/160.

### 3.3 Classical methods

**Exhaustive search** enumerates all valid \(k\)-ETF combinations and evaluates \(J(w)\), providing a proven exact optimum under the specified input and objective. **Greedy search** adds one ETF at a time by choosing the next asset that produces the highest partial objective with the target final \(k\) weights. **One-swap local search** exchanges one included ETF for one excluded ETF as long as that improves the score. A stronger classical control used 25 starts (greedy plus 24 seeded random feasible portfolios), followed by one-swap improvement. Greedy and local search are heuristics: they need exact enumeration or another certified optimizer before an optimum can be claimed.

### 3.4 QAOA design and experimental controls

QAOA encoded the ETF inclusion indicator with one qubit per fund. An RZ/RZZ cost layer represented the predicted-return-minus-risk score; an XY mixer preserved the number of selected funds. A classical COBYLA optimizer varied the circuit's rotation angles to increase the expected portfolio objective sampled from Aer. Outcomes were checked for valid cardinality.

The original ETF-count scaling used depth 2, a maximum of 50 COBYLA evaluations, 128 optimization shots, 1,024 final shots and 10 random starts per size. Later controlled experiments tested depth 1–3, cost-phase scales 30/100/300, three initial state strategies, the optimizer evaluation limit and an alternative Powell optimizer. The six held-out market dates reused **depth 3, phase scale 30**, the original spaced and rotated initial states and three fixed seeds, with a maximum of 50 evaluations, 128 optimization shots and 1,024 final shots. All planned trial outcomes, including unsuccessful ones, were retained.

## 4. Results

### 4.1 Initial January 2025 classical and QAOA scaling

On January 2025, the original 20-ETF exhaustive and greedy algorithms both selected **XLF, XLE, SPY**, reaching the exact objective score **0.044302**.

| ETFs available | Exact QAOA hits / 10 | Mean QAOA score gap | Mean QAOA simulator time |
|---:|---:|---:|---:|
| 6 | 10/10 | 0.000000 | 1.04 s |
| 10 | 8/10 | 0.000257 | 1.69 s |
| 15 | 0/10 | 0.003863 | 2.42 s |
| 20 | 0/10 | 0.015216 | 3.49 s |

This 40-trial experiment demonstrates decreasing QAOA reliability under a *fixed* depth-two budget as the candidate universe increased. Nested candidate sets also changed asset composition, so size is not the only possible explanation. An additional 18-trial robustness check with different ETF groups produced **5/9 exact hits at 10 ETFs** and **0/9 at 15 ETFs**, indicating sensitivity to which ETFs were included.

### 4.2 Circuit depth, phase scaling and initialization

The nine-configuration factorial experiment (three seeds per configuration, **27 trials**) compared depth 1/2/3 and phase scale 30/100/300 on the original January inputs. At phase scale 30:

| Depth | Mean gap to exact | Best QAOA score | Mean runtime |
|---:|---:|---:|---:|
| 1 | 0.017858 | 0.026444 | 1.23 s |
| 2 | 0.009378 | 0.040498 | 3.64 s |
| 3 | **0.004606** | **0.043425** | 10.57 s |

Increasing depth to three reduced the average gap but increased simulator time. Scale 30 produced the smallest mean gap among the measured depth-three configurations; this is a small, selected sample rather than proof of universal superiority. A further three-seed depth-three test raising COBYLA's evaluation allowance from 50 to 120 produced **the same 0.004606 mean gap**, so extra allowed iterations alone did not improve results. Comparing COBYLA with Powell at depth two also produced no advantage for Powell under the tested budgets.

Changing only the three starting ETFs, while preserving depth three, scale 30, optimizer and shot settings, produced the first exact January QAOA hits. Across ten starts per strategy (three exploratory and seven new confirmation seeds):

| Initial state method | Exact matches / 10 | Mean score gap |
|---|---:|---:|
| Original spaced positions | 2/10 | 0.003283 |
| Rotated positions | **4/10** | **0.001902** |
| Random feasible positions | 2/10 | 0.005705 |

Across these **30 trials**, QAOA sampled the true optimum **8 times**, including configurations that did not begin with the optimum. On the seven *new* confirmation seeds alone, the exact-hit counts were 2/7, 3/7 and 1/7 for spaced, rotated and random respectively. This suggests initialization can matter, but with only ten seeds per strategy the observed differences are not reliable statistical rankings.

### 4.3 Six previously untested historical decisions

To test whether January 2025 tuning generalized, the same depth-three configuration was used for six additional decisions: **March, June, September and December 2023; March and June 2024**. The Random Forest was retrained separately using only labels already known at each decision date; covariance came from the previous 36 months. Exhaustive search calculated the exact score for every month. We ran **36 total QAOA trials**, using two initial state methods and three seeds across all six dates.

| QAOA initial state | Trials | Exact optimum found | Mean gap to exact | QAOA wins over greedy |
|---|---:|---:|---:|---:|
| Original spaced | 18 | 3 | 0.006516 | 0 |
| Rotated | 18 | 2 | **0.003144** | 0 |
| **Total** | **36** | **5** | — | **0** |

Greedy matched exhaustive search in **all six months**; therefore QAOA could not exceed greedy's score on those problems. The rotated state had the lower mean gap but one fewer exact match than the spaced state. Taken together, these held-out results are more cautious than the January-only initialization findings: the algorithm sometimes reached the optimum, but it did not do so reliably and had no demonstrated advantage over greedy.

### 4.4 Expanded ETF problems and certified 6/40 optimum

The expanded universe used real adjusted price histories with its own forecasted returns and covariance matrix. Exhaustive search evaluated **all 3,838,380 six-of-forty combinations** (roughly **2.32 seconds** for the objective-only vectorized scan), confirming that the exact highest-scoring portfolio was **XLF, XLE, XLU, XLB, VFH, VDE**. Greedy and 25-start local search both matched the exact **0.071265** score.

| Portfolio | Classical greedy score | 25-start classical score | Is global optimum certified? |
|---|---:|---:|---|
| 3/20 (expanded input) | 0.074451 | 0.074451 | Yes |
| 6/40 | 0.071265 | 0.071265 | **Yes** |
| 12/80 | 0.065307 | 0.065307 | No |
| 24/160 | 0.062452 | 0.062452 | No |

No multi-start local search improved on greedy in the tested expanded-data snapshots. That indicates consistent local solutions, not mathematical proof of global optimality at 80 or 160 assets.

Limited-budget, frozen-data QAOA experiments on the enlarged problems produced:

| Portfolio | QAOA score | Matched classical reference | QAOA depth / budget | Status |
|---|---:|---:|---|---|
| 6/40 | **0.048243** | **0.071265 exact** | Depth 3; 25 optimizer evaluations | Seed 0 completed, next seed cancelled |
| 12/80 | 0.045642 | 0.065307 best-known classical | Depth 1; 6 evaluations | Pilot completed; optimizer not converged |
| 24/160 | 0.035916 | 0.062452 best-known classical | Depth 1; 6 evaluations | Pilot completed; optimizer not converged |

The 6/40 QAOA objective was **0.023021 below the known exact optimum** on its frozen-data run. Only **one** improved depth-three trial completed, so there is no statistically reliable 6/40 depth-three hit rate. The workflow's next seed was cancelled; it must not be treated as a zero score. The 80- and 160-qubit Qiskit Aer circuits executed and produced feasible samples, but their **six-evaluation pilots were intentionally under-optimized** and should not be presented as equal-budget comparisons.

Different large-scale GitHub Actions runs collected adjusted prices at different times, resulting in slightly different dataset hashes and benchmark numbers. Each numerical comparison here pairs QAOA with the classical results generated from **the same run's frozen inputs**; the cross-run scores should not be merged into a single controlled numerical average.

### 4.5 Exploratory risk-penalty robustness

As a separate, **post-hoc** extension, we varied the risk penalty from the primary \(\lambda=1\) to **10 and 100**, using the same six held-out dates, exact and greedy references, depth-three rotated QAOA and three seeds per date. All **36** quantum trials completed.

| Risk penalty | QAOA trials | Exact QAOA hits | QAOA beats greedy | Mean score gap |
|---:|---:|---:|---:|---:|
| 10 | 18 | 0 | 0 | 0.003700 |
| 100 | 18 | 1 | 0 | 0.020166 |

Greedy again matched exhaustive search in all **12 month-and-risk cases**. Higher risk penalties changed the objective and some selected portfolios, but did not produce a QAOA win over greedy. The experiment was selected after seeing the original results and is exploratory, not a preregistered confirmation.

## 5. Discussion

These results answer the professor's two technical concerns. **Qiskit itself is well-documented and used in published research**, and the tested implementation's score encoding and small-circuit simulator behavior matched classical calculations. Thus the original low QAOA scores cannot reasonably be attributed to Qiskit simply being unresearched or inherently defective. Parameter choices, optimization difficulty, finite shots, mixing and initialization are more plausible explanations, though this work does not isolate a single cause.

**Circuit depth and initial state mattered.** Depth three and varied initial states enabled exact hits on the original 20-ETF problem, while simply increasing COBYLA's evaluation limit did not help. On held-out dates the algorithm was less reliable. Its observed runtime also increased with circuit depth and problem size. These Qiskit Aer wall-clock measurements are not controlled benchmarks of a future physical quantum device.

**Classical search was exceptionally strong on these instances.** Greedy found the exact optimum in the original 20-ETF January decision, all six additional 20-ETF decisions, all twelve higher-risk decisions and the exact 6/40 expanded-data problem. Consequently, QAOA had no higher score available to surpass. An appropriate future benchmark would include other datasets where a classical greedy method has a *certified nonzero optimality gap*, along with a fixed computation budget and independent test periods.

## 6. Limitations

1. **Simulator, not hardware:** Qiskit Aer ran on classical machines; no quantum hardware speed or cost advantage can be inferred.
2. **Modeled objective, not investment profit:** Predicted return minus historical variance is not actual next-month profit or long-term Sharpe ratio. This work was an optimization study, not a live trading experiment.
3. **Limited independent dates:** Six held-out historical decisions provide useful validation but not broad coverage of market regimes.
4. **Parameter selection:** Depth-three/scale-30/rotated initialization was informed by January 2025 experiments. January is a tuning case, not an untouched final test.
5. **Strong classical references:** Greedy equaled exhaustive on every fully certified test reported. This prevents a QAOA score-based win, regardless of QAOA settings.
6. **Large-instance uncertainty:** At 12/80 and 24/160, 25-start local search is not a globally certified optimum and QAOA runs were minimal feasibility pilots.
7. **Resource and data consistency:** Runtimes include simulator/optimizer work but not all data preparation; CI environments and independently downloaded data snapshots vary. The improved 6/40 depth-three job yielded only one complete quantum trial before cancellation.
8. **Sampling and numerical settings:** Finite shots, optimizer settings and circuit depth may limit observed performance. Exact solution samples do not certify convergence of COBYLA's continuous optimization.
9. **ETF overlap:** Sector and broad-market funds may hold overlapping securities. A mechanically selected ETF portfolio is not guaranteed to be diversified or practical for investors.

## 7. Conclusion

Simulated QAOA could sample the exact best ETF combination, and its performance changed materially with circuit depth, initial state, candidate set and market date. However, across the tested original and expanded ETF portfolio problems, **QAOA did not outperform the classical greedy or exact search references on the same optimization objective**. Greedy was especially competitive: it matched the global optimum in all fully verified cases. QAOA's larger simulated circuits were technically executable, but limited-budget optimization remained difficult and its result quality was lower.

The main contribution is a reproducible, appropriately qualified experimental comparison of quantum and classical methods rather than a claim of quantum superiority. The findings support further research into harder benchmark instances, varied market environments, objective design and efficient quantum parameter optimization. They do not establish investment outperformance or a quantum computational advantage.

## 8. Reproducibility and references

**Project code**

- Original 20-ETF notebook: [data/03_twenty_etf_exploration.ipynb](../data/03_twenty_etf_exploration.ipynb)
- Original size-scaling notebook: [data/04 QAOA ETF Scaling Test.ipynb](../data/04%20QAOA%20ETF%20Scaling%20Test.ipynb)
- Held-out market validation: [scripts/final_walkforward_qaoa.py](../scripts/final_walkforward_qaoa.py)
- Larger classical exact benchmark: [scripts/final_large_prepare.py](../scripts/final_large_prepare.py)
- Larger QAOA simulation: [scripts/final_large_qaoa.py](../scripts/final_large_qaoa.py)
- Optional risk robustness: [scripts/final_risk_sensitivity.py](../scripts/final_risk_sensitivity.py)
- Results summary generator: [scripts/final_results_summary.py](../scripts/final_results_summary.py) (requires local trial CSV artifacts)

**Verified GitHub Actions evidence**

- [Original 40-trial scaling](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/44225096990)
- [27-trial depth/phase experiment](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/45260005221)
- [21-trial initialization confirmation](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/45263040991)
- [36-trial held-out six-month evaluation](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/45265578168)
- [Exact 6/40 benchmark](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/45265830611)
- [Frozen-data larger QAOA run; 40 seed 1 cancelled](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/45266001683)
- [36-trial higher-risk exploratory evaluation](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/45267442283)
- [Final code tests](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/45267442240)

**Scholarly and software references**

1. Javadi-Abhari, A., et al. (2024). *Quantum computing with Qiskit*. arXiv:2405.08810. https://arxiv.org/abs/2405.08810
2. Brandhofer, S., et al. (2023). *Benchmarking the performance of portfolio optimization with QAOA*. *Quantum Information Processing*, 22, article 25. https://doi.org/10.1007/s11128-022-03766-5
3. Qiskit Community. *Portfolio Optimization* (Qiskit Finance tutorial). https://qiskit-community.github.io/qiskit-finance/tutorials/01_portfolio_optimization.html
4. Qiskit Aer documentation. https://qiskit.github.io/qiskit-aer/
5. Source ETF data. https://github.com/manisahni/marketdata

**Final submission check:** This report is complete as a research narrative; the instructor's exact required report length, reference style, submission format and rubric were not provided here and must be checked before official submission.
