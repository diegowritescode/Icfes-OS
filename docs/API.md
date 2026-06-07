# API

Base local: `http://localhost:8000`

## Health

- `GET /health`

## Documents

- `GET /documents`
- `POST /documents/import-jsonl`
- `POST /documents/import-csv`
- `POST /documents/extract-pdf`
- `POST /documents/import-sample`

## Questions

- `GET /questions`
- `GET /questions/{id}`
- `PATCH /questions/{id}`
- `POST /questions/{id}/classify`
- `GET /questions/{id}/similar`

## Practice

- `GET /practice/next`
- `GET /practice/review-due`
- `POST /practice/attempt`

## Attempts

- `GET /attempts`
- `GET /attempts/stats`

## Analytics

- `GET /analytics/overview`
- `GET /analytics/by-area`
- `GET /analytics/by-topic`
- `GET /analytics/errors`
- `GET /analytics/priority-topics`

## Recommendations

- `POST /recommendations/daily-plan`

Body:

```json
{
  "available_minutes": 120,
  "area": "ciencias_naturales",
  "max_blocks": 3,
  "preference": "mixto"
}
```

## Tutor

- `POST /tutor/explain-error`

## Search

- `GET /search/text?q=porcentaje`
- `POST /search/semantic`
