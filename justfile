[private]
default:
  @just --summary --unsorted

format:
  uv lock --check
  uv run ruff format

lint:
  uv lock --check
  uv run ruff check
  uv run ruff format --diff
  uv run ty check
