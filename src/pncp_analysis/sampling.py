from __future__ import annotations

import random
from collections import OrderedDict
from typing import Any


def deduplicate_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: OrderedDict[str, dict[str, Any]] = OrderedDict()
    for record in sorted(records, key=lambda item: str(item.get("numeroControlePNCP") or "")):
        control = str(record.get("numeroControlePNCP") or "")
        if control and control not in deduped:
            deduped[control] = record
    return list(deduped.values())


def deterministic_sample(
    records: list[dict[str, Any]],
    *,
    sample_n: int,
    seed: int,
) -> list[dict[str, Any]]:
    ordered = deduplicate_records(records)
    if len(ordered) <= sample_n:
        return ordered
    selected = random.Random(seed).sample(ordered, sample_n)
    return sorted(selected, key=lambda item: str(item.get("numeroControlePNCP") or ""))
