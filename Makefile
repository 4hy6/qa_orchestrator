# ==============================================================================
# CONFIGURATION
# ==============================================================================
PYTHON_VERSION := 3.12
VENV_DIR       := .venv
CMD            := uv run
IMAGE_NAME     := qa-orchestrator
TAG            := latest

# ==============================================================================
# UTILS
# ==============================================================================
.PHONY: help install lint format test clean check docker-build docker-clean docker-run

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Core Targets:"
	@echo "  install        Install dependencies using uv"
	@echo "  clean          Remove all cache and temporary files"
	@echo ""
	@echo "QA Targets:"
	@echo "  lint           Run static analysis (Ruff)"
	@echo "  format         Auto-format code and sort imports"
	@echo "  test           Run pytest suite"
	@echo "  check          Run full pipeline (format -> lint -> test)"
	@echo ""
	@echo "Docker Targets:"
	@echo "  docker-build   Build optimized multi-stage image"
	@echo "  docker-run     Run container with automatic cleanup (--rm)"
	@echo "  docker-clean   Remove dangling images and system prune"

# ==============================================================================
# CORE
# ==============================================================================
install:
	@echo "Pinning Python $(PYTHON_VERSION) and syncing dependencies..."
	uv python pin $(PYTHON_VERSION)
	uv sync

clean:
	@echo "Cleaning up caches..."
	find . -type d -name "__pycache__" -exec rm -rf {}
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .ruff_cache .coverage .venv

# ==============================================================================
# QA PIPELINE
# ==============================================================================
lint:
	$(CMD) ruff check .

format:
	$(CMD) ruff check --fix .
	$(CMD) ruff format .

test:
	$(CMD) pytest tests -v

check: format lint test

# ==============================================================================
# DOCKER
# ==============================================================================
docker-build:
	@echo "Building Docker image: $(IMAGE_NAME):$(TAG)"
	docker build -t $(IMAGE_NAME):$(TAG) .

docker-run:
	@echo "Starting container: $(IMAGE_NAME)"
	docker run --rm --name $(IMAGE_NAME)-container $(IMAGE_NAME):$(TAG)

docker-clean:
	@echo "Deep cleaning Docker resources..."
	docker system prune -f
	docker rmi $$(docker images -f "dangling=true" -q) 2>/dev/null || true
