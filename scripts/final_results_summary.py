"""Generate a transparent final-results Markdown summary from measured CSV files.

Never fill missing quantum trials with zero scores. Only describe verified rows.
Usage: python scripts/final_results_summary.py
"""
from pathlib import Path
import pandas as pd

W=Path("results/final_walkforward")
L=Path("results/final_large")
OUT=Path("results/final_report")
OUT.mkdir(parents=True,exist_ok=True)


def fmt(v):
    return f"{float(v):.6f}"

def main():
    lines=["# CECS 385 — Quantum Versus Classical ETF Portfolio Selection",
           "",
           "**Experiment status:** Report built from available measured CSV files. Missing work is identified, not extrapolated.",
           "",
           "Scores maximize *predicted next-month ETF return minus a covariance-risk penalty*.",
           "These scores are not realized investment returns. QAOA used a **Qiskit Aer simulator**, not quantum hardware.",
           ""]
    if (W/"trials.csv").exists() and (W/"classical_by_month.csv").exists():
        q=pd.read_csv(W/"trials.csv")
        c=pd.read_csv(W/"classical_by_month.csv")
        lines.extend(["## Six-month out-of-sample walk-forward experiment", "",
          f"Measured QAOA trials: **{len(q)}**; historical months: **{c['target_month'].nunique()}**.",
          f"Exact optimum known for every included month; greedy matched exact in **{int(c['greedy_optimal'].sum())}/{len(c)}** months.",
          "",
          "| Initialization | Trials | Exact hits | Beats greedy | Mean gap to exact | Mean QAOA seconds |",
          "|---|---:|---:|---:|---:|---:|"])
        for method,sub in q.groupby("start_method",sort=True):
            lines.append(f"| {method} | {len(sub)} | {int(sub['exact_hit'].sum())} | {int(sub['beat_greedy'].sum())} | {fmt(sub['gap_to_exact'].mean())} | {float(sub['seconds'].mean()):.2f} |")
        lines.extend(["",
          "The exact optimum is a mathematical upper bound on the objective score; neither QAOA nor greedy can exceed it.",
          "",
          "| Target month | Exact score | Greedy score | Greedy exact? |",
          "|---|---:|---:|---|"])
        for _,x in c.iterrows():
            lines.append(f"| {x['target_month']} | {fmt(x['exact_score'])} | {fmt(x['greedy_score'])} | {bool(x['greedy_optimal'])} |")
        lines.append("")
    else:
        lines.extend(["## Six-month experiment", "",
                      "NOT YET COMPLETE — the full walk-forward CSV files were not found.", ""])
    if (L/"classical_benchmarks.csv").exists():
        c=pd.read_csv(L/"classical_benchmarks.csv")
        lines.extend(["## Expanded ETF classical benchmarks", "",
          "| Select / available | Greedy score | Best 25-start classical score | Proven exact score |",
          "|---|---:|---:|---:|"])
        for _,x in c.iterrows():
            exact=fmt(x["exact_score"]) if pd.notna(x.get("exact_score")) else "Not certified"
            lines.append(f"| {int(x['k'])}/{int(x['n'])} | {fmt(x['greedy_score'])} | {fmt(x['best_25_start_score'])} | {exact} |")
        lines.append("")
        for n in (40,80,160):
            file=L/f"qaoa_{n}_trials.csv"
            if file.exists():
                d=pd.read_csv(file)
                lines.extend([f"### {int(d.iloc[0]['k'])}/{n} QAOA",
                   f"Completed QAOA trials: **{len(d)}**. Best QAOA objective score: **{fmt(d['qaoa_score'].max())}**.",
                   f"QAOA trials beating the greedy reference: **{int((d['score_minus_greedy']>1e-8).sum())}/{len(d)}**.",
                   f"Budget: depth {int(d.iloc[0]['depth'])}, up to {int(d.iloc[0]['maxiter'])} COBYLA evaluations, {int(d.iloc[0]['finalshots'])} final shots.",
                   "These quantum settings differ across ETF sizes; 80/160 are feasibility pilots, not equal-budget quality comparisons." if n!=40 else "The 6/40 classical exact optimum is independently computed.",
                   ""])
            else:
                lines.extend([f"### {n} ETF QAOA", "No verified QAOA trial CSV found.", ""])
    else:
        lines.extend(["## Larger ETF experiment",
             "NOT YET COMPLETE — the frozen large-data benchmark CSV was not found.", ""])
    lines.extend(["## Scientific limitations", "",
      "- QAOA outcomes depend on objective encoding, starting state, shot budget, depth and classical optimization.",
      "- January 2025 was used to select promising settings; the six other months are held-out validation, not an independent prospective market test.",
      "- The expanded ETF dataset differs from the original 20-ETF marketdata source; never compare their numerical objective scores as if the portfolios were the same.",
      "- Strong local-search results are not proof of global optimality at 12/80 or 24/160.",
      "- Running QAOA on a classical simulator does not demonstrate quantum computational speedup.",
      "- Retain failed/cancelled computational jobs and report only completed measured trials.",
      ""])
    dest=OUT/"Final Research Results.md"
    dest.write_text("\n".join(lines),encoding="utf-8")
    print("Wrote",dest,"lines",len(lines),flush=True)
    print("\n".join(lines[:35]),flush=True)


if __name__=="__main__":
    main()
