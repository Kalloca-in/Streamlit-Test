"""CRUD y búsqueda de personajes ficticios."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import Arquetipo, NivelDificultad
from app.models.personaje import Personaje
from app.schemas.personaje import PersonajeCreate
from app.services.marcas_catalog import slugs_validos


class PersonajesService:
    @staticmethod
    def listar(
        db: Session,
        arquetipo: Arquetipo | None = None,
        nivel: NivelDificultad | None = None,
        organizacion_id: UUID | None = None,
        solo_semilla: bool = False,
    ) -> list[Personaje]:
        stmt = select(Personaje)
        if arquetipo:
            stmt = stmt.where(Personaje.arquetipo == arquetipo)
        if nivel:
            stmt = stmt.where(Personaje.nivel_sugerido == nivel)
        if organizacion_id:
            stmt = stmt.where(
                (Personaje.organizacion_id == organizacion_id)
                | (Personaje.es_semilla.is_(True))
            )
        if solo_semilla:
            stmt = stmt.where(Personaje.es_semilla.is_(True))
        return list(db.execute(stmt).scalars())

    @staticmethod
    def obtener(db: Session, personaje_id: UUID) -> Personaje | None:
        return db.get(Personaje, personaje_id)

    @staticmethod
    def crear(db: Session, payload: PersonajeCreate) -> Personaje:
        catalogo = slugs_validos()
        for slug in payload.marcas_asociadas:
            if slug not in catalogo:
                raise ValueError(f"marca_asociada '{slug}' no existe en el catálogo")

        p = Personaje(
            organizacion_id=payload.organizacion_id,
            nombre=payload.nombre,
            edad=payload.edad,
            arquetipo=payload.arquetipo,
            nivel_sugerido=payload.nivel_sugerido,
            cargo_ficticio=payload.cargo_ficticio,
            empresa_ficticia=payload.empresa_ficticia,
            contexto_familiar=payload.contexto_familiar,
            habitos_consumo=payload.habitos_consumo,
            vector_exposicion=payload.vector_exposicion.model_dump(),
            avatar_url=payload.avatar_url,
            marcas_asociadas=list(payload.marcas_asociadas),
            disclaimer_visible=True,
            es_semilla=payload.es_semilla,
        )
        db.add(p)
        db.commit()
        db.refresh(p)
        return p
