# Qiskit validation and larger ETF experiment plan

## Question 1 — Is Qiskit the reason the earlier QAOA scores were low?

Qiskit is not an untested application. IBM introduced Qiskit in 2017, the research paper *Quantum computing with Qiskit* (2024) documents its SDK architecture, and the Qiskit community has official QAOA portfolio-optimization examples. Qiskit Aer is a software simulator, not a quantum processor.

The current project used Qiskit to build circuits, Qiskit Aer's matrix-product-state engine to simulate them, and SciPy COBYLA to choose circuit parameters. The 20-ETF notebook checks the classical portfolio score against the QAOA cost-function encoding and reports an error below 1e-10. That **verifies the scored binary objective**, but does not independently verify the complete QAOA circuit, optimizer, simulator behavior, or convergence.

**We cannot attribute low QAOA scores to Qiskit itself.** Potential confounding factors include fixed depth 2, optimization starts and iterations, finite shots, gate-angle scaling, the XY mixer, dense all-to-all portfolio covariance interactions, and the ETF group. The existing results show algorithm performance for one configuration, not a software defect.

Recommended controlled verification:
1. Test that the circuit always samples the requested number of ETFs.
2. On six small ETFs, verify circuit behavior with both statevector and matrix-product-state simulation, matched circuit and measurement settings.
3. Compare QAOA depth, optimizer iteration count and shot budgets at the same problem size with repeated seeds.
4. Keep a classical exact reference for **small** instances, and report the gap and runtime. Do not compare runtime across different hardware as if it were a controlled experiment.
5. Do not claim that changing the simulator alone makes QAOA optimal.

## Question 2 — Can we scale from 3/20 to 6/40, 12/80, 24/160?

| Portfolio size | Number of subsets |
|---|---:|
| 3 of 20 | 1,140 |
| 6 of 40 | 3,838,380 |
| 12 of 80 | 60,246,643,120,300 |
| 24 of 160 | 20,767,445,112,335,933,694,764,617,900 |

These counts assume choosing exactly k assets from n, with equal weights. The *selection ratio* is 15% for all four experiments. Each circuit has one qubit per ETF, so these involve 20, 40, 80, and 160 qubits.

Exhaustive enumeration is reasonable for 3/20, expensive for 6/40 and impractical for 12/80 and 24/160. For the larger cases, compare **greedy search and local search** with clearly labeled approximate results; add an exact constrained solver only where the run is feasible and its status confirms optimality.

The current QAOA cost circuit includes a phase term for each nonzero covariance pair. For a dense covariance matrix, the *possible pairs per layer* are 190, 780, 3,160 and 12,720 respectively, before compilation and additional mixer gates. Larger QAOA experiments can therefore exceed practical simulation resources even when the code can construct the circuit.

A fair scaling analysis must report:
- The *same ETF universe, same date, return-estimation method, risk penalty, and portfolio constraint* across each algorithm at a given size.
- Actual runtimes, algorithm quality and convergence or failure statuses.
- Whether the measured score has an exact optimum, a best-known classical reference, or neither.
- Whether QAOA was actually executed or only its circuit cost was estimated.

## Data source status

The original `manisahni/marketdata` adjusted-price CSV contains **27 asset columns**, of which **23** intersect the project's candidate-ETF list with complete required historical coverage. The audit cannot support 40/80/160 ETF experiments from that file.

The separate extended-source audit uses **real, adjusted price series** rather than generating asset histories. It must demonstrate at least 160 eligible ETFs with complete features and labels for the January 2025 forecast before claiming a 24/160 test. In the initial network smoke test 12 of 12 requested ETF histories passed; the larger collection is a separate workflow.

The preliminary classical code uses the original Random Forest feature structure: last month return, three- and six-month price change, and recent three-month volatility, trained before the January 2025 decision. A one-swap local search is performed after greedy selection. **A higher score from the local method is not proof of the global optimum.**

## Directly relevant sources

- Javadi-Abhari et al. (2024), *Quantum computing with Qiskit*: https://arxiv.org/abs/2405.08810
- Qiskit Finance portfolio optimization with QAOA: https://qiskit-community.github.io/qiskit-finance/tutorials/01_portfolio_optimization.html
- IBM Quantum, *Quantum approximate multi-objective optimization*: https://quantum.cloud.ibm.com/docs/en/tutorials/quantum-approximate-multi-objective-optimization (includes a 40-asset cardinality-constrained portfolio example and discusses limitations; it does **not** demonstrate quantum advantage)
- Qiskit Aer matrix-product-state simulation notes: https://qiskit.github.io/qiskit-aer/tutorials/7_matrix_product_state_method.html

**Bottom line:** The new large-ETF results should test problem-size scaling while recognizing simulator constraints, not treat Qiskit as an explanation for the prior performance without controlled evidence.
