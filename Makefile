.PHONY: help install test lint format clean run-demo

help:
	@echo "Risk MC - Monte Carlo Engine for Enterprise Risk Quantification"
	@echo ""
	@echo "Available commands:"
	@echo "  make install     - Install dependencies"
	@echo "  make test        - Run test suite"
	@echo "  make lint        - Run linter (ruff)"
	@echo "  make format      - Format code with black"
	@echo "  make clean       - Clean artifacts and cache"
	@echo "  make run-demo    - Run portfolio simulation demo"
	@echo ""

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v --tb=short

test-cov:
	pytest tests/ -v --cov=src/risk_mc --cov-report=html --cov-report=term

lint:
	ruff check src/ tests/ scripts/

format:
	black src/ tests/ scripts/

clean:
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf artifacts/*.png
	rm -rf artifacts/*.csv
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

run-demo:
	python scripts/demo_portfolio.py

all: format lint test run-demo
