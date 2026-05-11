.PHONY: install lint format typecheck test dev clean migrate-create migrate-up migrate-down docker-up docker-down

install:
	uv sync

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/

typecheck:
	mypy src/

test:
	pytest tests/ -v --cov=src/

dev:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

clean:
	rm -rf .venv .ruff_cache .mypy_cache .pytest_cache __pycache__

migrate-create:
	alembic revision --autogenerate -m "$(name)"

migrate-up:
	alembic upgrade head

migrate-down:
	alembic downgrade -1

docker-up:
	docker compose up --build

docker-down:
	docker compose down -v
