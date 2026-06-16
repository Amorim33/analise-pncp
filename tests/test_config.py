from pathlib import Path

from pncp_analysis.config import load_config


def test_load_config_accepts_all_strategy_and_unlimited_municipality_scan(tmp_path: Path) -> None:
    path = tmp_path / "analysis.yaml"
    path.write_text(
        """
period:
  start: "2025-06-15"
  end: "2026-06-15"
modality:
  id: 6
  name: "Pregao - Eletronico"
sample:
  strategy: "all"
  n: null
  document_n: 100
  seed: 20260608
api:
  query_bases: []
  document_bases: []
  page_size: 50
  municipality_scan_max_pages: null
  request_delay_seconds: 0
  retries: 1
semantic:
  model: "codex-subagent"
  reasoning_effort: "medium"
  text_verbosity: "low"
  max_document_chars: 12000
  document_cache_dir: "data/raw/q3_documents"
sao_paulo_filter:
  include_indicators: []
  exclude_indicators: []
cities: []
""",
        encoding="utf-8",
    )

    config = load_config(path)

    assert config.sample_strategy == "all"
    assert config.sample_n is None
    assert config.document_sample_n == 100
    assert config.api.municipality_scan_max_pages is None
    assert config.semantic.model == "codex-subagent"
    assert config.semantic.reasoning_effort == "medium"
