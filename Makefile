.PHONY: build check lint test init

build:
	begone build

check:
	begone check

lint:
	ruff check .
	ruff format --check .
	mypy begone tests

test:
	pytest

init:
	uv venv
	uv sync
