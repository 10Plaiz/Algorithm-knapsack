"""Dynamic Programming 0/1 knapsack solver: O(n*W) time and space.

Mirrors the StudyTimeKnapsack pseudocode in project_algo_draft.docx.md (section 3.4):
tabulate DP[i][w], then backtrack using the DP[i][w] != DP[i-1][w] rule to recover
which topics were selected.
"""

import csv
from collections import namedtuple

Topic = namedtuple("Topic", ["name", "hours", "value"])


def load_topics(csv_path):
    """Load topics from a CSV with columns: topic,hours,value.

    hours must be a non-negative integer (required for DP table indexing).
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


def solve_dp(topics, capacity):
    """Return (max_value, selected_topics, total_hours) for the given capacity.

    capacity must be a non-negative integer (the DP table is indexed by hour).
    """
    if capacity < 0:
        raise ValueError("capacity must be non-negative")

    n = len(topics)
    w_max = capacity
    dp = [[0.0] * (w_max + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        hours_i = topics[i - 1].hours
        value_i = topics[i - 1].value
        for w in range(1, w_max + 1):
            if hours_i <= w:
                include = value_i + dp[i - 1][w - hours_i]
                exclude = dp[i - 1][w]
                dp[i][w] = max(include, exclude)
            else:
                dp[i][w] = dp[i - 1][w]

    selected = []
    w = w_max
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected.append(topics[i - 1])
            w -= topics[i - 1].hours
    selected.reverse()

    total_hours = sum(t.hours for t in selected)
    return dp[n][w_max], selected, total_hours


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Run the DP knapsack solver on a topics CSV.")
    parser.add_argument(
        "--data",
        default=str(Path(__file__).parent / "data" / "sample_topics_small.csv"),
        help="Path to topics CSV (columns: topic,hours,value)",
    )
    parser.add_argument("--capacity", type=int, default=20, help="Maximum study hours")
    args = parser.parse_args()

    topics = load_topics(args.data)

    print("=== Study Time Allocation: Dynamic Programming (0/1 Knapsack) ===\n")
    print(f"Input: capacity = {args.capacity} hours, {len(topics)} topics")
    for t in topics:
        print(f"  - {t.name:<28} hours={t.hours:<3} value={t.value}")

    max_value, selected, total_hours = solve_dp(topics, args.capacity)

    print(f"\nOutput: max grade boost = {max_value}, hours used = {total_hours}/{args.capacity}")
    print("Selected topics:")
    for t in selected:
        print(f"  - {t.name:<28} hours={t.hours:<3} value={t.value}")
