# ICFES OS

ICFES OS es una plataforma local-first para preparar Saber 11 convirtiendo preguntas, intentos y errores en datos de estudio. La Fase 1 incluye banco de preguntas, practica, registro de intentos, analitica, scoring de temas y plan diario basico.

## Ejecutar con Docker

```bash
cp .env.example .env
docker compose up --build
```

Servicios:

- Web: http://localhost:3000
- API: http://localhost:8000
- Docs FastAPI: http://localhost:8000/docs
- PostgreSQL: localhost:5432

Para cargar preguntas sample desde la UI usa Dashboard o Documentos -> `Importar sample`. Tambien puedes usar:

```bash
make seed
```

Si venias de una build anterior y el sample falla dentro de Docker, reconstruye la imagen API:

```bash
docker compose up --build
```

## Comandos utiles

```bash
make dev      # docker compose up --build
make up       # levantar en background
make down     # detener servicios
make seed     # importar data/samples/questions.sample.jsonl
make test     # pytest backend
make lint     # ruff backend + lint frontend
```

## Desarrollo local sin Docker

Backend:

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn src.main:app --reload
```

Frontend:

```bash
cd apps/web
npm install
npm run dev
```

## Importar preguntas

Formato JSONL soportado:

```json
{"id":"q001","year":2024,"area":"ciencias_naturales","subarea":"quimica","topic":"enlaces_quimicos","statement":"...","option_a":"...","option_b":"...","option_c":"...","option_d":"...","correct_answer":"B","explanation":"..."}
```

Opciones:

- UI: `/documents`, subir `.jsonl`, `.csv` o `.pdf`.
- API: `POST /documents/import-jsonl`, `POST /documents/import-csv`, `POST /documents/extract-pdf`.
- CLI local: `cd apps/api && python scripts/import_jsonl.py ../../data/samples/questions.sample.jsonl`.
- Docker: `docker compose exec api python scripts/seed.py`.

## IA y embeddings

La app funciona sin API keys. Sin keys usa clasificacion heuristica y busqueda por texto/tema.

Para IA opcional:

```bash
OPENAI_API_KEY=...
AI_PROVIDER=openai
ENABLE_EMBEDDINGS=false
```

Tambien hay soporte inicial para Anthropic:

```bash
ANTHROPIC_API_KEY=...
AI_PROVIDER=anthropic
```

## Fase 1 implementada

- Docker Compose con PostgreSQL + pgvector, API y web.
- Modelos principales con SQLAlchemy y migracion Alembic.
- Importacion JSONL/CSV y extraccion basica de texto PDF.
- Seed con 20 preguntas inventadas.
- Dashboard, documentos, banco de preguntas, practica, analitica, plan diario y settings.
- Registro de intentos con repeticion espaciada simple.
- Scoring por tema con pesos estrategicos por area.
- Clasificacion IA opcional con fallback heuristico.
- Tutor IA opcional con fallback manual.

## Pendiente Fase 2

- Embeddings persistidos y busqueda semantica real para lotes completos.
- Cola visual de revision para extracciones PDF imperfectas.
- Edicion masiva de clasificaciones.
- Simulacros cortos con resumen de sesion.
- Analitica de progreso diario y calibracion de puntaje.
- Tutor con memoria de errores frecuentes.
