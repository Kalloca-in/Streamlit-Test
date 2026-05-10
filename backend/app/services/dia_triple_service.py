"""CRUD de Días Triples + persistencia atómica de actos e indicadores."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.dia_triple import Acto, DiaTriple, Indicador
from app.schemas.dia_triple import DiaTripleCreate
from app.services.safety_filter import validate_dia_triple_safe


class DiaTripleService:
    @staticmethod
    def listar_por_personaje(db: Session, personaje_id: UUID) -> list[DiaTriple]:
        stmt = (
            select(DiaTriple)
            .where(DiaTriple.personaje_id == personaje_id)
            .options(selectinload(DiaTriple.actos).selectinload(Acto.indicadores))
        )
        return list(db.execute(stmt).scalars())

    @staticmethod
    def obtener(db: Session, dia_triple_id: UUID) -> DiaTriple | None:
        stmt = (
            select(DiaTriple)
            .where(DiaTriple.id == dia_triple_id)
            .options(selectinload(DiaTriple.actos).selectinload(Acto.indicadores))
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def crear(db: Session, payload: DiaTripleCreate) -> DiaTriple:
        # 1) Defensa post-generación: marcas, dificultad, líneas rojas.
        validate_dia_triple_safe(payload, contexto="DiaTripleService.crear")

        dt = DiaTriple(
            personaje_id=payload.personaje_id,
            titulo=payload.titulo,
            gancho_psicologico_raiz=payload.gancho_psicologico_raiz,
            nivel_dificultad=int(payload.nivel_dificultad),
            nota_revelacion=payload.nota_revelacion,
        )
        for acto_in in payload.actos:
            acto = Acto(
                orden=acto_in.orden,
                rol=acto_in.rol,
                canal=acto_in.canal,
                hora_dramatizada=acto_in.hora_dramatizada,
                remitente_aparente=acto_in.remitente_aparente,
                asunto=acto_in.asunto,
                cuerpo=acto_in.cuerpo,
                marca_ficticia_slug=acto_in.marca_ficticia_slug,
                opciones_decision=[op.model_dump() for op in acto_in.opciones_decision],
            )
            for ind_in in acto_in.indicadores:
                acto.indicadores.append(
                    Indicador(
                        tipo=ind_in.tipo,
                        fragmento=ind_in.fragmento,
                        explicacion=ind_in.explicacion,
                    )
                )
            dt.actos.append(acto)

        db.add(dt)
        db.commit()
        db.refresh(dt)
        return dt
