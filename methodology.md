# CECS 385 Research Methods

## Question
How often does simulated QAOA find the optimal equal-weight, exactly-three-ETF portfolio, and how do solution quality, feasibility and runtime compare with greedy and exhaustive classical methods as the candidate asset universe grows?

## Shared inputs
For a fair optimization comparison, every method uses the same estimated return vector `mu`, covariance matrix `Sigma`, and risk-aversion `lambda`.

Objective: `score = mu @ weights - lambda * weights.T @ Sigma @ weights`; each selected weight is 1/3 and all other weights are 0.

## Baselines and scope
- Exhaustive: enumerates every group of 3; exact optimum for the defined objective, not guaranteed best future return.
- Greedy: adds the ETF with the greatest immediate objective improvement. Fast but not guaranteed optimal.
- QAOA: simulated hybrid quantum-classical solver with a three-ETF constraint penalty. Check feasibility, score and seed variation.

QAOA is intended only for manageable small qubit counts. The 100-ETF experiment is a **classical reference benchmark**; it does not claim to run a 100-qubit statevector simulation.

## Proposed settings
- Asset counts: small QAOA 6, 8 (optional 10 and 12); classical 10, 25, 50, 75, 100.
- Exactly 3 investments, equal weight.
- Risk aversion `lambda = 1.0` initially; sensitivity tests at 0.5, 2.0 and 5.0.
- QAOA depth p=1 (optional 2), 1024 sampled bitstrings, COBYLA 30 iterations in quick mode; 10 seeds in full mode.
- Constrain selection using `A * (sum(x) - 3)^2`, verify penalty sufficiency; choose best feasible sampled bitstring by objective score.
- Exact optimal hit: score difference <= 1e-8. Also report normalized optimality gap, feasible fraction and wall-clock seconds.
- Walk-forward investment test (secondary) uses historical information available by each decision date; include 10 basis points per unit traded.

## Caveats
QAOA optimization must be executed and checked in Colab before claiming any results; unverified library compatibility is not evidence. All simulation runtimes include classical emulation and cannot demonstrate hardware quantum speedup. Comparing net Sharpe ratios over too few months is not meaningful. For enough matched observations, estimate paired time-series bootstrap intervals, with assumptions and bootstrap settings stated.
