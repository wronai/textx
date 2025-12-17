.PHONY: help install install-dev test lint format clean build docs run-examples

help:
	@echo "NLP2CMD - Makefile commands"
	@echo ""
	@echo "  install        Install package"
	@echo "  install-dev    Install package with dev dependencies"
	@echo "  test           Run tests"
	@echo "  lint           Run linters"
	@echo "  format         Format code"
	@echo "  clean          Clean build artifacts"
	@echo "  build          Build package"
	@echo "  docs           Generate documentation"
	@echo "  run-examples   Run example scripts"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v --cov=nlp2cmd --cov-report=html --cov-report=term

lint:
	flake8 nlp2cmd/ tests/ --max-line-length=100
	mypy nlp2cmd/ --ignore-missing-imports

format:
	black nlp2cmd/ tests/ examples/
	isort nlp2cmd/ tests/ examples/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python setup.py sdist bdist_wheel

docs:
	cd docs && make html

run-examples:
	@echo "Running basic examples..."
	python examples/basic_usage.py
	@echo ""
	@echo "For LLM examples (requires model download):"
	@echo "  python examples/advanced_llm.py"

# Development helpers
watch-test:
	pytest-watch tests/ -v

check: lint test
	@echo "All checks passed!"

up:
	docker-compose up --build


down:
	docker-compose down
