# Data dictionary

Primary inputs: adjusted daily prices from manisahni/marketdata (daily_adjclose.csv), monthly last observations; expanded prices from yfinance. No personal data. Notebook 02 is excluded from reported results.

| Variable | Meaning | Type | Units/source |
|---|---|---|---|
| Date, month, target_month, decision, decision_date | Observation, target, or prior-month decision date | date | Calendar date; source/script |
| ETF ticker, portfolio, indices | Fund identifier or selected asset list | string/integer list | Source/script |
| Adjusted close; ticker-named columns | Adjusted month-end price | float | Currency/share; marketdata/yfinance |
| last_month, last_3_months, last_6_months | Trailing price changes | float | Decimal return; derived |
| volatility_3m | Rolling standard deviation | float | Decimal monthly return; derived |
| mu, next_month | Forecast or realized target return | float/vector | Decimal return; RF/prices |
| cov, Sigma | Historical return covariance | matrix | Return squared; derived |
| risk, risk_lambda, lambda | Risk penalty | float | Multiplier |
| exact_score, greedy_score, local_score, swap_score, qaoa_score, random_score | Objective value by method | float | Predicted return minus penalty times variance |
| greedy_gap, gap_to_exact, gap | Exact score less heuristic score | float | Objective units |
| seed, optimizer_calls, valid_shots, random_budget | Trial control/count | integer | Count |
| optimizer_success, exact_hit, beat_greedy, beat_local, beat_random, beat_swap | Convergence or score comparison | boolean | True/false |
| seconds, runtime_seconds | Execution duration | float | Seconds |
| *_return, SPY, equal_weight | Realized portfolio return | float | Decimal return |
| input_sha256 | Forecast/covariance fingerprint | string | SHA-256 |
| etfs, selected, combination_count | Universe size, cardinality, candidate combinations | integer | Count |
| depth, phase_scale, maxiter, optimization_shots, final_shots | Circuit and optimization settings | number | Layers, multiplier, evaluations, counts |
| start_method, initial_selection | Initial basis state strategy and holdings | string | Labels |
| trials, cases, hard_cases, wins_*, exact_hits | Aggregated experiment counts | integer | Count |
| mean_gap, mean_greedy_gap | Mean optimality gap | float | Objective units |
| total_return | Compounded realized return | float | Decimal |
| annualized_volatility | Monthly sample SD times sqrt(12) | float | Decimal annualized |
| annualized_sharpe_rf_zero | Monthly mean divided by SD times sqrt(12) | float | Dimensionless; zero risk-free rate |
| wealth (strategy columns in classical_wealth.csv) | Compounded value from initial 1 | float | Value per initial dollar |

Full raw CSV headers are preserved in the evidence archive. Missing or cancelled trials must not be imputed. Scores are not realized returns. Expanded snapshots are separate and must not be mixed.
