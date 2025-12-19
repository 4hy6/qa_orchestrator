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
.PHONY: docker-build docker-run docker-clean

# ==============================================================================
# HELP & DOCS
# ==============================================================================
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Core Targets:"
	@echo "  install        Install dependencies and pin Python version"
	@echo "  clean          Remove all cache, venv, and temporary files"
	@echo ""
	@echo "QA & Code Quality:"
	@echo "  format         Auto-format code (Ruff)"
	@echo "  lint           Run static code analysis (Ruff)"
	@echo "  type-check     Run static type checking (Mypy)"
	@echo "  test           Run unit tests (Pytest)"
	@echo "  check          Run FULL pipeline: format -> lint -> type -> test"
	@echo ""
	@echo "Docker Targets:"
	@echo "  docker-build   Build optimized multi-stage image"
	@echo "  docker-run     Run container with auto-cleanup (--rm)"
	@echo "  docker-clean   Remove dangling images and system prune"

# ==============================================================================
# CORE
# ==============================================================================
install:
	@echo "[install] Pinning Python $(PYTHON_VERSION) and syncing dependencies..."
	uv python pin $(PYTHON_VERSION)
	uv sync

clean:
	@echo "[clean] Cleaning up caches and artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .ruff_cache .coverage .mypy_cache $(VENV_DIR)

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
	$(CMD) mypy app config

test:
	@echo "[test] Running Tests (Pytest)..."
	$(CMD) pytest tests -v

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
	docker run --rm --name $(IMAGE_NAME)-container $(IMAGE_NAME):$(TAG)

docker-clean:
	@echo "[docker-clean] Deep cleaning Docker resources..."
	docker system prune -f
	docker rmi $$(docker images -f "dangling=true" -q) 2>/dev/null || true
