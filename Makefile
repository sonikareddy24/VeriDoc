.PHONY: setup run-backend run-frontend test generate-data eval report clean

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

setup:
	@echo "Setting up Python virtual environment and dependencies..."
	@if [ ! -d "$(VENV)" ]; then /opt/homebrew/bin/python3.11 -m venv $(VENV); fi
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt
	@cd frontend && npm install
	@echo "Setup complete!"

run-backend:
	@echo "Starting FastAPI backend on http://127.0.0.1:8000..."
	@PYTHONPATH=. $(VENV)/bin/uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

run-frontend:
	@echo "Starting Vite frontend on http://localhost:5173..."
	@cd frontend && npm run dev

test:
	@echo "Running backend and evaluation test suite with coverage..."
	@PYTHONPATH=. $(VENV)/bin/pytest backend/tests eval/tests --cov=backend/app --cov=eval --cov-report=term-missing

generate-data:
	@echo "Generating synthetic dataset..."
	@PYTHONPATH=. $(PYTHON) eval/generator/generate_dataset.py --profile quick

eval:
	@echo "Running research evaluation benchmark..."
	@PYTHONPATH=. $(PYTHON) eval/run_eval.py --profile quick

report:
	@echo "Generating evaluation summary report..."
	@PYTHONPATH=. $(PYTHON) eval/generate_summary_report.py

clean:
	@rm -rf data/sessions_temp/*
	@rm -rf .pytest_cache
	@rm -rf frontend/dist
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "Cleaned temporary files."
