"""
Reportes agregados al facilitador. Política: nunca individuales.
Mínimo MIN_AGGREGATE_N respuestas para mostrar cualquier métrica.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.enums import EstadoSesion, Rol
from app.models.sesion import Decision, Reflexion, Sesion
from app.models.usuario import Usuario

router = APIRouter(prefix="/reportes", tags=["reportes"])


@router.get("/organizacion/{organizacion_id}/agregado")
def reporte_agregado(organizacion_id: UUID, db: Session = Depends(get_db)):
    settings = get_settings()
    minimo_n = settings.min_aggregate_n

    usuarios = list(
        db.execute(
            select(Usuario.id).where(Usuario.organizacion_id == organizacion_id)
        ).scalars()
    )
    if not usuarios:
        return _respuesta_insuficiente(minimo_n, 0)

    sesiones = list(
        db.execute(
            select(Sesion).where(Sesion.usuario_id.in_(usuarios))
        ).scalars()
    )
    sesiones_completadas = [s for s in sesiones if s.estado == EstadoSesion.COMPLETADA]

    if len(sesiones_completadas) < minimo_n:
        return _respuesta_insuficiente(minimo_n, len(sesiones_completadas))

    decisiones = list(
        db.execute(
            select(Decision).where(
                Decision.sesion_id.in_([s.id for s in sesiones])
            )
        ).scalars()
    )

    por_rol = {r.value: {"total": 0, "seguras": 0} for r in Rol}
    for d in decisiones:
        rol_v = d.rol.value if hasattr(d.rol, "value") else str(d.rol)
        por_rol[rol_v]["total"] += 1
        if d.fue_segura:
            por_rol[rol_v]["seguras"] += 1

    reflexiones = list(
        db.execute(
            select(Reflexion).where(
                Reflexion.sesion_id.in_([s.id for s in sesiones])
            )
        ).scalars()
    )

    return {
        "n_usuarios_con_sesion_completada": len(
            {s.usuario_id for s in sesiones_completadas}
        ),
        "n_sesiones_completadas": len(sesiones_completadas),
        "tasa_decisiones_seguras_global": round(
            sum(1 for d in decisiones if d.fue_segura) / max(len(decisiones), 1), 3
        ),
        "tasa_decisiones_seguras_por_rol": {
            rol: round(stats["seguras"] / max(stats["total"], 1), 3)
            for rol, stats in por_rol.items()
        },
        "n_reflexiones": len(reflexiones),
        "advertencia": (
            "Reporte agregado. No incluye datos individualizables. "
            f"Política: mínimo {minimo_n} usuarios con sesión completada."
        ),
    }


def _respuesta_insuficiente(minimo_n: int, n_actual: int) -> dict:
    return {
        "n_actual": n_actual,
        "minimo_requerido": minimo_n,
        "mensaje": (
            "n insuficiente para preservar anonimato. "
            f"Se requieren al menos {minimo_n} usuarios con sesión completada."
        ),
    }
