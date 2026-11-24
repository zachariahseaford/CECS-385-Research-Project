# CECS 385 — Final Submission Checklist

**Prepared November 23, 2026.** This checklist distinguishes verified research work from instructor-specific requirements that are not available in the project materials.

## Research deliverables — complete

- [x] Research question, hypothesis and scope in [final report](CECS%20385%20Final%20Research%20Report.md)
- [x] Data sources and Random Forest forecast methodology
- [x] Portfolio formula and cardinality constraint explained
- [x] Exhaustive, greedy, local-search and QAOA algorithm explanations
- [x] Original 40-trial QAOA size-scaling results
- [x] Qiskit software credibility and published QAOA portfolio literature
- [x] Circuit scoring validation and dual-Aer simulation check
- [x] Depth/phase/optimizer/initial-state tuning study, including negative results
- [x] Initialization confirmation on previously untested random seeds
- [x] QAOA evaluation across six market months not used for January tuning
- [x] Exact 6-of-40 portfolio result from all 3,838,380 combinations
- [x] Classical heuristic analysis on 12-of-80 and 24-of-160
- [x] 80- and 160-qubit simulation feasibility pilots, with actual resource limits
- [x] Completed exploratory higher-risk objective sensitivity
- [x] Cancelled QAOA 40-qubit trial disclosed as **not completed**
- [x] Separate results for original and extended data sources
- [x] Limitations and defensible negative conclusion
- [x] Full GitHub Actions links for traceability
- [x] Final presentation speaking notes and professor Q&A

## Code and data — verified / qualified

- [x] Final code was submitted via GitHub, with verification actions covering compilation, objective encoding, unit tests and a held-out-data smoke run
- [x] Six-month 36-trial workflow completed successfully
- [x] Exact expanded 6/40 classical workflow completed successfully
- [x] 80/160 quantum feasibility workflows completed
- [x] Optional higher-risk 36-trial workflow completed
- [x] CI archive links supplied for original trial CSVs, final snapshots and models
- [ ] Full rerun of *every* original exploratory notebook from a fresh clone **not independently reverified** in this final pass
- [ ] Standalone local CSV files are not committed as static GitHub repository assets; measured exports are in GitHub Actions artifacts
- [ ] The 40-qubit depth-3 follow-up has **one completed seed and one cancelled seed**; it must not be represented as a repeated full-budget study

## Instructor-specific checks before submission

- [ ] Confirm the assignment rubric, required sections and page/word count
- [ ] Confirm required citation style and whether a title page is mandatory
- [ ] Confirm whether a PDF, Word document, GitHub URL, slides or zipped code is expected
- [ ] Confirm whether a final video/presentation is required and its maximum length
- [ ] Review academic integrity and collaboration/AI-use disclosure rules for this course
- [ ] Proofread names, course identifier and any instructions specific to your professor
- [ ] Add and check screenshots/figures if the rubric requires them
- [ ] Submit the final deliverables through the university's actual assignment portal; **no course submission has been made by this GitHub workflow**

## Suggested submission links

- [Canonical final research report](CECS%20385%20Final%20Research%20Report.md)
- [Final presentation notes](CECS%20385%20Final%20Presentation%20Notes.md)
- [Reproduction guide](Final%20CECS%20385%20Reproduction%20Guide.md)
- [Project repository](https://github.com/zachariahseaford/CECS-385-Research-Project)

## Final scientific statement

> QAOA sometimes found the exact best portfolio score. We demonstrated that depth and initial state influence QAOA performance, but it did not outperform classical greedy search in the fully verified benchmarks. Our Qiskit Aer experiments do not show quantum computational speedup or realized investment gains.

**Stop rule:** Additional unplanned QAOA reruns are not necessary for the current study. Improvements should be justified by a new research question and evaluated on distinct test cases, not by rerunning random seeds until a favorable outcome appears.


## November 24 update — final exploratory extension

The original no-win result applies only to the original experiments. The additional 72-case screening identified two greedy failures; QAOA matched the exact optimum and beat greedy in two of six conditional trials, both April 2023 at risk penalty 10. It beat neither one-swap local search nor random sampling (which found the optimum in all six trials). No quantum advantage was demonstrated. The separate 30-month classical backtest returned 1.96% for optimized portfolios versus 5.05% equal-weight and 18.96% SPY, gross of costs, with zero-risk-free-rate Sharpe ratios of 0.127, 0.205 and 0.464. Six unit tests passed. Run `python scripts/portfolio_backtest.py` and `python scripts/hard_portfolio_benchmark.py` to reproduce the extension. [Verified results](../results/verified_extension/README.md).
