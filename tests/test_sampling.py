from pncp_analysis.sampling import deterministic_sample


def test_deterministic_sample_is_stable() -> None:
    records = [{"numeroControlePNCP": f"00000000000000-1-{idx:06d}/2026"} for idx in range(20)]

    first = deterministic_sample(records, sample_n=5, seed=20260608)
    second = deterministic_sample(list(reversed(records)), sample_n=5, seed=20260608)

    assert first == second
    assert len(first) == 5


def test_deterministic_sample_returns_all_when_pool_is_small() -> None:
    records = [{"numeroControlePNCP": "00000000000000-1-000001/2026"}]

    assert deterministic_sample(records, sample_n=10, seed=1) == records
