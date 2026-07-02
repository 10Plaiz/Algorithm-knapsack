"""Benchmark harness comparing brute force vs DP on the study time allocation problem.

Sweep A (n=5..20, capacity fixed): both solvers, to show brute force's exponential
blowup against DP's near-flat time, and to double-check they still agree on max value.
Sweep B (n=50..500, capacity fixed): DP only, since brute force is infeasible here.

Writes results/benchmark_results.csv and two plots (time, memory) vs n.
"""

import csv
import random
import time
import tracemalloc
from pathlib import Path

from knapsack_brute_force import solve_brute_force
from knapsack_dp import Topic, solve_dp

ROOT = Path(__file__).parent.parent
RESULTS_DIR = ROOT / "results"
CAPACITY = 100


def generate_topics(n, seed=0):
    rng = random.Random(seed)
    return [
        Topic(name=f"Topic{i}", hours=rng.randint(1, 10), value=rng.uniform(1, 20))
        for i in range(n)
    ]


def measure(solve_fn, topics, capacity):
    tracemalloc.start()
    start = time.perf_counter()
    max_value, selected, total_hours = solve_fn(topics, capacity)
    elapsed = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return elapsed, peak / 1024, max_value


def run_sweep_a():
    rows = []
    for n in range(5, 21):
        topics = generate_topics(n)

        bf_time, bf_mem, bf_value = measure(solve_brute_force, topics, CAPACITY)
        rows.append(("brute_force", n, CAPACITY, bf_time, bf_mem, bf_value))

        dp_time, dp_mem, dp_value = measure(solve_dp, topics, CAPACITY)
        rows.append(("dp", n, CAPACITY, dp_time, dp_mem, dp_value))

        assert abs(bf_value - dp_value) < 1e-6, f"Mismatch at n={n}: bf={bf_value} dp={dp_value}"
        print(f"n={n:>3}  brute_force={bf_time:>8.4f}s  dp={dp_time:>8.5f}s  (values agree: {bf_value:.1f})")
    return rows


def run_sweep_b():
    rows = []
    for n in range(50, 501, 50):
        topics = generate_topics(n)
        dp_time, dp_mem, dp_value = measure(solve_dp, topics, CAPACITY)
        rows.append(("dp", n, CAPACITY, dp_time, dp_mem, dp_value))
        print(f"n={n:>3}  dp={dp_time:>8.5f}s  peak_mem={dp_mem:>8.1f}KB")
    return rows


def write_csv(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["algorithm", "n", "capacity", "time_seconds", "peak_memory_kb", "max_value"])
        writer.writerows(rows)


def plot_results(rows):
    import matplotlib.pyplot as plt

    bf_rows = [r for r in rows if r[0] == "brute_force"]
    dp_rows = [r for r in rows if r[0] == "dp"]

    fig, ax = plt.subplots()
    if bf_rows:
        ax.plot([r[1] for r in bf_rows], [r[3] for r in bf_rows], "o-", label="Brute force O(2^n)")
    ax.plot([r[1] for r in dp_rows], [r[3] for r in dp_rows], "o-", label="Dynamic Programming O(n*W)")
    ax.set_xlabel("Number of topics (n)")
    ax.set_ylabel("Time (seconds)")
    ax.set_yscale("log")
    ax.set_title(f"Runtime vs. number of topics (capacity = {CAPACITY} hours)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "time_complexity_plot.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots()
    if bf_rows:
        ax.plot([r[1] for r in bf_rows], [r[4] for r in bf_rows], "o-", label="Brute force O(2^n)")
    ax.plot([r[1] for r in dp_rows], [r[4] for r in dp_rows], "o-", label="Dynamic Programming O(n*W)")
    ax.set_xlabel("Number of topics (n)")
    ax.set_ylabel("Peak memory (KB)")
    ax.set_title(f"Peak memory vs. number of topics (capacity = {CAPACITY} hours)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "memory_plot.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    print("=== Sweep A: n=5..20, both solvers ===")
    rows_a = run_sweep_a()

    print("\n=== Sweep B: n=50..500, DP only ===")
    rows_b = run_sweep_b()

    all_rows = rows_a + rows_b
    write_csv(all_rows, RESULTS_DIR / "benchmark_results.csv")
    plot_results(rows_a)

    print(f"\nWrote {len(all_rows)} rows to results/benchmark_results.csv")
    print("Wrote results/time_complexity_plot.png and results/memory_plot.png")
