# CECS 385 — Final Presentation Notes

**Presentation title:** Quantum Versus Classical ETF Portfolio Selection  
**Suggested length:** 5–7 minutes, followed by questions. These notes are a speaking guide, not a finished slideshow.

## Slide 1 — Research question
**Question:** Can QAOA select an ETF portfolio as effectively as traditional computer algorithms?

**Say:** “I wanted to test whether quantum optimization could compete with classical methods when choosing ETFs. I compared three methods—exhaustive search, greedy search and QAOA—on exactly the same portfolio score. I used the Qiskit Aer simulator, not actual quantum hardware.”

## Slide 2 — How the portfolio score works
Show: **Predicted next-month return − risk penalty**.

- Random Forest estimates returns from previous monthly returns, three/six-month changes and volatility.
- Risk is estimated from historical covariance.
- The algorithms must select exactly three ETFs in the original study.
- All selected ETFs are equally weighted.

**Say:** “A higher score is better under my model, but it is not the same thing as making more money.”

## Slide 3 — Why compare to exhaustive and greedy?
- **Exhaustive:** tests all valid combinations and proves the highest score at manageable size.
- **Greedy:** makes sequential ETF selections, fast but not always guaranteed optimal.
- **QAOA:** builds a quantum circuit and uses COBYLA to tune its parameters and sample portfolios.

**Important:** QAOA cannot exceed the exact mathematical optimum on the same inputs. A real algorithmic win would require beating a *suboptimal* heuristic, or finding the optimum using fewer properly measured resources.

## Slide 4 — Initial scaling results (January 2025)

| ETFs | Exactly 3 selected | Exact QAOA hits / 10 |
|---|---:|---:|
| 6 | 20 combinations | 10/10 |
| 10 | 120 combinations | 8/10 |
| 15 | 455 combinations | 0/10 |
| 20 | 1,140 combinations | 0/10 |

**Say:** “As the candidate set grew, QAOA had a harder time finding the exact answer under a fixed circuit depth and shot budget.”

## Slide 5 — Improving QAOA
The depth/phase experiment tested 27 runs and showed:
- Depth 1, scale 30: average gap 0.017858
- Depth 2, scale 30: average gap 0.009378
- Depth 3, scale 30: average gap 0.004606

Depth 3 improved solution quality but cost more simulator time.

The next 30-trial initial-state study at depth 3 produced:
- Original positions: **2/10** exact hits
- Rotated positions: **4/10** exact hits
- Random positions: **2/10** exact hits

**Say:** “Changing the circuit depth and where the search started helped QAOA reach the exact answer. That shows the settings mattered.”

## Slide 6 — Does it generalize? Six more months
We repeated the depth-3 experiment at six different historical market months, with 36 QAOA trials.

- QAOA found **5 exact solutions out of 36**.
- It beat greedy **0 out of 36** times.
- Greedy matched exhaustive on **all six dates**.

**Say:** “The January improvement was real for that problem, but it didn’t automatically generalize to other market months.”

## Slide 7 — Larger ETF analysis
Scenarios: **6/40, 12/80, 24/160**.

For 6/40, exhaustive search checked all **3,838,380** combinations and confirmed greedy had the exact optimum **0.071265**.

The frozen-data improved QAOA depth-3 pilot scored **0.048243** for its completed seed. Its second seed was cancelled. At 12/80 and 24/160, short depth-1 QAOA pilot scores were **0.045642** and **0.035916**, below the classical reference scores **0.065307** and **0.062452**.

**Say:** “My simulator could execute 80- and 160-qubit circuits, but those were intentionally short feasibility tests. The results don’t demonstrate that QAOA was fully optimized.”

## Slide 8 — Is Qiskit trustworthy?
- Qiskit is an established IBM-supported, open-source quantum software framework with published academic literature.
- The Qiskit community has a QAOA portfolio-optimization tutorial.
- Our six-qubit statevector and matrix-product-state comparisons matched closely.
- Four code tests validated the cost-phase calculation and classical score.

**Say:** “The low QAOA results are not evidence that Qiskit is untested software. Circuit and optimization settings affected the performance, though my tests can’t rule out every possible implementation issue.”

## Slide 9 — Conclusion
**We did not demonstrate a quantum advantage.**

- QAOA sometimes matched the exact score.
- Greedy repeatedly found the exact best answer on the instances we could certify.
- Increasing depth and changing initialization improved QAOA's January results.
- Simulator runtime and optimization difficulty increased on larger problems.
- These are objective scores from forecasts, **not actual investment returns**.

**Say:** “The project shows why it is important to benchmark a quantum approach against a strong classical baseline rather than assume the quantum method is better.”

## Likely professor questions

**Why didn't QAOA beat greedy?**  
“On every fully verified benchmark, greedy already reached the exact optimum. QAOA could only tie, not surpass it.”

**Does that make the study unsuccessful?**  
“No. I tested a hypothesis, validated the implementation, showed sensitivity to circuit settings, and documented where the simulated approach does and does not compete.”

**Is Qiskit responsible for the low QAOA scores?**  
“There is no evidence of a fundamental Qiskit failure in my checks. I confirmed the objective encoding and compared two simulator methods, and I found that QAOA depth and initialization changed the results.”

**Did you prove an 80- or 160-qubit quantum advantage?**  
“No. I demonstrated that those circuits could be simulated in short pilots. They didn't beat my classical references, and I did not fully optimize them.”

**Are the scores investment returns?**  
“No. They're forecast return minus risk for an equal-weighted portfolio. Real trading returns and Sharpe ratios would need a separate backtest.”

**What would you do next?**  
“I'd build or select harder, independently validated test instances where greedy is known to miss the optimum, test more market dates, and analyze circuit resources on actual quantum hardware.”

## Sources for the presentation

- [Final full research report](CECS%20385%20Final%20Research%20Report.md)
- [Original scaling experiment](../results/QAOA%20ETF%20Scaling%20Results.md)
- [Initialization confirmation](../results/November%2023%20Initialization%20Findings%20and%20Remaining%20Tests.md)
- [Original 20-ETF simulation](../data/04%20QAOA%20ETF%20Scaling%20Test.ipynb)
- [Qiskit academic paper](https://arxiv.org/abs/2405.08810)
- [Peer-reviewed portfolio QAOA benchmarking](https://doi.org/10.1007/s11128-022-03766-5)
