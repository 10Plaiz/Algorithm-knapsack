import random

import pytest

from src.knapsack_brute_force import solve_brute_force
from src.knapsack_dp import Topic, load_topics, solve_dp


def random_topics(n, hours_range=(1, 10), value_range=(1, 50), seed=None):
    rng = random.Random(seed)
    return [
        Topic(name=f"T{i}", hours=rng.randint(*hours_range), value=rng.uniform(*value_range))
        for i in range(n)
    ]


def assert_selection_valid(topics, capacity, max_value, selected, total_hours):
    assert total_hours <= capacity
    assert total_hours == sum(t.hours for t in selected)
    assert max_value == pytest.approx(sum(t.value for t in selected))
    assert set(t.name for t in selected).issubset(set(t.name for t in topics))
    assert len(set(t.name for t in selected)) == len(selected)


@pytest.mark.parametrize("seed", range(10))
def test_dp_matches_brute_force_random_instances(seed):
    topics = random_topics(n=12, seed=seed)
    capacity = random.Random(seed).randint(0, 40)

    bf_value, bf_selected, bf_hours = solve_brute_force(topics, capacity)
    dp_value, dp_selected, dp_hours = solve_dp(topics, capacity)

    assert dp_value == pytest.approx(bf_value)
    assert_selection_valid(topics, capacity, bf_value, bf_selected, bf_hours)
    assert_selection_valid(topics, capacity, dp_value, dp_selected, dp_hours)


def test_zero_capacity_selects_nothing():
    topics = random_topics(n=8, seed=1)
    for solve in (solve_brute_force, solve_dp):
        value, selected, hours = solve(topics, 0)
        assert value == 0
        assert selected == []
        assert hours == 0


def test_empty_topic_list():
    for solve in (solve_brute_force, solve_dp):
        value, selected, hours = solve([], 10)
        assert value == 0
        assert selected == []
        assert hours == 0


def test_single_topic_exceeds_capacity_is_excluded():
    topics = [Topic(name="TooBig", hours=20, value=100)]
    for solve in (solve_brute_force, solve_dp):
        value, selected, hours = solve(topics, 5)
        assert value == 0
        assert selected == []
        assert hours == 0


def test_all_topics_exceed_capacity():
    topics = [Topic(name=f"T{i}", hours=50 + i, value=10) for i in range(5)]
    for solve in (solve_brute_force, solve_dp):
        value, selected, hours = solve(topics, 10)
        assert value == 0
        assert selected == []


def test_single_topic_fits_exactly():
    topics = [Topic(name="Exact", hours=10, value=25)]
    for solve in (solve_brute_force, solve_dp):
        value, selected, hours = solve(topics, 10)
        assert value == pytest.approx(25)
        assert selected == topics
        assert hours == 10


def test_dp_matches_brute_force_on_sample_small_csv():
    topics = load_topics("src/data/sample_topics_small.csv")
    for capacity in (0, 5, 10, 15, 20, 30):
        bf_value, _, bf_hours = solve_brute_force(topics, capacity)
        dp_value, _, dp_hours = solve_dp(topics, capacity)
        assert dp_value == pytest.approx(bf_value)
        assert bf_hours <= capacity
        assert dp_hours <= capacity
