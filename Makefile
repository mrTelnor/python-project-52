install:
	uv sync

lint:
	uv run ruff check

.PHONY: install lint