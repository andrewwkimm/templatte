help:
	cat Makefile

################################################################################

ci:
	uv sync
	make format
	make lint
	make type-check
	make test

lint:
	uv run ruff check --fix .
	uv run lint-imports

format:
	uv run ruff format .

setup:
	@if [ -f bootstrap.py ]; then uv run python bootstrap.py; fi
	uv sync
	uv run pre-commit install --install-hooks

test:
	uv run pytest --cov

type-check:
	uv run ty check tests

################################################################################

.PHONY: \
	ci \
	format \
	help \
	lint \
	setup \
	test \
	type-check
