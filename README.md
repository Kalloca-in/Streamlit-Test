# CiberTeatro

Plataforma de awareness en ciberseguridad mediante **dramatizaciones interactivas
en triple rol**. El usuario no es atacado: observa cómo se construye un ataque
contra un personaje ficticio en sus tres frentes —ciudadano, colaborador,
cliente— y aprende a reconocer el mismo gancho psicológico cuando lo vea en su
propia vida.

> **Diferenciador.** Ningún producto en el mercado trabaja al colaborador como
> "consumidor triple": su día atravesado por ataques en sus tres roles. La
> superficie real es 24/7 y los mismos ganchos golpean en los tres frentes.

## Principios no negociables

Estos cinco principios están **codificados en la arquitectura**, no solo
declarados:

1. **Nunca se ataca al usuario real.** Toda dramatización ocurre contra
   personajes ficticios declarados como tales en cada pantalla.
2. **Nunca se solicita ni procesa OSINT del usuario real.** Los inputs son
   sobre el personaje o sobre la propia experiencia.
3. **Marcas, bancos, escuelas, instituciones son ficticios.** Catálogo cerrado
   en `backend/app/data/marcas_ficticias.json` (30 entradas, dominios `.example`
   / `.test`). El `safety_filter` rechaza cualquier marca real.
4. **Detección post-hoc, no captura.** Cada Día Triple termina en una
   revelación explícita de los indicadores que el personaje (y el usuario
   observador) deberían haber detectado.
5. **La dificultad escala pedagógicamente.** Techo absoluto = 3. CHECK
   constraint en la DB + validación en el filtro + `NivelDificultad` enum.

Detalles del marco didáctico en [`PEDAGOGIA.md`](./PEDAGOGIA.md).

## Stack

| Capa | Tecnología |
|------|------------|
| Backend | Python 3.11, FastAPI 0.115, SQLAlchemy 2.0 |
| LLM | Anthropic API (claude-sonnet-4-5 por defecto) |
| Base de datos | PostgreSQL 16 (prod) · SQLite en memoria (tests) |
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind, Framer Motion |
| Empaquetado | Docker + docker-compose |

## Estructura

```
Streamlit-Test/
├── backend/
│   ├── app/
│   │   ├── core/            config, enums, database (tipos portables GUID/JSONType)
│   │   ├── models/          ORM SQLAlchemy
│   │   ├── schemas/         Pydantic v2
│   │   ├── services/        catálogo, safety_filter, anthropic_client, dominio
│   │   ├── routers/         endpoints HTTP
│   │   ├── prompts/         prompts versionados (IP del producto)
│   │   ├── data/
│   │   │   ├── marcas_ficticias.json         (catálogo cerrado, 30 entradas)
│   │   │   ├── blocklist_marcas_reales.py    (~200 marcas reales bloqueadas)
│   │   │   └── seed_personajes.json          (6 personajes + Días Triples)
│   │   ├── seed.py          carga inicial idempotente
│   │   └── main.py
│   ├── tests/               pytest (54 tests verdes)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/                 rutas: /, /personajes, /dia-triple, /diseccion,
│   │                                /reflejo, /dashboard, /biblioteca, /facilitador
│   ├── components/          DisclaimerBar, Avatar, Dramatizacion (SMS / chat / correo),
│   │                          DecisionPanel, MensajeAnotado, Timeline, ...
│   ├── lib/                 api client, types, utils, persistencia local
│   ├── tailwind.config.ts
│   └── Dockerfile
├── docker-compose.yml
├── PEDAGOGIA.md             marco didáctico para el cliente final
└── README.md
```

## Correr en local

### Opción A — Docker (recomendada)

```bash
cp backend/.env.example backend/.env  # opcional, edita ANTHROPIC_API_KEY
docker compose up --build
```

Esto levanta:
- `db` — PostgreSQL 16 con healthcheck.
- `backend` — FastAPI en `http://localhost:8000` (`/docs` para Swagger).
- `seed` — corre `python -m app.seed` una sola vez con los 6 personajes.
- `frontend` — Next.js en `http://localhost:3000`.

Tras `up`, visita `http://localhost:3000`, elige un personaje y vive su día.

### Opción B — Manual (sin Docker)

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # edita
# Levanta Postgres aparte (o usa SQLite para dev simple)
python -m app.seed
uvicorn app.main:app --reload

# Frontend
cd ../frontend
npm install
echo "BACKEND_URL=http://localhost:8000" > .env.local
npm run dev
```

## Tests

```bash
cd backend
source .venv/bin/activate
pytest -q
```

54 tests verdes cubren: smoke + catálogo cerrado (≥30 entradas, TLDs reservados,
sin colisión con blocklist) + `safety_filter` (marcas reales, OSINT, líneas
rojas, dificultad excedida) + endpoints E2E (SQLite en memoria) + prompts
versionados + integridad del seed.

```bash
# Frontend (typecheck)
cd ../frontend
npm run typecheck
```

## Endpoints clave

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Status de la API |
| GET | `/principios` | Principios no negociables como dato público |
| GET | `/marcas` | Catálogo cerrado de marcas ficticias |
| GET/POST | `/personajes` | Listar / crear personajes (con filtros) |
| GET/POST | `/dias-triples` | Días Triples (POST pasa por `safety_filter`) |
| POST | `/sesiones` | Iniciar una sesión |
| POST | `/sesiones/{id}/decisiones` | Registrar decisión por acto |
| POST | `/sesiones/{id}/reflexion` | Registrar reflexión privada |
| GET | `/sesiones/usuario/{uid}/progreso` | Dashboard del usuario |
| GET | `/disecciones/acto/{id}` | Indicadores estructurados de un acto |
| GET | `/reportes/organizacion/{id}/agregado` | Reporte agregado al facilitador (n ≥ MIN_AGGREGATE_N) |

Documentación completa: `http://localhost:8000/docs`.

## Advertencias de uso

- **Es una plataforma de awareness, no de ataque real.** No incluye ni admitirá
  funciones para enviar correos / SMS / mensajes a destinatarios reales.
- **No expone datos individuales al empleador.** Todo reporte agregado, con
  `MIN_AGGREGATE_N = 10` por defecto.
- **No procesa OSINT del usuario real.** El sistema rechaza explícitamente
  patrones de ese tipo en pre-llamada al modelo.
- **Tono coach, no inspector.** El usuario es aprendiz, no sospechoso.

## Cumplimiento

Documenta tratamiento mínimo de datos para LOPDP de Ecuador: identificador
externo opaco por usuario, finalidad acotada (capacitación), no se solicitan
datos personales sensibles, datos en tránsito y reposo cifrados (HTTPS y
cifrado de PostgreSQL al ser desplegado), reportes siempre agregados.
