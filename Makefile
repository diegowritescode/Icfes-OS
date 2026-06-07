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
	docker compose exec api python scripts/seed.py

test:
	if command -v pytest >/dev/null 2>&1; then \
		cd apps/api && PYTHONPATH=. pytest tests -q; \
	else \
		docker compose exec -T api pytest tests -q; \
	fi

lint:
	if command -v ruff >/dev/null 2>&1; then \
		cd apps/api && ruff check src tests scripts; \
	else \
		docker compose exec -T api ruff check src tests scripts; \
	fi
	if test -d apps/web/node_modules; then \
		cd apps/web && npm run lint; \
	else \
		docker compose exec -T web npm run lint; \
	fi

api-dev:
	cd apps/api && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

web-dev:
	cd apps/web && npm run dev
