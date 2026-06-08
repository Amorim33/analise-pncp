from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PNCP_CONTROL_RE = re.compile(r"^(?P<cnpj>\d{14})-(?P<type>\d)-(?P<seq>\d+)/(?P<year>\d{4})$")


@dataclass(frozen=True)
class PncpControlNumber:
    cnpj: str
    control_type: int
    sequence: int
    year: int


def parse_control_number(value: str) -> PncpControlNumber:
    match = PNCP_CONTROL_RE.match(value)
    if not match:
        raise ValueError(f"Invalid PNCP control number: {value}")
    return PncpControlNumber(
        cnpj=match.group("cnpj"),
        control_type=int(match.group("type")),
        sequence=int(match.group("seq")),
        year=int(match.group("year")),
    )


def normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    ascii_value = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(ascii_value.upper().split())


def date_for_pncp(value: str) -> str:
    return value.replace("-", "")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def nested_get(payload: dict[str, Any], path: str) -> Any:
    current: Any = payload
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    if isinstance(value, list):
        return len(value) > 0
    return True


def format_percent(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)
