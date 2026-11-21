"""Validate binary portfolio scoring, one-swap math, and QAOA cost phases.

This runs against deterministic synthetic covariance *only for code verification*.
The real ETF experiment uses actual downloaded adjusted prices separately.
"""
import itertools
import unittest
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from large_etf_rf_classical import score, swap_gain, greedy, improve_by_swaps


def qaoa_cost_coefficients(mu, cov, k, lam=1.0):
    a = np.asarray(mu) / k - lam * np.diag(cov) / (k*k)
    b = -2 * lam * np.asarray(cov) / (k*k)
    np.fill_diagonal(b, 0)
    return a, b


def cost_phase_circuit(mu, cov, k, gamma=0.13, scale=100.0):
    """The exact RZ / RZZ phase layer used in qaoa_larger_real_etfs."""
    n=len(mu)
    a, b=qaoa_cost_coefficients(mu, cov, k)
    qc=QuantumCircuit(n)
    for i in range(n):
        qc.rz(scale*gamma*(a[i]+b[i].sum()/2),i)
    for i in range(n):
        for j in range(i+1,n):
            if abs(b[i,j])>1e-12:
                qc.rzz(-scale*gamma*b[i,j]/2,i,j)
    return qc


class ValidatePortfolioAndQAOA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rng=np.random.default_rng(385)
        cls.mu=rng.normal(0.015,0.018,6)
        r=rng.normal(0,.07,(10,6))
        cls.cov=r.T@r/10
        cls.k=3

    def test_binary_encoding_matches_portfolio_objective(self):
        a,b=qaoa_cost_coefficients(self.mu,self.cov,self.k)
        for selected in itertools.combinations(range(6),self.k):
            bits=np.zeros(6)
            bits[list(selected)]=1
            expected=score(selected,self.mu,self.cov,self.k)
            encoded=float(a@bits+sum(b[i,j]*bits[i]*bits[j]
                                         for i in range(6) for j in range(i+1,6)))
            self.assertAlmostEqual(expected,encoded,places=12)

    def test_single_swap_gain_matches_full_recomputation(self):
        for selected in itertools.combinations(range(6),self.k):
            outside=set(range(6))-set(selected)
            for leaving in selected:
                for entering in outside:
                    changed=sorted((set(selected)-{leaving})|{entering})
                    actual=score(changed,self.mu,self.cov,self.k)-score(selected,self.mu,self.cov,self.k)
                    self.assertAlmostEqual(actual,swap_gain(selected,leaving,entering,self.mu,self.cov,self.k),places=12)

    def test_greedy_and_swap_never_exceed_exhaustive(self):
        exact=max(score(s,self.mu,self.cov,self.k) for s in itertools.combinations(range(6),self.k))
        g=greedy(self.mu,self.cov,self.k)
        improved,_=improve_by_swaps(self.mu,self.cov,g,self.k)
        self.assertLessEqual(score(g,self.mu,self.cov,self.k),exact+1e-12)
        self.assertGreaterEqual(score(improved,self.mu,self.cov,self.k)+1e-12,score(g,self.mu,self.cov,self.k))
        self.assertLessEqual(score(improved,self.mu,self.cov,self.k),exact+1e-12)

    def test_qaoa_cost_gate_relative_phases_match_score_differences(self):
        gamma=0.13
        scale=100.
        phase=cost_phase_circuit(self.mu,self.cov,self.k,gamma,scale)
        # Initialize equal-amplitude superposition of all 64 bit strings.
        start=QuantumCircuit(6)
        start.h(range(6))
        start.compose(phase,inplace=True)
        amplitudes=Statevector.from_instruction(start).data
        candidate=list(itertools.combinations(range(6),self.k))
        first=candidate[0]
        index=lambda chosen:sum(1<<i for i in chosen)
        ref=index(first)
        for chosen in candidate[1:]:
            actual=amplitudes[index(chosen)]/amplitudes[ref]
            difference=score(chosen,self.mu,self.cov,self.k)-score(first,self.mu,self.cov,self.k)
            expected=np.exp(1j*scale*gamma*difference)
            self.assertLess(abs(actual-expected),1e-9,
                            f"Incorrect circuit phase for {chosen}")

if __name__=="__main__":
    unittest.main()
