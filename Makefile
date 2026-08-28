.PHONY: help install run dev build lint format clean

help:
	@echo "Marker PDF Converter - Reflex Framework"
	@echo "========================================"
	@echo ""
	@echo "Available commands:"
	@echo "  make install     - Install dependencies"
	@echo "  make run         - Run development server"
	@echo "  make build       - Build production bundle"
	@echo "  make lint        - Lint Python code"
	@echo "  make format      - Format Python code"
	@echo "  make clean       - Remove build artifacts"
	@echo "  make help        - Show this help message"

install:
	pip install -e .
	pip install -r requirements.txt

run:
	reflex run

dev:
	reflex run --env dev

build:
	reflex build

lint:
	python -m black --check reflex_app.py
	python -m ruff check reflex_app.py

format:
	python -m black reflex_app.py
	python -m ruff check --fix reflex_app.py

clean:
	rm -rf .web
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .reflex
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
