"""Compare two Qiskit Aer simulation methods on the SAME six-ETF QAOA circuit."""
import json
import numpy as np
from pathlib import Path
from IPython.display import display
from qiskit import transpile
from qiskit_aer import AerSimulator

book = json.loads(Path("data/04 QAOA ETF Scaling Test.ipynb").read_text())
scope = {"__name__": "__main__", "display": display}
for index in [4, 5, 7, 9]:
    exec(compile("".join(book["cells"][index]["source"]), f"cell {index}", "exec"), scope)

problem = scope["make_problem"](6)
angles = np.array([0.2, 0.6, 0.3, 0.9])
qc = scope["qaoa_circuit"](problem, angles).remove_final_measurements(inplace=False)
qc.save_statevector()
states = []
for name in ("statevector", "matrix_product_state"):
    sim = AerSimulator(method=name)
    transpiled = transpile(qc, sim)
    result = sim.run(transpiled).result()
    arr = np.asarray(result.data(0)["statevector"], dtype=complex)
    states.append(arr)
    print(name, "state norm:", np.linalg.norm(arr), flush=True)

fidelity = float(abs(np.vdot(states[0], states[1])) ** 2)
max_prob_difference = float(np.max(np.abs(np.abs(states[0])**2 - np.abs(states[1])**2)))
invalid = sum(float(abs(states[1][j])**2) for j in range(2**6) if j.bit_count() != 3)
print(f"Fidelity: {fidelity:.12f}", flush=True)
print(f"Largest probability difference: {max_prob_difference:.12g}", flush=True)
print(f"Invalid-cardinality probability: {invalid:.12g}", flush=True)
assert fidelity > 0.999999999
assert max_prob_difference < 1e-8
assert invalid < 1e-8
print("PASSED: small-circuit backend comparison; NOT evidence of large-scale QAOA convergence", flush=True)
