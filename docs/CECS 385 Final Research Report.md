# Final report — text companion

This text is extracted from the final submission PDF (November 24, 2026). The PDF in the submission bundle is the authoritative formatted report, including figures and tables. See also [AI use statement](AI_USE_STATEMENT.md) and [data dictionary](DATA_DICTIONARY.md).

Quantum Versus Classical
ETF Portfolio Selection

Zachariah Seaford

CECS 385 — Final Research Project Report

University of Tennessee, Knoxville

November 24, 2026

## Abstract
This individual research study investigates whether the Quantum Approximate Optimization 
Algorithm (QAOA), simulated using Qiskit Aer, can compete with classical optimization when 
selecting exchange-traded funds (ETFs). Random Forest models forecast next-month ETF returns, 
and a historical covariance matrix estimates risk. Each method selects exactly three of twenty funds 
in the primary experiment, with equal weights and a common return-minus-variance objective. 
Exhaustive search establishes the exact optimum, while greedy search, local search and uniform 
random sampling provide classical comparisons. The initial scaling experiment achieved exact 
QAOA solutions in 10/10 trials at six ETFs and 0/10 at twenty ETFs. Subsequent depth and 
initialization changes produced eight exact hits in thirty trials on the January 2025 tuning instance 
and five in thirty-six trials on six additional market months. An exploratory extension screened 
seventy-two historical month-and-risk cases, identifying two in which greedy missed the optimum. 
QAOA beat greedy in two of six conditional trials, improving the positive objective score from 
0.007605 to 0.009561 in April 2023. However, local search and random sampling also reached the 
optimum. A separate thirty-month classical backtest returned 1.96% for optimized portfolios versus 
18.96% for SPY. Larger simulations demonstrated circuit feasibility up to 160 qubits, not 
converged optimization. The results support the feasibility of quantum-inspired portfolio research 
but do not demonstrate general quantum superiority, hardware speedup or investment 
outperformance. The study emphasizes exact benchmarks, transparent negative findings and the 
difference between modeled objectives and actual returns.

## 1. Introduction
Choosing investments requires a balance between expected return and uncertainty. An ETF 
combines multiple securities into a tradable fund. For an investor or portfolio analyst who must 
select a fixed number of funds, the decision becomes a discrete optimization problem rather than 
simply ranking returns. Three selections from twenty candidates create 1,140 feasible portfolios; six 
selections from forty create 3,838,380. This growth makes portfolio selection an accessible example 
of a broader computing problem: how to search a rapidly expanding set of choices efficiently.

Research question: Can Qiskit Aer–simulated QAOA find competitive ETF portfolios compared 
with classical exact and heuristic search, and how do circuit depth, initialization and problem size 
affect its solution quality? The working hypothesis is that QAOA can match exact solutions on 
small cases and sometimes outperform greedy on cases where greedy is suboptimal. A secondary 
expectation is that greater depth may reduce the optimality gap at the cost of runtime. The study 
addresses financial analysts and computing researchers interested in constrained optimization; it is 
not a recommendation to trade particular funds.

## 2. Literature and context
Orús, Mugel and Lizaso [1] describe financial optimization as a potential application of quantum 
computing. Their overview provides motivation for investigating combinatorial investment choices, 
but prospective usefulness should not be mistaken for evidence that a quantum method is faster or 
more accurate today. Brandhofer et al. [2] examine QAOA specifically for portfolio optimization, 
making the choice of circuit configuration and classical comparison central to evaluating 
performance. Together these sources motivate using an exact answer key rather than judging the 
quantum algorithm in isolation.

Buonaiuto et al. [3] investigate portfolio optimization using a related variational quantum 
eigensolver (VQE) approach and experiments on real quantum devices. That work highlights a 
distinction important to this project: running a circuit on a classical simulator is not equivalent to 
measuring the performance of a physical quantum computer. Qiskit provides the software 
framework for defining and executing circuits [4]; this project uses Qiskit Aer simulation, not 
quantum hardware. The findings therefore address the behavior of the implemented algorithm under 
simulation constraints.

The contribution here is an applied, reproducible comparison using monthly Random Forest 
forecasts and common portfolio constraints. Instead of comparing algorithms with different 
objectives, the exact, greedy, local and QAOA methods receive identical forecasts and covariance 
for each instance. The additional random sampling baseline tests whether expensive variational 
tuning offers a benefit beyond drawing feasible candidates. The study also separates estimated 
portfolio quality from observed investment returns, a distinction necessary when interpreting 
financial optimization results.

## 3. Research design and methods

### 3.1 Design and data

The design is a quantitative computational experiment with repeated seeds and historical decision 
dates. The original universe contains XLK, XLV, XLF, XLE, XLI, XLP, XLU, XLB, XLY, SPY, 
IWM, EFA, EEM, TLT, IEF, GLD, LQD, VNQ, TIP and HYG. Historical adjusted closing prices 
come from the marketdata repository [5]. Daily prices are aggregated to month-end; the final walk-
forward script uses January 2018 through June 2024 monthly prices. Missing or nonpositive 
monthly values are rejected. The study contains no human participants or individual account data.

The expanded universe uses adjusted ETF prices downloaded through yfinance, with 315 usable 
forecasts after completeness checks. The original source was insufficient for the planned 40-, 80- 
and 160-fund cases. The expanded source is therefore a methodological extension rather than a 
directly comparable replacement. Each larger experiment freezes its inputs so the algorithms within 
that experiment optimize the same problem. Independent downloaded snapshots may differ and 
scores are not pooled across them.

### 3.2 Forecasting and optimization

For each ETF, monthly returns are calculated as the current adjusted price divided by the previous 
month’s price, minus one. Random Forest features include the latest monthly return, three- and six-
month cumulative price changes, and the standard deviation of the previous three monthly returns. 
The label is next-month return. At a decision date, training uses only feature rows whose next-
month labels are already known. The final walk-forward model uses 100 trees, minimum leaf size 
three, random state seven, and one worker; the covariance estimate uses 36 prior monthly returns. 
The first assessment compares Random Forest with a simple forecasting baseline using mean 
absolute error (MAE).

The portfolio objective is J(w) = μᵀw − λwᵀΣw, where μ is the predicted monthly return vector, Σ is 
historical monthly covariance, and λ is a risk penalty. Exactly k out of n funds are selected; each 
receives weight 1/k and all others receive zero. The primary risk penalty is 1, with 10 and 100 tested 
separately. A larger score is preferred, but the score is neither a percentage investment return nor a 
Sharpe ratio.

Table 1. Optimization methods and controls.

Method Procedure

Exhaustive Enumerate all combinations and retain the highest 
score.

Greedy Add one ETF at a time using the best partial score 
with the final k denominator.

Local search Exchange one selected and one unselected ETF if 
the score improves; repeat until no improvement.

QAOA Encode cost with RZ/RZZ gates; XY mixer 
preserves exactly k holdings; tune angles with 
COBYLA and sample.

Random Draw feasible portfolios uniformly with 
replacement; match the total number of QAOA 
shots.

Table 1 summarizes the shared comparison. QAOA uses one qubit per candidate ETF. The cost 
layer represents the objective and the XY mixing layer moves between feasible selections. A 
classical optimizer adjusts circuit angles to maximize the expected sampled score. The best valid 
final measurement is recorded. Depth is the number of cost/mixer repetitions. The final historical 
settings were depth 3, phase scale 30, 50 maximum optimizer evaluations, 128 optimization shots 
and 1,024 final shots. Seeds 0–2 were used for each configuration. The exact-score gap is exact 
minus observed score; a gap of zero within 10 ⁸ indicates an exact hit.⁻

The original proposal/progress presentation focused on three classical/quantum comparisons and 
planned scaling and Sharpe tests. Later work added depth and initial-state experiments, additional 
historical decisions, a wider ETF dataset, one-swap and random baselines, and an exploratory hard-
case grid. The planned paired moving-block bootstrap for quantum Sharpe ratios was not performed 
because continuous QAOA returns were not collected. A separate descriptive classical backtest was 
substituted; it does not answer that original inferential question.

## 4. Results

### 4.1 Original forecasts and scaling

Across 120 ETF-month predictions in July–December 2024, Random Forest MAE was 0.03757 
versus 0.04881 for the simple baseline, approximately 23.0% lower. In the six original historical 
classical decisions, greedy matched the exact portfolio six times. For January 2025, both selected 
XLF, XLE and SPY at score 0.044302; the earlier single QAOA result was 0.027837 (XLF, XLU, 
LQD). The earlier ten-run depth comparison reported mean gaps 0.02113 (depth 1) and 0.01417 
(depth 2), and mean times 2.51 and 5.35 seconds; neither found the optimum.

Table 2. Initial QAOA scaling (10 trials per size).

ETFs Exact hits Mean gap Mean time (s)

6 10/10 0.000000 1.04

10 8/10 0.000257 1.69

15 0/10 0.003863 2.42

20 0/10 0.015216 3.49

Table 2 shows the later completed 40-trial scaling experiment. An additional group-composition 
check found five exact hits in nine 10-ETF trials and zero in nine 15-ETF trials.

Figure 1. Exact-hit rate in the original scaling experiment (10 trials per size).

### 4.2 Circuit tuning

The later factorial study compared three depths and three phase scales with three seeds per setting. 
At scale 30, gaps for depths 1, 2 and 3 were 0.017858, 0.009378 and 0.004606; mean times were 
1.23, 3.64 and 10.57 seconds. The depth-three gap was 74.2% lower than depth one. Raising the 
evaluation allowance from 50 to 120 did not improve that gap. Across ten trials per initial-state 
method, spaced, rotated and random starts achieved 2, 4 and 2 exact hits respectively. The rotated 
mean gap was 0.001902, versus 0.003283 and 0.005705 for spaced and random starts.

### 4.3 Historical validation and expanded simulations

Across six distinct historical months (March, June, September and December 2023; March and June 
2024), QAOA reached the exact solution in five of 36 trials. Spaced starts achieved 3/18 hits (mean 
gap 0.006516); rotated starts achieved 2/18 (mean gap 0.003144). Greedy matched the exact 
objective on all six dates. A separate risk sensitivity test with penalties 10 and 100 produced one 
exact hit in 36 trials and no greedy wins. Greedy was exact in all 12 month-and-risk cases.

Table 3. Expanded portfolio simulations using matched inputs.

k/n Classical score QAOA score Reference

6/40 0.071265 0.048243 Exact

12/80 0.065307 0.045642 Best known

24/160 0.062452 0.035916 Best known

Table 3 shows the larger feasibility experiments. The 6/40 exhaustive scan checked 3,838,380 
combinations in about 2.32 seconds, and greedy matched its optimum. Only one depth-three 
quantum seed completed; the next was cancelled. The 80- and 160-qubit pilots used depth 1 and six 
evaluations without convergence. Their classical references are not certified global optima.

### 4.4 Hard-case extension

The fixed exploratory grid screened 24 additional months from January 2022 through May 2024, 
excluding previous validation months, at risk penalties 1, 10 and 100. Greedy was exact in 70 of 72 
cases. Three QAOA seeds were run on each of the two remaining cases. Table 4 reports all six 
outcomes.

Table 4. Objective scores for the two certified greedy misses.

Month / λ Greedy Exact QAOA 0 QAOA 1 QAOA 2

Sep 2022 / 100 −.024080 −.018745 −.024992 −.035360 −.043169

Apr 2023 / 10 .007605 .009561 .009561 .009561 .006939

In April, two seeds selected XLV, XLU and TLT, improving the positive greedy score by 0.001956 
(25.7%). Local search and random sampling also reached the exact optimum in both cases; QAOA 
beat neither. Random sampling used 7,424 draws per trial from 1,140 feasible combinations. All six 
QAOA optimizers reported nonconvergence. The successful workflow compiled the scripts and 
passed six unit tests [6].

### 4.5 Realized returns

A separate continuous classical backtest rebalanced monthly from January 2022 to June 2024 using 
risk penalty 1. It used returns observed after each selection, with no trading costs or taxes. Table 5 
reports total compounded returns, annualized standard deviation of monthly returns and annualized 
Sharpe ratios calculated with a zero risk-free rate.

Table 5. Classical investment backtest (30 months).

Strategy Total return Annualized vol. Sharpe

Exact / greedy / local 1.96% 16.23% 0.127

Equal-weight 20 ETFs 5.05% 14.69% 0.205

SPY 18.96% 18.66% 0.464

Figure 2. Gross cumulative wealth from the classical backtest, starting with $1.

Figure 2 displays the wealth paths corresponding to Table 5. The three optimization methods had 
identical realized returns. SPY had the highest cumulative return and Sharpe ratio over the 
measured window. No continuous QAOA strategy was backtested; the hard-case file records only 
its selected months.

## 5. Discussion
The results partially support the hypothesis. QAOA can match a mathematical optimum and 
occasionally outperform a weak heuristic, but no advantage over stronger classical controls was 
established. The depth experiment is consistent with the importance of configuration emphasized by 
Brandhofer et al. [2], while the different initialization results illustrate why one successful seed 
cannot establish reliability. The 25.7% improvement is relative to one positive model objective, not 
a financial return. The two wins occurred on the same instance, not two independent market 
conditions. The classical backtest further shows that better modeled objectives do not automatically 
translate into better realized returns.

## 6. Limitations
All circuits ran on classical hardware using Qiskit Aer; simulator runtime cannot establish quantum 
hardware speedup. The 80- and 160-qubit pilots were deliberately under-optimized. Only one 
completed 40-qubit depth-three seed is available. The fixed ETF universe, overlapping holdings, 
short historical window and selected market regimes limit generalization. Parameter settings were 
informed by January 2025; the later hard-case grid was exploratory and conditional on greedy 
failure. Random sampling matched total shots, not elapsed time or computational cost, and used 
cached scores; it also retained the best draw across the full budget while QAOA retained the best 
final sample. This is not a symmetric resource benchmark. The earlier proposed normalized-gap 
threshold was not evaluated as a formal matched-budget success criterion. The 30-month backtest 
excludes trading frictions, uses a zero risk-free rate and does not include continuous QAOA returns 
or a paired bootstrap. All original notebooks have not been freshly rerun end-to-end.

## 7. Ethical, social and disciplinary considerations
The data describe publicly available ETF prices, not identifiable people. No participant consent or 
personal identifiers were collected. Nonetheless, data provenance matters: source and snapshot 
differences must be disclosed, and redistribution should comply with provider terms. The fixed list 
of ETFs can introduce selection and survivorship bias; it excludes many products and does not 
represent all investor circumstances, regions or risk preferences. Equal weighting and variance 
penalization are simplifying choices, not universal definitions of fairness or suitability. Reporting 
the results as individualized financial advice could mislead investors, especially those with limited 
ability to absorb losses. To reduce this risk, objective scores are distinguished from actual returns, 
negative results and cancelled runs are retained, and simulation is explicitly distinguished from 
hardware. Computational resource use also matters: expensive simulation should be justified by 
evidence, rather than assumed valuable because it is quantum. The study compares transparent 
baselines and documents assumptions so readers can challenge the conclusions.

## 8. Conclusions and recommendations
Simulated QAOA achieved exact solutions and beat greedy in two conditional trials, but it did not 
outperform local search or random sampling. The evidence does not establish a general quantum 
advantage. Future work should preselect independent hard instances, match computational budgets, 
report optimizer convergence and use stronger classical solvers. Financial performance should be 
evaluated separately using continuous out-of-sample returns, realistic costs and a predeclared 
statistical procedure. Physical hardware comparisons would require comparable circuit and resource 
measurements.

## 9. Personal reflection
Reflection draft for student review: This project helped me understand that a fair comparison is 
more important than finding a favorable result. The hardest technical issue was separating a poor 
optimizer outcome from an implementation error and identifying cases where greedy was not 
already optimal. Explaining the difference between the model score and investment returns also 
required translating technical results into language that a nontechnical audience could understand. If 
I repeated the study, I would define the benchmark grid and resource budget earlier, preserve frozen 
inputs from the start, and plan the continuous return evaluation before tuning. I would also verify 
each notebook from a clean environment before presenting the final results.

## References
[1] R. Orús, S. Mugel, and E. Lizaso, “Quantum computing for finance: Overview and prospects,” 
Reviews in Physics, vol. 4, art. 100028, 2019. doi: 10.1016/j.revip.2019.100028.

[2] S. Brandhofer et al., “Benchmarking the performance of portfolio optimization with QAOA,” 
Quantum Information Processing, vol. 22, art. 25, 2023. doi: 10.1007/s11128-022-03766-5.

[3] G. Buonaiuto et al., “Best practices for portfolio optimization by quantum computing, 
experimented on real quantum devices,” Scientific Reports, vol. 13, art. 19434, 2023. doi: 
10.1038/s41598-023-45392-w.

[4] A. Javadi-Abhari et al., “Quantum computing with Qiskit,” arXiv:2405.08810, 2024. 
https://arxiv.org/abs/2405.08810

[5] M. Sahni, “marketdata,” GitHub, daily_adjclose.csv. https://github.com/manisahni/marketdata 
(accessed Nov. 2026).

[6] Z. Seaford, “CECS-385-Research-Project,” GitHub, 2026. 
https://github.com/zachariahseaford/CECS-385-Research-Project. Final extension run: 
https://github.com/zachariahseaford/CECS-385-Research-Project/actions/runs/45393056795.

## Appendix A. Data dictionary
Table A1. Primary inputs and derived variables.

Variable Meaning / type Units / source

Date, month, decision Date/time; observation, target, 
decision

Calendar date; source/script

ETF ticker / indices String / integer list; selected 
assets

Identifier; source/script

Adjusted close Float; adjusted month-end price Currency per share; 
marketdata/yfinance

last_month, last_3_months, 
last_6_months

Float; trailing price returns Decimal return; derived

volatility_3m Float; rolling return std. dev. Decimal; derived

μ / next_month Float; forecast / realized target Decimal return; RF/prices

Σ / risk Matrix / float; covariance / 
penalty

Return squared / multiplier; 
derived

exact_score, greedy_score, 
local_score, qaoa_score, 
random_score

Float; objective by method Objective units; scripts

greedy_gap Float; exact minus greedy Objective units; screening

seed, optimizer_calls, 
valid_shots, random_budget

Integer; trial controls/counts Count; scripts

optimizer_success, exact_hit, 
beat_greedy, beat_local, 
beat_random

Boolean; convergence or 
comparison

True/false; scripts

seconds Float; QAOA simulation runtime Seconds; timer

*_return, SPY, equal_weight Float; observed portfolio return Decimal return; prices

input_sha256 String; hash of 
forecast/covariance

SHA-256; script

The supplementary CSV files contain the full trial-level records. The wealth series is compounded 
from monthly returns; annualized volatility and Sharpe ratios are derived from the same 30-month 
sequence.

## Appendix B. Code and reproducibility
Repository: https://github.com/zachariahseaford/CECS-385-Research-Project. From the repository 
root, use Python 3.11; the final successful workflow recorded NumPy 2.4.6, pandas 2.3.3, scikit-
learn 1.9.1, SciPy 1.17.1, Qiskit 2.6.2, Qiskit Aer 0.18.4, Matplotlib 3.11.2 and pytest 9.2.0. Earlier 
experiments may use different versions. The workflow and its artifacts provide the measured 
evidence; downloading live prices again may change results.

python -m pip install -r requirements.txt

python -m pip install yfinance matplotlib pytest

PYTHONPATH=scripts python -m pytest tests/test_portfolio.py 
tests/test_large_portfolio_qaoa.py

python scripts/final_walkforward_qaoa.py --smoke

python scripts/final_walkforward_qaoa.py

python scripts/portfolio_backtest.py

python scripts/hard_portfolio_benchmark.py

Exhaustive search excerpt from the progress presentation (adapted for readability):

all_portfolios = list(itertools.combinations(range(len(TICKERS)), CHOOSE))

scores = np.array([portfolio_score(p) for p in all_portfolios])

best_i = int(np.argmax(scores))

classical_choice = all_portfolios[best_i]

See the repository reproduction guide for expanded universe workflows, frozen inputs and earlier 
experimental artifacts. The attached evidence archive includes the final extension’s monthly prices, 
raw trials, screening data, returns, summary tables and chart.

## Appendix C. AI Use Statement
ChatGPT was used for literature discovery, explaining algorithms, code generation and revision, 
GitHub workflow configuration, analysis summaries, report drafting and editing, and slide creation. 
AI-generated or AI-edited material includes portions of Python scripts, workflow files, 
documentation, figures prepared from measured values, report prose and presentation text. The 
historical price observations were obtained from documented market data sources; they were not 
generated by AI. Experimental outputs came from executed GitHub workflows rather than invented 
measurements. ChatGPT-assisted output was revised to distinguish objective scores from actual 
returns, to disclose nonconvergence and cancelled runs, and to avoid unsupported claims of 
quantum advantage. The final extension was checked against the raw trial CSV, screening 
summary, backtest summary and six passing unit tests; scholarly publication titles and DOI records 
were checked against publisher or bibliographic records. The student must verify the final text, 
personally review source claims and code, confirm whether any other AI tools were used, and revise 
the reflection to accurately describe their own experience. This disclosure is a draft to confirm 
before submission.

	Abstract
	1. Introduction
	2. Literature and context
	3. Research design and methods
	3.1 Design and data
	3.2 Forecasting and optimization

	4. Results
	4.1 Original forecasts and scaling
	4.2 Circuit tuning
	4.3 Historical validation and expanded simulations
	4.4 Hard-case extension
	4.5 Realized returns

	5. Discussion
	6. Limitations
	7. Ethical, social and disciplinary considerations
	8. Conclusions and recommendations
	9. Personal reflection
	References
	Appendix A. Data dictionary
	Appendix B. Code and reproducibility
	Appendix C. AI Use Statement
