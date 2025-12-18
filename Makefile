
# CONFIGURATION
PYTHON_VERSION := 3.12
VENV_DIR       := .venv
CMD            := uv run


.PHONY: help install lint format test clean check

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  install    Install dependencies (Python $(PYTHON_VERSION))"
	@echo "  lint       Run static analysis (Ruff)"
	@echo "  format     Auto-format code"
	@echo "  test       Run tests"
	@echo "  clean      Remove cache files"
	@echo "  check      Run full QA pipeline"

install:
	@echo "Installing dependencies..."
	uv python pin $(PYTHON_VERSION)
	uv sync

lint:
	$(CMD) ruff check .

format:
	$(CMD) ruff check --fix .
	$(CMD) ruff format .

test:
	$(CMD) pytest tests -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .ruff_cache .coverage

check: format lint test
