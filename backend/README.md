# CiberTeatro · Backend

API FastAPI de la plataforma. Este README cubre solo el backend; el
README de la raíz del repo describe el producto completo y los
principios no negociables (se entrega en el Bloque 12).

## Estado por bloque
- [x] Bloque 1: estructura FastAPI, cliente Anthropic, base de datos, modelos
- [ ] Bloque 2: catálogo de marcas ficticias + safety_filter + tests
- [ ] Bloque 3: prompts versionados
- [ ] Bloque 4: endpoints (personaje, día triple, disección)

## Estructura
```
backend/
  app/
    core/          config, enums, database
    models/        SQLAlchemy ORM
    schemas/       Pydantic v2
    services/      cliente Anthropic, catálogo de marcas
    routers/       endpoints HTTP
    prompts/       (Bloque 3) prompts del sistema versionados
    data/          marcas_ficticias.json (Bloque 2)
  tests/           pytest
```

## Correr en local
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # luego edita
uvicorn app.main:app --reload
```

## Tests
```bash
pytest
```

## Compromisos codificados
- `MAX_DIFFICULTY = 3` (CHECK constraint en `dias_triples`).
- `MIN_AGGREGATE_N = 10` para cualquier reporte al empleador.
- Catálogo de marcas ficticias cerrado; el `safety_filter` (Bloque 2)
  rechaza generación con marcas reales.
- Disclaimer permanente en `Personaje.disclaimer_visible`, leído por el frontend.
