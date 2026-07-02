"""Brute-force 0/1 knapsack solver: O(2^n) enumeration of every subset.

Used as the correctness baseline and performance contrast for the DP solver.
Only practical for small n (roughly n <= 20-22) since it enumerates 2^n subsets.
"""

import csv
from collections import namedtuple

Topic = namedtuple("Topic", ["name", "hours", "value"])


def load_topics(csv_path):
    """Load topics from a CSV with columns: topic,hours,value.

    hours must be a non-negative integer (required for the hour-budget check).
    value is the projected grade boost, read as a float.
    """
    topics = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            hours = int(row["hours"])
            if hours < 0:
                raise ValueError(f"Negative hours for topic {row['topic']!r}")
            topics.append(Topic(name=row["topic"], hours=hours, value=float(row["value"])))
    return topics


def solve_brute_force(topics, capacity):
    """Return (max_value, selected_topics, total_hours) for the given capacity."""
    n = len(topics)
    best_value = 0.0
    best_mask = 0

    for mask in range(1 << n):
        total_hours = 0
        total_value = 0.0
        for i in range(n):
            if mask & (1 << i):
                total_hours += topics[i].hours
                total_value += topics[i].value
        if total_hours <= capacity and total_value > best_value:
            best_value = total_value
            best_mask = mask

    selected = [topics[i] for i in range(n) if best_mask & (1 << i)]
    total_hours = sum(t.hours for t in selected)
    return best_value, selected, total_hours


MAX_FEASIBLE_TOPICS = 25  # 2^25 subsets (~33M) is the practical ceiling for pure-Python enumeration


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Run the brute-force knapsack solver on a topics CSV.")
    parser.add_argument(
        "--data",
        default=str(Path(__file__).parent / "data" / "sample_topics_small.csv"),
        help="Path to topics CSV (columns: topic,hours,value)",
    )
    parser.add_argument("--capacity", type=int, default=20, help="Maximum study hours")
    parser.add_argument(
        "--force", action="store_true", help="Run anyway even if the topic count is not feasible for brute force"
    )
    args = parser.parse_args()

    topics = load_topics(args.data)

    if len(topics) > MAX_FEASIBLE_TOPICS and not args.force:
        print(
            f"Refusing to run: {len(topics)} topics means 2^{len(topics)} "
            f"(~{1 << len(topics):,}) subsets to check."
        )
        print("Brute force is not feasible at this size. Use src/knapsack_dp.py instead, "
              "or pass --force to run anyway (not recommended).")
        raise SystemExit(1)

    print("=== Study Time Allocation: Brute Force (0/1 Knapsack) ===\n")
    print(f"Input: capacity = {args.capacity} hours, {len(topics)} topics")
    for t in topics:
        print(f"  - {t.name:<28} hours={t.hours:<3} value={t.value}")

    max_value, selected, total_hours = solve_brute_force(topics, args.capacity)

    print(f"\nOutput: max grade boost = {max_value}, hours used = {total_hours}/{args.capacity}")
    print("Selected topics:")
    for t in selected:
        print(f"  - {t.name:<28} hours={t.hours:<3} value={t.value}")
