.PHONY: help install install-dev test lint format type-check clean run-dashboard run-jupyter docs
.DEFAULT_GOAL := help

# Project variables
PYTHON := python
PIP := pip
SRC_DIR := src
TESTS_DIR := tests
DOCS_DIR := docs

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	$(PIP) install -e .

install-dev: ## Install development dependencies
	$(PIP) install -e ".[dev,docs]"
	pre-commit install

test: ## Run tests
	pytest $(TESTS_DIR) -v

test-cov: ## Run tests with coverage
	pytest $(TESTS_DIR) -v --cov=$(SRC_DIR) --cov-report=html --cov-report=term

lint: ## Run linting
	flake8 $(SRC_DIR) $(TESTS_DIR)
	mypy $(SRC_DIR)

format: ## Format code
	black $(SRC_DIR) $(TESTS_DIR)
	isort $(SRC_DIR) $(TESTS_DIR)

format-check: ## Check code formatting
	black --check $(SRC_DIR) $(TESTS_DIR)
	isort --check-only $(SRC_DIR) $(TESTS_DIR)

type-check: ## Run type checking
	mypy $(SRC_DIR)

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

run-dashboard: ## Run Streamlit dashboard
	$(PYTHON) run_app.py

run-jupyter: ## Start Jupyter notebook server
	jupyter notebook analysis/

docs: ## Build documentation
	cd $(DOCS_DIR) && make html

docs-serve: ## Serve documentation locally
	cd $(DOCS_DIR)/_build/html && $(PYTHON) -m http.server 8000

setup-dev: install-dev ## Setup development environment
	@echo "Development environment setup complete!"
	@echo "Run 'make run-dashboard' to start the Streamlit app"
	@echo "Run 'make run-jupyter' to start Jupyter notebooks"

check-all: format-check lint type-check test ## Run all checks (formatting, linting, type checking, tests)

# Docker commands
docker-build: ## Build Docker image
	docker build -t hospitals-access-peru .

docker-run: ## Run Docker container
	docker run -p 8501:8501 hospitals-access-peru

# Data commands
download-data: ## Download required datasets (if needed)
	@echo "Data files should be placed in the data/ directory"
	@echo "See README.md for data source information"

validate-data: ## Validate data files exist and are readable
	$(PYTHON) -c "from src.utils import load_and_clean_data; print('✅ Data validation passed')"