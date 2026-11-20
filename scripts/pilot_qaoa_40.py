"""Resource-limited 6-of-40 QAOA PILOT on real January 2025 RF forecasts.

This is deliberately NOT the 10-seed, 50-iteration full QAOA experiment.
Do not interpret it as an exact optimality or large-scale speed comparison.
"""
from pathlib import Path
import time
import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import pandas as pd

from large_etf_rf_classical import prepare_forecasts, score, greedy

OUT = Path("results/large_etf_feasibility")
N, K = 40, 6
DEPTH = 1
MAX_ITER = 6
OPT_SHOTS = 32
FINAL_SHOTS = 128
SCALE = 100.0


def circuit(mu, cov, angles):
    a = mu / K - np.diag(cov) / K**2
    b = -2.0 * cov / K**2
    np.fill_diagonal(b, 0)
    qc = QuantumCircuit(N)
    chosen = np.linspace(0, N-1, K, dtype=int)
    for i in chosen:
        qc.x(int(i))
    for gamma, beta in zip(angles[:DEPTH], angles[DEPTH:]):
        for i in range(N):
            adjustment = a[i] + b[i].sum() / 2
            qc.rz(SCALE * gamma * adjustment, i)
        for i in range(N):
            for j in range(i+1, N):
                if abs(b[i, j]) > 1e-12:
                    qc.rzz(-SCALE * gamma * b[i, j] / 2, i, j)
        for offset in (0, 1):
            for i in range(offset, N-1, 2):
                qc.rxx(beta, i, i+1)
                qc.ryy(beta, i, i+1)
        qc.rxx(beta, N-1, 0)
        qc.ryy(beta, N-1, 0)
    qc.measure_all()
    return qc


def main():
    path = OUT / "new_data_source_monthly_prices.csv"
    monthly = pd.read_csv(path, index_col=0, parse_dates=True).sort_index()
    names, all_mu, all_cov = prepare_forecasts(monthly)
    if len(names) < N:
        raise ValueError(f"Only {len(names)} valid ETF predictions; need {N}")
    mu, cov = all_mu[:N], all_cov[:N, :N]
    g = greedy(mu, cov, K)
    gscore = score(g, mu, cov, K)
    rng = np.random.default_rng(7)
    simulator = AerSimulator(method="matrix_product_state")
    initial = rng.uniform(0, 2*np.pi, 2*DEPTH)
    calls = [0]
    start = time.perf_counter()

    def samples(angles, shots):
        compiled = transpile(circuit(mu, cov, angles), simulator, optimization_level=1)
        counts = simulator.run(compiled, shots=shots, seed_simulator=7).result().get_counts()
        valid = []
        for bits, count in counts.items():
            selected = tuple(i for i, b in enumerate(bits[::-1]) if b == "1")
            if len(selected) == K:
                valid.append((selected, count, score(selected, mu, cov, K)))
        return valid

    def loss(angles):
        valid = samples(angles, OPT_SHOTS)
        calls[0] += 1
        total = sum(row[1] for row in valid)
        print("QAOA evaluation", calls[0], "valid shots", total, flush=True)
        if not total:
            return 1e4
        return -sum(row[1]*row[2] for row in valid)/total

    print("PILOT 6/40 using real monthly ETF data; NOT the final multi-seed study.", flush=True)
    fitted = minimize(loss, initial, method="COBYLA", options={"maxiter":MAX_ITER})
    final = samples(fitted.x, FINAL_SHOTS)
    seconds = time.perf_counter() - start
    if not final:
        raise RuntimeError("No valid portfolio sample was produced")
    best, count, bestscore = max(final, key=lambda t:t[2])
    assert len(best) == K
    row = {"etfs": N, "selected": K, "depth": DEPTH, "maxiter": MAX_ITER,
           "opt_shots": OPT_SHOTS, "final_shots": FINAL_SHOTS,
           "valid_final_shots": sum(r[1] for r in final),
           "calls": calls[0], "optimizer_success": bool(fitted.success),
           "qaoa_score": bestscore, "greedy_score": gscore,
           "difference_from_greedy": bestscore-gscore,
           "qaoa_simulator_seconds": seconds,
           "qaoa_portfolio": ", ".join(names[i] for i in best),
           "greedy_portfolio": ", ".join(names[i] for i in g),
           "exact_optimum_known": False}
    pd.DataFrame([row]).to_csv(OUT / "qaoa_40_qubit_pilot.csv", index=False)
    print("QAOA PILOT COMPLETE", row, flush=True)


if __name__ == "__main__":
    main()
