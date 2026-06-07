.PHONY: dev up down seed test lint api-dev web-dev migrate

dev:
	docker compose up --build

up:
	docker compose up -d --build

down:
	docker compose down

migrate:
	cd apps/api && alembic upgrade head

seed:
	docker compose exec api python scripts/seed.py /workspace/data/samples/questions.sample.jsonl

test:
	cd apps/api && PYTHONPATH=. pytest

lint:
	cd apps/api && ruff check src tests scripts
	cd apps/web && npm run lint

api-dev:
	cd apps/api && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

web-dev:
	cd apps/web && npm run dev
