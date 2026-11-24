# CECS 385 — Quantum vs. Classical ETF Portfolio Selection

**Final research project · University of Tennessee, Knoxville · November 2026**

This project asks whether Qiskit Aer–simulated Quantum Approximate Optimization Algorithm (QAOA) can select high-scoring ETF portfolios competitively with classical exhaustive and greedy search, under the **same predicted return-minus-risk objective**. We use Random Forest return forecasts, exactly selected and equally weighted ETFs, a cardinality-preserving quantum mixer, and fully recorded simulator experiments.

**Final conclusion:** QAOA sometimes sampled the mathematically optimal portfolio and **beat greedy in two of six conditional exploratory trials**, both April 2023 at risk penalty 10. It did not beat local search or shot-budget-matched random sampling. Greedy was optimal in 70 of 72 additional screening cases. No quantum advantage was demonstrated. A separate classical backtest distinguishes modeled scores from realized returns.

## Start with the final deliverables

- **Final submission PDF: `Seaford_CECS385_FinalReport.pdf`** — supplied in the submission ZIP; [matching report text](docs/CECS%20385%20Final%20Research%20Report.md) includes all nine sections and appendices
- **[Final presentation notes and professor questions](docs/CECS%20385%20Final%20Presentation%20Notes.md)** — nine-slide speaking outline and direct explanations
- **[Final reproduction guide](docs/Final%20CECS%20385%20Reproduction%20Guide.md)** — commands, experimental settings and exact/approximate baseline distinctions
- **[Submission checklist](docs/CECS%20385%20Submission%20Checklist.md)** — what is complete and what to verify against the course rubric

## Final experiment highlights

| Experiment | Measured outcome |
|---|---|
| Original 3/20 January 2025 | Exact and greedy score 0.044302, portfolio XLF/XLE/SPY |
| Original 6/10/15/20 QAOA scaling | Exact hits: 10/10, 8/10, 0/10, 0/10 |
| Improved depth-three initialization | **8 exact hits / 30 trials** across three start strategies |
| Six held-out historical months | **5 exact QAOA hits / 36**, no wins over greedy |
| Exhaustive six-of-forty benchmark | **3,838,380 combinations**, greedy exactly optimal, score ~0.071265 |
| Expanded 12/80 and 24/160 | QAOA simulation feasible in short pilots; below classical reference |
| Higher-risk exploratory extension | 36 QAOA trials; 1 exact hit; no QAOA wins over greedy |
| Hard-case extension | 72 screens; two greedy misses; QAOA wins 2/6, no wins over local or random |
| Classical 30-month backtest | Optimized strategies 1.96%, equal-weight 5.05%, SPY 18.96% gross return |

**Important:** The expanded ETF dataset is different from the original 20-ETF source. Only compare QAOA and classical numerical scores when both were computed from the **same underlying ETF universe, forecasts and covariance**.
 
[Verified extension results](results/verified_extension/README.md)

## Code and repeatability

- [Original exploratory notebook](data/03_twenty_etf_exploration.ipynb)
- [QAOA scaling notebook](data/04%20QAOA%20ETF%20Scaling%20Test.ipynb)
- [Six-month walk-forward QAOA evaluation](scripts/final_walkforward_qaoa.py)
- [Exact 6-of-40 and expanded classical baselines](scripts/final_large_prepare.py)
- [Frozen-data expanded QAOA circuit evaluation](scripts/final_large_qaoa.py)
- [Risk-penalty exploratory experiment](scripts/final_risk_sensitivity.py)
- [Results report generator](scripts/final_results_summary.py)
- [Scoring and phase-encoding tests](tests/test_large_portfolio_qaoa.py)

Python 3.11.18; `requirements.txt` is a flexible environment, including yfinance and pytest. For the final extension, install `requirements-final-extension.txt` with the measured versions: NumPy 2.4.6, pandas 2.3.3, scikit-learn 1.9.1, SciPy 1.17.1, Qiskit 2.6.2, Qiskit Aer 0.18.4, Matplotlib 3.11.2 and pytest 9.2.0. Earlier runs may differ; yfinance was not used in the final extension and its earlier version is not verified.

```bash
python -m pip install -r requirements.txt
python -m pip install -r requirements-final-extension.txt
PYTHONPATH=scripts python -m pytest tests/ -q
python scripts/final_walkforward_qaoa.py --smoke
python scripts/final_walkforward_qaoa.py
```

For expanded universe benchmarking, follow the reproduction guide and save a consistent adjusted-price snapshot. Full QAOA for 40/80/160 may require substantial time/resources; 80/160 studies are deliberately limited **feasibility pilots**.

## Scientific integrity

All experiments use **Qiskit Aer simulation**, not physical quantum hardware. Exhaustive solutions are exact under the model, but optimization scores are not future or realized returns. A six-of-forty QAOA depth-three run completed one seed and then was cancelled; its uncompleted seed is not counted as a failed portfolio. Raw measured outputs are preserved in the separate submission evidence ZIP; the original Actions links are provenance, not permanent storage. Notebook 02 is an excluded synthetic/CSV demonstration, not research evidence.

[Project workflow history](https://github.com/zachariahseaford/CECS-385-Research-Project/actions) · [Original market data](https://github.com/manisahni/marketdata) · [Qiskit Finance portfolio tutorial](https://qiskit-community.github.io/qiskit-finance/tutorials/01_portfolio_optimization.html)

## Submission documentation

- [Data dictionary](docs/DATA_DICTIONARY.md)
- [AI Use Statement (Appendix C companion)](docs/AI_USE_STATEMENT.md)
- [Data sources and notebook scope](data/README.md)
- [Artifact manifest](docs/ARTIFACT_MANIFEST.md)

Primary fields: date/decision/target month (calendar dates); ticker (identifier); adjusted close (currency/share); trailing returns and volatility (decimal); forecasts and realized returns (decimal); covariance (return squared); risk penalty (multiplier); algorithm scores and gaps (objective units); seed, evaluations, shots (counts); hit/win/convergence (boolean); runtime (seconds); SHA-256 (fingerprint). See the dictionary for additional output fields. Run the full test suite including `tests/test_qaoa_scaling.py`; the final extension originally verified six tests, not the whole notebook suite.
