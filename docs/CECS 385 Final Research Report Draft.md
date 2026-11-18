# CECS 385 — Quantum vs. Classical ETF Portfolio Selection

**Final research report — working draft**  
**University of Tennessee, Knoxville | November 2026**

## Abstract

For this project I compared simulated quantum computing with two classical methods to see which could select the best three-ETF portfolio under the same scoring formula. I tested exhaustive search, greedy search, and Quantum Approximate Optimization Algorithm (QAOA). The objective combines predicted monthly ETF return with a penalty for portfolio risk. Random Forest models estimated ETF returns from historical data. I compared the methods on a January 2025 portfolio decision, checked classical methods across six earlier months, and ran QAOA at different depths and ETF counts. In the final scaling experiment, QAOA reached the exact best portfolio score in 10 of 10 runs with six ETFs, 8 of 10 with ten ETFs, and none of the ten runs at either fifteen or twenty ETFs. Its average simulation runtime also increased with ETF count. Under the settings tested, exhaustive search was the reliable exact reference, greedy search performed well, and simulated QAOA did not show an advantage for the larger ETF groups. These findings concern the model's optimization score and simulation runtime, not guaranteed investing returns or real quantum hardware.

## 1. Research question

I wanted to see whether simulated quantum computing could compete with classical computing when selecting ETFs for the best predicted monthly portfolio score. I also wanted to compare accuracy, computing time, and how performance changes when more ETFs are available. Annual or longer-term realized performance is a separate goal that needs more backtesting than the current QAOA experiment provides.

My comparison focuses on three methods:

- **Exhaustive search** evaluates every possible three-ETF combination and identifies the best score under the chosen formula.
- **Greedy search** builds a portfolio one ETF at a time by taking the highest-scoring next addition. It is faster but is not guaranteed to find the exact optimum.
- **QAOA** uses a parameterized quantum circuit simulated with Qiskit Aer to sample candidate portfolios. It is not a real quantum computer.

## 2. Data and methods

### 2.1 ETF data and forecasts

The main notebook uses adjusted historical ETF prices from the public [manisahni/marketdata dataset](https://github.com/manisahni/marketdata). The universe contains twenty ETFs covering different stock sectors, broad markets, bonds, gold, and real estate. Prices are converted to monthly returns.

A Random Forest regressor forecasts the next month's return separately for each ETF using previous monthly returns, three- and six-month changes, and recent volatility. For the January 2025 decision, the forecast uses information available by the end of December 2024. Risk is estimated with a covariance matrix based on monthly returns from January 2022 through December 2024.

The project also performs walk-forward forecasting checks for six test months, July through December 2024. The reported evaluation contains 120 ETF-month predictions.

### 2.2 Portfolio objective

Every method selects exactly three equally weighted ETFs. Each selected ETF receives a one-third weight. The formula is

\[
\text{Score}(w) = \mu^T w - \lambda w^T \Sigma w,
\]

where \(\mu\) contains predicted monthly ETF returns, \(\Sigma\) is the monthly covariance matrix, and \(\lambda = 1.0\) is the chosen risk penalty. The goal is to **maximize the score**, not to maximize realized profit.

With twenty ETFs, selecting three gives \(\binom{20}{3} = 1{,}140\) possible portfolios.

### 2.3 QAOA setup

QAOA uses a circuit with one qubit for each candidate ETF and a constraint-preserving XY mixer so that each valid sampled portfolio contains three selected ETFs. The portfolio score is converted into the circuit's cost parameters. The notebook checks that the encoded quantum score matches the classical formula on all feasible selections.

The earlier depth test used twenty ETFs and compared QAOA depths 1 and 2 across ten random starts each. The later scaling experiment used **depth 2, COBYLA with at most 50 optimization iterations, 128 shots per optimizer evaluation, 1,024 final sampling shots, and ten random starts** for each ETF count.

For scaling, I tested nested ETF groups of 6, 10, 15 and 20 tickers. The same January 2025 forecasts and risk inputs were reused across each nested group. All four jobs were executed in GitHub Actions on November 18, 2026.

## 3. Results

### 3.1 Forecasting

The six-month forecasting evaluation reported the following mean absolute errors (MAE):

| Model | MAE |
|---|---:|
| Random Forest | 0.03757 |
| Simple forecasting baseline | 0.04881 |

Random Forest had the lower error on these 120 predictions. This result supports using its forecasts as inputs to the comparison, although it does not mean the resulting portfolios will outperform investments in practice.

### 3.2 Exhaustive search versus greedy search

For the January 2025 twenty-ETF decision, exhaustive search and greedy search both selected **XLF, XLE and SPY**, with a portfolio score of **0.044302**. In the July–December 2024 historical comparison, greedy matched the exact-search portfolio in **all six months**.

That does not mean greedy search is guaranteed to find the best portfolio for every dataset. It means it matched exhaustive search on the decisions tested here.

### 3.3 QAOA circuit-depth comparison

For the original twenty-ETF depth comparison, the saved notebook outputs show:

| QAOA depth | Trials | Mean score gap from exact optimum | Exact best score found |
|---|---:|---:|---:|
| 1 | 10 | 0.02113 | 0/10 |
| 2 | 10 | 0.01417 | 0/10 |

Depth 2 reduced the average gap, but neither depth found the exact best score in those repeated trials. Its average simulation runtime was also higher: approximately 5.35 seconds for depth 2 versus 2.51 seconds for depth 1 in the original notebook environment.

### 3.4 ETF-count scaling

The later experiment kept QAOA depth and optimization settings fixed while increasing the number of available ETFs:

| ETFs available | Three-ETF combinations | Exact optimum found | Mean QAOA score | Mean score gap | Mean simulation runtime |
|---:|---:|---:|---:|---:|---:|
| 6 | 20 | 10/10 | 0.042605 | 0.000000 | 1.04 s |
| 10 | 120 | 8/10 | 0.044045 | 0.000257 | 1.69 s |
| 15 | 455 | 0/10 | 0.040440 | 0.003863 | 2.42 s |
| 20 | 1,140 | 0/10 | 0.029086 | 0.015216 | 3.49 s |

The exact-hit rate dropped as the candidate set increased, and the average score gap and simulator runtime increased. The 20-ETF test showed the largest mean gap. The full scaling experiment completed **40 of 40 QAOA trials** successfully. Individual trial CSVs and charts were saved as GitHub Actions artifacts.

These scaling results and the older twenty-ETF depth results came from separate runs and settings. They should not be treated as one identical experimental series.

## 4. Discussion

The results show a clear difference among the three approaches. Exhaustive search is the benchmark because it checks every valid portfolio, and the 20-ETF problem is still small enough to evaluate all 1,140 combinations directly. Greedy search found the same best portfolios on the six historical decisions and the January 2025 decision, using much less searching.

Simulated QAOA performed well on the smallest ETF groups in the scaling experiment. With fifteen and twenty ETFs, however, it did not find the exact best score in any of the ten attempts for each size. Increasing circuit depth from one to two improved mean solution quality in the earlier experiment but did not eliminate the gap.

The runtime measurements are **implementation-specific**. They describe Python exhaustive and greedy searches compared with Qiskit Aer circuit simulation. They do not establish that a future physical quantum computer would be faster or slower. The measured optimizer evaluations and sampling shots describe computing effort, but no actual dollar-cost comparison has been completed.

## 5. Limitations

1. QAOA was tested with a simulator rather than physical quantum hardware.
2. The scaling test used **one January 2025 decision date**, not a multi-year quantum backtest.
3. The ETF groups were nested, meaning that adding ETFs also changed which assets were eligible. The test therefore mixes problem size and asset-composition effects.
4. Ten random starts at each size provide initial evidence but do not measure performance across many datasets or market conditions.
5. The score uses **forecast monthly return minus a risk penalty**; it is not realized monthly profit, annual return or Sharpe ratio.
6. The six-month realized-return comparison covers exhaustive and greedy search, not QAOA.
7. Simulator runtimes depend on the runner hardware and code implementation, so they are not reliable hardware-cost estimates.

## 6. Conclusion

In this project, exhaustive search was the most reliable method for finding the exact best score because the search space was still manageable. Greedy search was a useful practical alternative and matched exhaustive search across the historical months tested. QAOA was able to find the best score on small ETF groups, but its success rate decreased as the number of ETFs increased under the tested settings. Simulated runtime also increased.

Based on these results, **I cannot claim a quantum advantage** for this portfolio problem. The experiment instead shows why it matters to compare both solution quality and computing cost, rather than assuming the quantum approach will be better. Additional decision dates and ETF groups would be needed before making broader conclusions.

## 7. Reproducibility and sources

- [Main twenty-ETF experiment — Notebook 3](../data/03_twenty_etf_exploration.ipynb)
- [QAOA scaling experiment — Notebook 4](../data/04%20QAOA%20ETF%20Scaling%20Test.ipynb)
- [Verified QAOA scaling results](../results/QAOA%20ETF%20Scaling%20Results.md)
- [Full GitHub Actions execution and downloadable CSV artifacts](https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/44225096990)
- [Source price dataset: manisahni/marketdata](https://github.com/manisahni/marketdata)
- [IBM Qiskit documentation](https://docs.quantum.ibm.com/)
- [Qiskit Aer documentation](https://qiskit.github.io/qiskit-aer/)

**Before submission:** Verify the required report length and citation style from the course assignment; add properly checked scholarly citations, review any graphics, and complete a fresh run of Notebook 3 if full reproducibility is required. Avoid presenting the current objective scores as actual investment returns.
