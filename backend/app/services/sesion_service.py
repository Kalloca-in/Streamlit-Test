"""Sesiones, decisiones y reflexiones."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.enums import EstadoSesion, Rol
from app.models.dia_triple import Acto
from app.models.sesion import Decision, Reflexion, Sesion
from app.schemas.sesion import DecisionCreate, ReflexionCreate, SesionCreate


class SesionService:
    @staticmethod
    def crear(db: Session, payload: SesionCreate) -> Sesion:
        s = Sesion(
            usuario_id=payload.usuario_id,
            personaje_id=payload.personaje_id,
            dia_triple_id=payload.dia_triple_id,
            estado=EstadoSesion.INICIADA,
            iniciada_en=datetime.now(timezone.utc),
        )
        db.add(s)
        db.commit()
        db.refresh(s)
        return s

    @staticmethod
    def obtener(db: Session, sesion_id: UUID) -> Sesion | None:
        stmt = (
            select(Sesion)
            .where(Sesion.id == sesion_id)
            .options(selectinload(Sesion.decisiones), selectinload(Sesion.reflexion))
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def avanzar_estado(db: Session, sesion: Sesion, nuevo_estado: EstadoSesion) -> Sesion:
        sesion.estado = nuevo_estado
        if nuevo_estado == EstadoSesion.COMPLETADA and sesion.completada_en is None:
            sesion.completada_en = datetime.now(timezone.utc)
        db.commit()
        db.refresh(sesion)
        return sesion

    @staticmethod
    def registrar_decision(
        db: Session, sesion_id: UUID, payload: DecisionCreate
    ) -> Decision:
        sesion = db.get(Sesion, sesion_id)
        if sesion is None:
            raise LookupError("sesion_no_encontrada")
        acto = db.get(Acto, payload.acto_id)
        if acto is None:
            raise LookupError("acto_no_encontrado")

        opciones = {op["id"]: op for op in (acto.opciones_decision or [])}
        if payload.opcion_elegida not in opciones:
            raise ValueError("opcion_elegida_no_valida")
        fue_segura = bool(opciones[payload.opcion_elegida].get("es_segura", False))

        decision = Decision(
            sesion_id=sesion_id,
            acto_id=payload.acto_id,
            rol=payload.rol,
            opcion_elegida=payload.opcion_elegida,
            fue_segura=fue_segura,
            indicadores_detectados=[str(u) for u in payload.indicadores_detectados],
        )
        db.add(decision)
        if sesion.estado == EstadoSesion.INICIADA:
            sesion.estado = EstadoSesion.EN_DIA_TRIPLE
        db.commit()
        db.refresh(decision)
        return decision

    @staticmethod
    def registrar_reflexion(
        db: Session, sesion_id: UUID, payload: ReflexionCreate
    ) -> Reflexion:
        sesion = db.get(Sesion, sesion_id)
        if sesion is None:
            raise LookupError("sesion_no_encontrada")
        existente = db.execute(
            select(Reflexion).where(Reflexion.sesion_id == sesion_id)
        ).scalar_one_or_none()
        if existente is not None:
            raise ValueError("reflexion_ya_registrada")

        r = Reflexion(
            sesion_id=sesion_id,
            rol_mas_vulnerable=payload.rol_mas_vulnerable,
            eco_personal=payload.eco_personal,
            cambio_propuesto=payload.cambio_propuesto,
            nivel_confianza=payload.nivel_confianza,
        )
        db.add(r)
        sesion.estado = EstadoSesion.COMPLETADA
        sesion.completada_en = datetime.now(timezone.utc)
        db.commit()
        db.refresh(r)
        return r

    @staticmethod
    def progreso_usuario(db: Session, usuario_id: UUID) -> dict:
        """
        Resumen para el dashboard del usuario:
        cuántos Días Triples vivió, ganchos donde detectó mejor, etc.
        Tono coach, no inspector.
        """
        sesiones = list(
            db.execute(
                select(Sesion).where(Sesion.usuario_id == usuario_id)
            ).scalars()
        )
        completadas = [s for s in sesiones if s.estado == EstadoSesion.COMPLETADA]

        decisiones = list(
            db.execute(
                select(Decision).where(
                    Decision.sesion_id.in_([s.id for s in sesiones]) if sesiones else False
                )
            ).scalars()
        )

        por_rol = {r.value: {"total": 0, "seguras": 0} for r in Rol}
        for d in decisiones:
            rol_v = d.rol.value if hasattr(d.rol, "value") else str(d.rol)
            por_rol[rol_v]["total"] += 1
            if d.fue_segura:
                por_rol[rol_v]["seguras"] += 1

        return {
            "sesiones_iniciadas": len(sesiones),
            "sesiones_completadas": len(completadas),
            "decisiones_totales": len(decisiones),
            "decisiones_seguras": sum(1 for d in decisiones if d.fue_segura),
            "por_rol": por_rol,
        }
