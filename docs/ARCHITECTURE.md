# Architecture

## Monorepo

```txt
apps/api  FastAPI + SQLAlchemy + Alembic
apps/web  Next.js + TypeScript + Tailwind + Recharts
data      raw/processed/samples
docs      product and technical docs
```

## Backend

La API separa rutas, repositorios y servicios:

- `api/routes`: contratos HTTP.
- `repositories`: consultas y persistencia.
- `services`: scoring, recomendador, practica, ingesta, IA y busqueda.
- `models`: entidades SQLAlchemy.
- `schemas`: DTOs Pydantic.

Los endpoints no contienen logica compleja; delegan a servicios.

## Base de datos

PostgreSQL con extension `vector`. La Fase 1 usa las tablas:

- `documents`
- `questions`
- `classifications`
- `attempts`
- `study_sessions`
- `daily_plans`
- `question_embeddings`

Alembic crea el esquema inicial y habilita `pgvector`.

## Flujo de datos

```txt
JSONL/CSV/PDF
  -> importer/extractor
  -> Document + Question + Classification
  -> Practice Attempt
  -> Analytics + Scoring
  -> Daily Plan
```

## IA

Hay abstraccion de provider:

- OpenAI opcional.
- Anthropic opcional.
- Fallback heuristico si no hay keys o si falla el proveedor.

Embeddings estan preparados en modelo y servicio, pero la Fase 1 usa fallback por texto/tema salvo configuracion explicita.

## Extensibilidad

La arquitectura permite agregar:

- nuevos importadores;
- nuevos providers de IA;
- clasificadores por lote;
- motor de simulacros;
- tareas background;
- calibracion de puntaje;
- frontend de cola de revision.
