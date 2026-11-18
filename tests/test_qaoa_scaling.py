"""Basic validation for the QAOA ETF-count experiment."""
import ast
import itertools
import json
from pathlib import Path
import time
import unittest

import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator


NOTEBOOK = Path(__file__).resolve().parents[1] / "data" / "04_qaoa_etf_scaling.ipynb"


class ScalingNotebookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
        cells = [c for c in cls.notebook["cells"] if c["cell_type"] == "code"]
        for cell in cells:
            source = "".join(cell["source"])
            if source.lstrip().startswith("%pip"):
                continue
            ast.parse(source)

        functions = next("".join(c["source"]) for c in cells
                         if "def make_problem(n):" in "".join(c["source"]))
        cls.ns = {
            "np": np,
            "itertools": itertools,
            "time": time,
            "minimize": minimize,
            "QuantumCircuit": QuantumCircuit,
            "transpile": transpile,
            "AerSimulator": AerSimulator,
            "TICKERS": [f"ETF{i}" for i in range(20)],
            "CHOOSE": 3,
            "LAMBDA": 1.0,
            "QAOA_DEPTH": 2,
            "QAOA_ITERATIONS": 2,
            "OPTIMIZATION_SHOTS": 16,
            "FINAL_SHOTS": 32,
            "MIXER_SCALE": 100.0,
            "mu": np.linspace(0.01, 0.03, 20),
            "cov": np.eye(20) * 0.003 + np.full((20, 20), 0.0002),
        }
        exec(compile(functions, str(NOTEBOOK), "exec"), cls.ns)

    def test_exact_count_and_score_encoding(self):
        expected = {6: 20, 10: 120, 15: 455, 20: 1140}
        for size, combinations in expected.items():
            with self.subTest(size=size):
                result = self.ns["make_problem"](size)
                self.assertEqual(result["combinations"], combinations)
                self.assertLess(result["encoding_error"], 1e-10)
                self.assertGreaterEqual(result["exact_seconds"], 0)
                self.assertGreaterEqual(result["greedy_seconds"], 0)
                self.assertGreaterEqual(result["exact_score"] + 1e-12,
                                        result["greedy_score"])

    def test_qaoa_keeps_exactly_three_etfs(self):
        problem = self.ns["make_problem"](6)
        angles = np.array([0.4, 0.7, 0.2, 0.5])
        circuit = self.ns["qaoa_circuit"](problem, angles)
        state = Statevector.from_instruction(circuit.remove_final_measurements(inplace=False))
        invalid_probability = sum(
            probability for index, probability in enumerate(state.probabilities())
            if int(index).bit_count() != 3
        )
        self.assertLess(invalid_probability, 1e-8)

    def test_small_qaoa_smoke_run(self):
        problem = self.ns["make_problem"](6)
        result = self.ns["run_qaoa"](problem, seed=0)
        self.assertEqual(result["etfs"], 6)
        self.assertEqual(result["valid_shots"], 32)
        self.assertEqual(len(result["portfolio"].split(", ")), 3)
        self.assertLessEqual(result["score"], problem["exact_score"] + 1e-10)
        self.assertGreaterEqual(result["gap"], 0)


if __name__ == "__main__":
    unittest.main()
