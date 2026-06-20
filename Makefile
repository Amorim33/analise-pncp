.PHONY: sync check test lint typecheck pipeline run clean

sync:
	uv sync --extra dev

lint:
	uv run ruff check .

typecheck:
	uv run mypy src

test:
	uv run pytest

check: lint typecheck test

pipeline:
	uv run pncp-analysis run-all

run:
	uv run pncp-analysis run-all

clean:
	rm -rf .mypy_cache .pytest_cache .ruff_cache
