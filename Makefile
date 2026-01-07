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
.PHONY: compose-up compose-down compose-logs load-test load-ui

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
	@echo "Infrastructure & Docker:"
	@echo "  compose-up     Start full environment (DB + App)"
	@echo "  compose-down   Stop and remove containers"
	@echo "  compose-logs   Show real-time logs"
	@echo "  compose-ps     Show containers status"
	@echo "  docker-build   Build optimized multi-stage image"
	@echo "  docker-run     Run container with auto-cleanup"
	@echo "  docker-clean   System prune and cleanup"
	@echo "  docker-dev     Run with Hot Reload (bind mounts)"
	@echo ""
	@echo "Performance Testing:"
	@echo "  load-test      Run headless Locust test (10s)"
	@echo "  load-ui        Start Locust Web UI"

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
# Local run: host override
	POSTGRES_HOST=localhost $(CMD) pytest

test-v:
	@echo "[test-v] Running Tests (Verbose)..."
# Local run: host override
	POSTGRES_HOST=localhost $(CMD) pytest -v

test-s:
	@echo "[test-s] Running Tests (Show Output)..."
# Local run: host override
	POSTGRES_HOST=localhost $(CMD) pytest -s

test-f:
	@echo "[test-f] Running Tests (Stop on First Failure)..."
# Local run: host override
	POSTGRES_HOST=localhost $(CMD) pytest -x

test-allure:
	@echo "[test-allure] Running Tests with Allure Results..."
# Local run: host override
	POSTGRES_HOST=localhost $(CMD) pytest --alluredir=allure-results

report:
	@echo "[report] Generating and opening Allure Report..."
	allure serve allure-results

check: format lint type-check test
	@echo "[check] All checks passed!"

# ==============================================================================
# DOCKER (App Build)
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

# ==============================================================================
# INFRASTRUCTURE (Docker Compose)
# ==============================================================================
compose-up:
	@echo "[compose-up] Starting Infrastructure..."
	docker compose up -d

compose-down:
	@echo "[compose-down] Stopping Infrastructure..."
	docker compose down

compose-logs:
	@echo "[compose-logs] Showing Infrastructure Logs..."
	docker compose logs -f

compose-ps:
	@echo "[compose-ps] Infrastructure status..."
	docker compose ps

# ==============================================================================
# PERFORMANCE TESTING (Locust)
# ==============================================================================
load-test:
	@echo "[load-test] Running headless performance test (10s)..."
	$(CMD) locust \
		-f tests/load/locustfile.py \
		--host http://localhost:3001 \
		--users 10 \
		--spawn-rate 2 \
		--run-time 10s \
		--headless \
		--html locust_report.html

load-ui:
	@echo "[load-ui] Starting Locust Web UI at http://localhost:8089..."
	$(CMD) locust -f tests/load/locustfile.py --host http://localhost:3001

# ==============================================================================
# DATABASE MIGRATIONS (Alembic)
# ==============================================================================
.PHONY: migrate-create migrate-up migrate-down migrate-history

# Usage: make migrate-create m="Initial migration"
migrate-create:
	@echo "[migrate-create] Generating new migration script..."
	POSTGRES_HOST=localhost $(CMD) alembic revision --autogenerate -m "$(m)"

migrate-up:
	@echo "[migrate-up] Applying all pending migrations..."
	POSTGRES_HOST=localhost $(CMD) alembic upgrade head

migrate-down:
	@echo "[migrate-down] Rolling back last migration..."
	POSTGRES_HOST=localhost $(CMD) alembic downgrade -1

migrate-history:
	@echo "[migrate-history] Showing migrations history..."
	$(CMD) alembic history --verbose
