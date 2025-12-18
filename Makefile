.PHONY: all help install lint format test clean

# Default target
all: install lint test

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies using uv
	uv sync

lint: ## Run code quality tools (Ruff)
	uv run ruff check .

format: ## Auto-format code (Ruff)
	uv run ruff format .

test: ## Run tests (Pytest)
	uv run pytest -v

clean: ## Clean up cache and temporary files
	rm -rf .venv
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +