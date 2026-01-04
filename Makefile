# ==============================================================================
# CONFIGURATION
# ==============================================================================
PYTHON_VERSION := 3.12
VENV_DIR       := .venv
CMD            := uv run
IMAGE_NAME     := qa-orchestrator
TAG            := latest

# ==============================================================================
# TARGETS DECLARATION (.PHONY)
# ==============================================================================
.PHONY: help install clean
.PHONY: lint format type-check check test
.PHONY: docker-build docker-run docker-clean docker-dev

# ==============================================================================
# HELP & DOCS
# ==============================================================================
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Core Targets:"
	@echo "  install        Install dependencies and pin Python version"
	@echo "  clean          Remove all cache, venv, coverage and temporary files"
	@echo ""
	@echo "QA & Code Quality:"
	@echo "  format         Auto-format code (Ruff)"
	@echo "  lint           Run static code analysis (Ruff)"
	@echo "  type-check     Run static type checking (Mypy)"
	@echo "  test           Run tests with Coverage (configured in pyproject.toml)"
	@echo "  test-v         Run tests in verbose mode (show test names)"
	@echo "  test-s         Run tests showing stdout/logs (good for debugging)"
	@echo "  test-f         Run tests and stop on first failure"
	@echo "  check          Run FULL pipeline: format -> lint -> type -> test"
	@echo ""
	@echo "Docker Targets:"
	@echo "  docker-build   Build optimized multi-stage image"
	@echo "  docker-run     Run container with auto-cleanup (--rm)"
	@echo "  docker-clean   Remove dangling images and system prune"
	@echo "  docker-dev     Run container with bind mounts (Hot Reload)"

# ==============================================================================
# CORE
# ==============================================================================
install:
	@echo "[install] Pinning Python $(PYTHON_VERSION) and syncing dependencies..."
	uv python pin $(PYTHON_VERSION)
	uv sync

clean:
	@echo "[clean] Cleaning up caches, coverage and artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	# Added htmlcov and coverage.xml to cleanup
	rm -rf .pytest_cache .ruff_cache .coverage .mypy_cache htmlcov coverage.xml $(VENV_DIR)

# ==============================================================================
# QA PIPELINE
# ==============================================================================
format:
	@echo "[format] Formatting code..."
	$(CMD) ruff check --fix .
	$(CMD) ruff format .

lint:
	@echo "[lint] Running Linter (Ruff)..."
	$(CMD) ruff check .

type-check:
	@echo "[type-check] Running Type Checker (Mypy)..."
	$(CMD) mypy .

test:
	@echo "[test] Running Tests (Pytest + Coverage)..."
	# Arguments are now loaded from pyproject.toml
	$(CMD) pytest

test-v:
	@echo "[test-v] Running Tests (Verbose)..."
	$(CMD) pytest -v

test-s:
	@echo "[test-s] Running Tests (Show Output)..."
	$(CMD) pytest -s

test-f:
	@echo "[test-f] Running Tests (Stop on First Failure)..."
	$(CMD) pytest -x

test-allure:
	@echo "[test-allure] Running Tests with Allure Results..."
	$(CMD) pytest --alluredir=allure-results

check: format lint type-check test
	@echo "[check] All checks passed!"

# ==============================================================================
# DOCKER
# ==============================================================================
docker-build:
	@echo "[docker-build] Building Docker image: $(IMAGE_NAME):$(TAG)"
	docker build -t $(IMAGE_NAME):$(TAG) .

docker-run:
	@echo "[docker-run] Starting container: $(IMAGE_NAME)"
	docker run --rm --env-file .env --name $(IMAGE_NAME)-container $(IMAGE_NAME):$(TAG)

docker-clean:
	@echo "[docker-clean] Deep cleaning Docker resources..."
	docker system prune -f
	docker rmi $$(docker images -f "dangling=true" -q) 2>/dev/null || true

docker-dev:
	@echo "[docker-dev] Starting Dev Container..."
	docker run --rm \
		-v $(PWD):/app \
		-v /app/.venv \
		$(IMAGE_NAME):$(TAG) python -m app.main
