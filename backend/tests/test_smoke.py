"""
Smoke tests del Bloque 1: la app importa, expone /health y /principios,
y los modelos/enums quedan registrados.
"""
import os

# Asegurar que la app no intente cargar un .env real durante tests.
os.environ.setdefault("ANTHROPIC_API_KEY", "")
os.environ.setdefault(
    "DATABASE_URL", "postgresql+psycopg://test:test@localhost:5432/test"
)

from fastapi.testclient import TestClient

from app.core.enums import GanchoPsicologico, NivelDificultad, Rol
from app.main import app

client = TestClient(app)


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_principios_publicados():
    r = client.get("/principios")
    assert r.status_code == 200
    body = r.json()
    assert body["max_dificultad"] == 3
    assert body["min_n_para_reporte_agregado"] >= 10
    # Al menos los 5 principios no negociables.
    assert len(body["principios"]) >= 5


def test_enums_cerrados_estan_registrados():
    # Garantía de que los enums cerrados existen y tienen los valores esperados.
    assert {r.value for r in Rol} == {"ciudadano", "colaborador", "cliente"}
    assert NivelDificultad.AVANZADO.value == 3
    assert "urgencia" in {g.value for g in GanchoPsicologico}


def test_modelos_orm_registrados():
    from app.core.database import Base

    tablas = set(Base.metadata.tables.keys())
    esperadas = {
        "organizaciones",
        "usuarios",
        "facilitadores",
        "personajes",
        "dias_triples",
        "actos",
        "indicadores",
        "sesiones",
        "decisiones",
        "reflexiones",
        "safety_logs",
    }
    assert esperadas.issubset(tablas), f"Faltan tablas: {esperadas - tablas}"
