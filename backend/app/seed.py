"""
Script de seed: carga 6 personajes ficticios + sus Días Triples.

Uso (con la app instalada y la DB accesible):
    python -m app.seed

El script:
1. Lee `app/data/seed_personajes.json`.
2. Crea cada Personaje (es_semilla=True).
3. Crea cada Día Triple asociado al Personaje correspondiente.
4. Cada paso pasa por safety_filter (validación post-generación).

Idempotencia: si ya existe un Personaje semilla con el mismo nombre,
omite su creación. Útil para correr el seed múltiples veces.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from sqlalchemy import select

from app.core.database import Base, SessionLocal, engine
from app.models.personaje import Personaje
from app.schemas.dia_triple import DiaTripleCreate
from app.schemas.personaje import PersonajeCreate
from app.services.dia_triple_service import DiaTripleService
from app.services.personajes_service import PersonajesService

log = logging.getLogger("app.seed")
logging.basicConfig(level=logging.INFO)

DATA_PATH = Path(__file__).resolve().parent / "data" / "seed_personajes.json"


def cargar_seed() -> list[dict]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def main() -> None:
    Base.metadata.create_all(bind=engine)
    data = cargar_seed()
    db = SessionLocal()
    try:
        creados = 0
        omitidos = 0
        for entry in data:
            personaje_payload = PersonajeCreate(**entry["personaje"])

            existente = db.execute(
                select(Personaje).where(
                    Personaje.nombre == personaje_payload.nombre,
                    Personaje.es_semilla.is_(True),
                )
            ).scalar_one_or_none()
            if existente is not None:
                log.info("[seed] %s ya existe, omito.", personaje_payload.nombre)
                omitidos += 1
                continue

            p = PersonajesService.crear(db, personaje_payload)
            log.info("[seed] Personaje creado: %s (%s)", p.nombre, p.id)

            dt_dict = entry["dia_triple"] | {"personaje_id": str(p.id)}
            dt_payload = DiaTripleCreate(**dt_dict)
            dt = DiaTripleService.crear(db, dt_payload)
            log.info("[seed] Día Triple creado: %s (%s)", dt.titulo, dt.id)
            creados += 1

        log.info("[seed] DONE — creados=%d, omitidos=%d", creados, omitidos)
    finally:
        db.close()


if __name__ == "__main__":
    main()
