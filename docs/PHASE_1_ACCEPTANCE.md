# Phase 1 Acceptance

## Fecha

2026-06-07

## Estado

APPROVED

## Comandos usados

```bash
docker compose up --build
docker compose exec api python scripts/seed.py
```

Verificaciones técnicas ejecutadas durante la estabilización:

```bash
cd apps/api && PYTHONPATH=. pytest tests -q
cd apps/api && ruff check src tests scripts
cd apps/web && npm run lint
cd apps/web && npm run build
```

## Servicios levantados

- `db`: PostgreSQL con pgvector.
- `api`: FastAPI en `http://localhost:8000`.
- `web`: Next.js en `http://localhost:3000`.

## Bugs encontrados

- El frontend mostraba `Failed to fetch` en Documentos al intentar importar el sample.
- El seed fallaba dentro del contenedor API con:

```txt
OSError: [Errno 35] Resource deadlock avoided
```

- Las 20 preguntas sample no aparecían porque el seed no terminaba correctamente.

## Fix aplicado

- El sample dejó de depender del bind mount `/workspace/data`.
- La imagen API ahora incluye `data/samples` dentro de `/app/data/samples`.
- `SAMPLE_QUESTIONS_PATH` apunta a `/app/data/samples/questions.sample.jsonl`.
- Se agregó resolución robusta de ruta de sample con fallback.
- El cliente web ahora muestra un error más claro si la API no responde.

## Checklist de verificación

- [x] `docker compose up --build` ejecuta la infraestructura local.
- [x] Servicio `db` disponible para API.
- [x] Servicio `api` disponible en puerto `8000`.
- [x] Servicio `web` disponible en puerto `3000`.
- [x] Seed de preguntas sample ejecutable con `docker compose exec api python scripts/seed.py`.
- [x] 20 preguntas sample importables.
- [x] Dashboard puede consultar API.
- [x] Banco de preguntas puede listar preguntas.
- [x] Práctica básica puede cargar una pregunta.
- [x] Registro de intentos implementado.
- [x] Analytics básicos implementados.
- [x] Scoring de temas implementado.
- [x] Plan diario básico implementado.
- [x] La app funciona sin API key.
- [x] Tests backend pasan.
- [x] Lint backend pasa.
- [x] Typecheck/build frontend pasa.

## Decisión final

APPROVED
