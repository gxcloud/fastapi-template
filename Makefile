.PHONY: install lint format typecheck test dev clean migrate-create migrate-up migrate-down docker-up docker-down

install:
	uv sync

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

typecheck:
	uv run mypy src/

test:
	uv run pytest tests/ -v --cov=src/

dev:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

clean:
	rm -rf .venv .ruff_cache .mypy_cache .pytest_cache __pycache__ htmlcov/ .coverage *.egg-info dist/

migrate-create:
	@test -n "$(name)" || (echo "Usage: make migrate-create name=description" && exit 1)
	uv run alembic revision --autogenerate -m "$(name)"

migrate-up:
	uv run alembic upgrade head

migrate-down:
	uv run alembic downgrade -1

docker-up:
	docker compose up --build

docker-down:
	docker compose down -v
