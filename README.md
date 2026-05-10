# CiberSpar

**Simulador de sparring conversacional contra ingeniería social.**

CiberSpar permite a colaboradores de organizaciones entrenarse contra ingeniería
social mediante conversaciones en tiempo real con un atacante simulado que
adapta sus tácticas turno a turno, aprende del estilo defensivo del usuario
durante la sesión, y al final le revela en primera persona el razonamiento
estratégico completo que usó.

A diferencia de los productos de awareness existentes (tests de opción
múltiple, simulaciones de phishing por correo), aquí el usuario sostiene una
conversación viva, decide en lenguaje natural, y enfrenta a un adversario
que se reconfigura.

CiberSpar es complementario de CiberTeatro (otro producto del ecosistema
HackTheMinds): allá se **observa** al personaje ser atacado; aquí se
**encarna** al personaje (o al sí mismo) sosteniendo la defensa.

---

## Principios no negociables (codificados, no solo declarados)

| Principio | Cómo se codifica |
|---|---|
| Sesiones efímeras | El `SessionStore` solo escribe en Redis y siempre con TTL. No existe API de export. |
| Indicador de efemeridad visible | Badge persistente en toda la pantalla del sparring + endpoint `/debrief/{id}/wipe` que devuelve evidencia. |
| Aprendizaje intra-sesión acotado | El `DefenseModel` vive solo en `session:{id}:defense` con TTL; nunca se serializa a Postgres. |
| Salida digna siempre disponible | Botón "Salir con dignidad" en cualquier turno → status `left_dignified`, sin penalización ni etiqueta de abandono. |
| Control de intensidad por el usuario | Dial 1-12 en la pantalla de configuración; el nivel se valida al crear la sesión y no se cambia durante la sesión. |
| Métricas agregadas, n≥10 | `Settings` valida `AGGREGATION_MIN_N>=10` en prod; `aggregated_*` queries suprimen buckets por debajo del umbral. |
| Límite de 30 minutos por sesión | `Settings` rechaza `SESSION_TTL_SECONDS>1800`; el WebSocket fuerza cierre narrativo digno al expirar. |

---

## Arquitectura

```
┌──────────────────────────────────────────────────────────────────────┐
│ Frontend (Next.js 14 + Tailwind + Framer Motion)                     │
│   /                 onboarding + consentimiento                      │
│   /configurar       dial de nivel + arquetipo + personaje            │
│   /sparring/[id]    chat en tiempo real (WebSocket) + Caja Negra     │
│   /debrief/[id]     6 paneles: resumen, confesión, replay, etc.      │
│   /demo             nivel 11 — guion pre-escrito con anotaciones     │
│   /facilitador      panel agregado n>=10                             │
└──────────────────────────────────────────────────────────────────────┘
                                 │
              REST + WebSocket   │
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Backend (FastAPI + asyncio)                                          │
│   POST /sessions                  crea sesión (Redis, TTL=1800)      │
│   WS   /ws/sessions/{id}          chat en vivo                       │
│   GET  /debrief/{id}              confesor + coach + anotaciones     │
│   POST /debrief/{id}/wipe         destruye y prueba el borrado       │
│   GET  /demo/nivel-11             guion pre-escrito                  │
│   /facilitator/*                  CRUD personajes + métricas n>=10   │
└──────────────────────────────────────────────────────────────────────┘
        │                        │                       │
        ▼                        ▼                       ▼
   Anthropic API               Redis (TTL)          Postgres
   (claude-sonnet-4-6,         estado de            catálogos +
   claude-haiku-4-5            sesión + modelo      facilitador +
   para evaluador)             de defensa           buckets agregados
```

### Capas del backend

```
backend/app/
  config.py              # guard rails de TTL e n agregado
  main.py                # FastAPI factory + lifespan
  clients/               # Anthropic + Redis singletons
  db/                    # SQLAlchemy async (catálogos + métricas SOLAMENTE)
  models/                # Pydantic: session, attacker, character, defense, debrief
  prompts/               # 5 prompts versionados (ver PEDAGOGIA.md)
  services/              # session_store, attacker_engine, evaluator,
                         # safety_filter, end_conditions, debrief_service,
                         # session_lifecycle, metrics
  routers/               # sessions, sparring, debrief, demo, facilitator, health
  data_catalogs.py       # cargador de los JSON
data/                    # 4 catálogos (atacantes, personajes, marcas, controles)
                         #   + guion pre-escrito de nivel 11
tests/                   # 49 tests (ver "Tests")
```

---

## Quickstart local

### Opción A: Docker (recomendado)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend:  http://localhost:8000/docs

### Opción B: dev nativo

Levanta solo Redis y Postgres con docker compose, y corre la app desde tu host:

```bash
docker compose -f docker-compose.dev.yml up -d

# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env       # luego edita ANTHROPIC_API_KEY
uvicorn app.main:app --reload --port 8000

# Frontend (en otra terminal)
cd frontend
npm install
npm run dev
```

---

## Tests

```bash
cd backend
pytest -q
```

Suite incluye:

- `test_config.py` — TTL > 30 min rechazado; prod no puede aflojar n≥10.
- `test_session_store.py` — TTL fijado en cada write; expiración real; destroy borra todo; no hay cross-session.
- `test_safety_filter.py` — marcas reales reemplazadas; dominios reales eliminados; líneas rojas neutralizadas.
- `test_catalogs.py` — 6 arquetipos completos, ≥30 marcas ficticias, controles válidos.
- `test_metrics_threshold.py` — buckets con n<10 se suprimen totalmente al leer.
- `test_session_lifecycle.py` — niveles 1-5 forzosamente como uno mismo; 6+ requieren personaje + arquetipo elegidos.
- `test_models.py`, `test_health.py` — round-trip y boot.

---

## Modelo de privacidad

- **Cero persistencia entre sesiones.** Postgres solo guarda: catálogos
  (estáticos), configuración del facilitador, y contadores agregados con
  esquema bucketizado por `(iso_year, iso_week, org, level, archetype,
  defender_kind, result)`. Ningún row es re-identificable.
- **Logs sin contenido.** Las intercepciones del `safety_filter` se
  registran únicamente por categoría.
- **No hay OSINT.** El atacante nunca recibe datos del jugador real.
  Cuando el jugador encarna un personaje, el atacante recibe solo la ficha
  ficticia.
- **Borrado verificable.** Al cerrar el debrief, `POST /debrief/{id}/wipe`
  destruye las claves Redis y devuelve la lista exacta como prueba.
- **Cumplimiento LOPDP Ecuador.** Plantilla contractual sugerida en
  [LEGAL.md](./LEGAL.md).

---

## Documentos

- [PEDAGOGIA.md](./PEDAGOGIA.md) — marco andragógico, 12 niveles, 6 arquetipos, justificación de cada decisión.
- [LEGAL.md](./LEGAL.md) — plantilla de cláusula contractual para cliente final.

---

## Lo que CiberSpar no hace

- No persiste conversaciones, modelos de defensa ni datos de sesión más allá del TTL de Redis.
- No procesa OSINT del usuario real.
- No usa nombres de marcas, bancos, instituciones o personas reales.
- No expone ningún dato individual al facilitador del cliente.
- No tiene "envío masivo" ni nada que ataque a personas reales fuera de la app.
- No usa fotos fotorrealistas para atacantes ni personajes.
- No usa tono punitivo, de examen, ni gamificación tipo Duolingo.
- No incluye niveles superiores a 12 ni "modos secretos".
- No permite al atacante romper el personaje durante el sparring (solo en el debrief).
- No excede 30 minutos por sesión bajo ninguna circunstancia.

---

## Licencia y autoría

Propiedad de **HackTheMinds**. Todos los derechos reservados.
