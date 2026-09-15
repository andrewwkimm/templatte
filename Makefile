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

format:
	uv run ruff format .

setup:
	@if [ -f bootstrap.sh ]; then bash bootstrap.sh; fi
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
