"""
Tests de endpoints. Usan SQLite en memoria como DB.

Cada test recibe un cliente con DB limpia, y validamos:
- /marcas devuelve el catálogo cerrado.
- POST /personajes acepta payloads válidos y rechaza marcas no catalogadas.
- POST /dias-triples invoca el safety_filter y bloquea marca real.
- Flujo de sesión: crear, decisión, reflexión, progreso.
- Reporte agregado respeta el mínimo n.
"""
from __future__ import annotations

import os
from uuid import uuid4

# DB en memoria por proceso de test, definida ANTES de importar la app.
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["ENVIRONMENT"] = "test"
os.environ["MIN_AGGREGATE_N"] = "2"  # más manejable para tests

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool

from app.core import database as db_module
from app.core.database import Base, GUID
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Reemplazar engine y SessionLocal por uno con pool estático (necesario para
# que TODOS los hilos compartan la misma DB en memoria).
TEST_ENGINE = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
db_module.engine = TEST_ENGINE
db_module.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)

# Importar la app después de re-bindear el engine.
from app.main import app  # noqa: E402

Base.metadata.create_all(bind=TEST_ENGINE)


@pytest.fixture(autouse=True)
def _limpiar_tablas():
    """Vacía todas las tablas entre tests para aislamiento."""
    yield
    with TEST_ENGINE.begin() as conn:
        for tabla in reversed(Base.metadata.sorted_tables):
            conn.execute(tabla.delete())


@pytest.fixture
def client():
    return TestClient(app)


# ===== /marcas =====


def test_listar_marcas(client):
    r = client.get("/marcas")
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 30
    assert any(m["slug"] == "banco-ribera-sur" for m in data)


# ===== /personajes =====


def _payload_personaje(**overrides) -> dict:
    base = {
        "nombre": "Carla Núñez",
        "edad": 38,
        "arquetipo": "guardian_financiero",
        "nivel_sugerido": 2,
        "cargo_ficticio": "Jefa de cuentas",
        "empresa_ficticia": "NexoFin Servicios",
        "contexto_familiar": "Vive con su pareja y un perro adoptado.",
        "habitos_consumo": "Compra electrodomésticos en Tienda Cronos.",
        "vector_exposicion": {
            "redes": ["publica reseñas en MercadoFácil"],
            "rutinas": ["yoga los sábados 8am"],
            "consumos": ["StreamColibrí cada noche"],
        },
        "marcas_asociadas": ["banco-ribera-sur", "nexofin-servicios", "streamcolibri"],
        "es_semilla": True,
    }
    base.update(overrides)
    return base


def test_crear_personaje_ok(client):
    r = client.post("/personajes", json=_payload_personaje())
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["nombre"] == "Carla Núñez"
    assert body["disclaimer_visible"] is True


def test_crear_personaje_rechaza_marca_no_catalogada(client):
    r = client.post(
        "/personajes",
        json=_payload_personaje(marcas_asociadas=["marca-inventada-no-existe"]),
    )
    assert r.status_code == 400


def test_listar_personajes_con_filtros(client):
    client.post("/personajes", json=_payload_personaje())
    client.post(
        "/personajes",
        json=_payload_personaje(nombre="Diego Salas", arquetipo="operador_confianza"),
    )

    r = client.get("/personajes")
    assert r.status_code == 200
    assert len(r.json()) == 2

    r = client.get("/personajes", params={"arquetipo": "operador_confianza"})
    assert len(r.json()) == 1


# ===== /dias-triples =====


def _payload_dia_triple(personaje_id: str) -> dict:
    base_indicadores = [
        {
            "tipo": "urgencia_artificial",
            "fragmento": "en las próximas 2 horas",
            "explicacion": "La urgencia inventada empuja a actuar sin verificar.",
        },
        {
            "tipo": "dominio_sospechoso",
            "fragmento": "bancoriberasur-seguro.example",
            "explicacion": "Sufijo extraño agregado al dominio de la marca ficticia.",
        },
        {
            "tipo": "llamado_accion_unico",
            "fragmento": "haga clic aquí",
            "explicacion": "Único botón visible, sin canal alterno de validación.",
        },
    ]
    return {
        "personaje_id": personaje_id,
        "titulo": "Día Triple del gancho de urgencia",
        "gancho_psicologico_raiz": "urgencia",
        "nivel_dificultad": 2,
        "nota_revelacion": (
            "Los tres mensajes usaron urgencia artificial. Cambió el canal, no la trampa."
        ),
        "actos": [
            {
                "orden": 1,
                "rol": "ciudadano",
                "canal": "sms",
                "hora_dramatizada": "07:30",
                "remitente_aparente": "Equipo Banco Ribera Sur",
                "asunto": None,
                "cuerpo": (
                    "Su cuenta fue bloqueada. Acceda en las próximas 2 horas en "
                    "bancoriberasur-seguro.example y haga clic aquí."
                ),
                "marca_ficticia_slug": "banco-ribera-sur",
                "opciones_decision": [
                    {"id": "a", "texto": "Hacer clic", "consecuencia": "Cae", "es_segura": False},
                    {"id": "b", "texto": "Llamar al banco", "consecuencia": "Detecta", "es_segura": True},
                    {"id": "c", "texto": "Ignorar", "consecuencia": "Neutro", "es_segura": True},
                ],
                "indicadores": base_indicadores,
            },
            {
                "orden": 2,
                "rol": "colaborador",
                "canal": "correo",
                "hora_dramatizada": "11:00",
                "remitente_aparente": "Recursos Humanos NexoFin",
                "asunto": "Verificación urgente de cuenta",
                "cuerpo": (
                    "Verifique sus credenciales en las próximas 2 horas en "
                    "nexofin-rrhh.example o haga clic aquí."
                ),
                "marca_ficticia_slug": "nexofin-servicios",
                "opciones_decision": [
                    {"id": "a", "texto": "Responder con credenciales", "consecuencia": "Cae", "es_segura": False},
                    {"id": "b", "texto": "Verificar con TI", "consecuencia": "Detecta", "es_segura": True},
                    {"id": "c", "texto": "Ignorar", "consecuencia": "Neutro", "es_segura": True},
                ],
                "indicadores": [
                    {
                        "tipo": "urgencia_artificial",
                        "fragmento": "en las próximas 2 horas",
                        "explicacion": "Mismo patrón que el SMS de la mañana.",
                    },
                    {
                        "tipo": "remitente_anomalo",
                        "fragmento": "nexofin-rrhh.example",
                        "explicacion": "Subdominio inusual para RR.HH.",
                    },
                    {
                        "tipo": "llamado_accion_unico",
                        "fragmento": "haga clic aquí",
                        "explicacion": "Único botón sin canal alternativo de validación.",
                    },
                ],
            },
            {
                "orden": 3,
                "rol": "cliente",
                "canal": "whatsapp",
                "hora_dramatizada": "19:00",
                "remitente_aparente": "StreamColibrí",
                "asunto": None,
                "cuerpo": (
                    "Su suscripción vence en las próximas 2 horas. Renueve aquí: "
                    "streamcolibri-renovar.example y haga clic aquí."
                ),
                "marca_ficticia_slug": "streamcolibri",
                "opciones_decision": [
                    {"id": "a", "texto": "Pagar inmediatamente", "consecuencia": "Cae", "es_segura": False},
                    {"id": "b", "texto": "Abrir la app oficial", "consecuencia": "Detecta", "es_segura": True},
                    {"id": "c", "texto": "Ignorar", "consecuencia": "Neutro", "es_segura": True},
                ],
                "indicadores": base_indicadores,
            },
        ],
    }


def _crear_personaje(client) -> str:
    r = client.post("/personajes", json=_payload_personaje())
    assert r.status_code == 201, r.text
    return r.json()["id"]


def test_crear_dia_triple_ok(client):
    pid = _crear_personaje(client)
    r = client.post("/dias-triples", json=_payload_dia_triple(pid))
    assert r.status_code == 201, r.text
    dt = r.json()
    assert len(dt["actos"]) == 3
    roles = {a["rol"] for a in dt["actos"]}
    assert roles == {"ciudadano", "colaborador", "cliente"}


def test_crear_dia_triple_rechaza_marca_real_en_cuerpo(client):
    pid = _crear_personaje(client)
    payload = _payload_dia_triple(pid)
    payload["actos"][0]["cuerpo"] = (
        "Estimado cliente de Banco Pichincha, su cuenta fue bloqueada en las próximas 2 horas."
    )
    r = client.post("/dias-triples", json=payload)
    assert r.status_code == 422
    detail = r.json()["detail"]
    assert detail["motivo"] == "marca_real_detectada"


def test_crear_dia_triple_rechaza_dificultad_excedida(client):
    pid = _crear_personaje(client)
    payload = _payload_dia_triple(pid)
    # El validador Pydantic rechaza primero (NivelDificultad solo admite 1-3),
    # asegurando defensa en profundidad.
    payload["nivel_dificultad"] = 4
    r = client.post("/dias-triples", json=payload)
    assert r.status_code == 422


# ===== /sesiones =====


def _crear_org_y_usuario(client) -> tuple[str, str]:
    r = client.post(
        "/organizaciones", json={"nombre": "Org Demo", "slug": "org-demo", "sector": "fintech"}
    )
    assert r.status_code == 201, r.text
    org_id = r.json()["id"]
    r = client.post(
        "/usuarios",
        json={"organizacion_id": org_id, "identificador_externo": "anon-001", "area": "operaciones"},
    )
    assert r.status_code == 201, r.text
    return org_id, r.json()["id"]


def _crear_dt_y_personaje(client) -> tuple[str, str, list[dict]]:
    pid = _crear_personaje(client)
    r = client.post("/dias-triples", json=_payload_dia_triple(pid))
    return pid, r.json()["id"], r.json()["actos"]


def test_flujo_sesion_decisiones_y_reflexion(client):
    _, uid = _crear_org_y_usuario(client)
    pid, dtid, actos = _crear_dt_y_personaje(client)

    r = client.post(
        "/sesiones",
        json={"usuario_id": uid, "personaje_id": pid, "dia_triple_id": dtid},
    )
    assert r.status_code == 201, r.text
    sid = r.json()["id"]

    # Decisión por cada acto: dos seguras, una insegura.
    elecciones = [("a", False), ("b", True), ("b", True)]
    for acto, (eleccion, esperada_segura) in zip(actos, elecciones):
        rd = client.post(
            f"/sesiones/{sid}/decisiones",
            json={
                "acto_id": acto["id"],
                "rol": acto["rol"],
                "opcion_elegida": eleccion,
                "indicadores_detectados": [],
            },
        )
        assert rd.status_code == 201, rd.text
        assert rd.json()["fue_segura"] is esperada_segura

    rr = client.post(
        f"/sesiones/{sid}/reflexion",
        json={
            "rol_mas_vulnerable": "ciudadano",
            "eco_personal": "Reconozco la urgencia que me empuja a actuar sin pensar.",
            "cambio_propuesto": "Voy a verificar por canal alterno antes de hacer clic.",
            "nivel_confianza": 4,
        },
    )
    assert rr.status_code == 201, rr.text

    # Reflexión duplicada: rechazo
    rr2 = client.post(
        f"/sesiones/{sid}/reflexion",
        json={"nivel_confianza": 5},
    )
    assert rr2.status_code == 400

    rp = client.get(f"/sesiones/usuario/{uid}/progreso")
    assert rp.status_code == 200
    body = rp.json()
    assert body["sesiones_iniciadas"] == 1
    assert body["sesiones_completadas"] == 1
    assert body["decisiones_totales"] == 3
    assert body["decisiones_seguras"] == 2


def test_decision_con_opcion_invalida_rechazada(client):
    _, uid = _crear_org_y_usuario(client)
    pid, dtid, actos = _crear_dt_y_personaje(client)
    sid = client.post(
        "/sesiones", json={"usuario_id": uid, "personaje_id": pid, "dia_triple_id": dtid}
    ).json()["id"]
    r = client.post(
        f"/sesiones/{sid}/decisiones",
        json={
            "acto_id": actos[0]["id"],
            "rol": actos[0]["rol"],
            "opcion_elegida": "z",
            "indicadores_detectados": [],
        },
    )
    assert r.status_code == 422  # Pydantic regex falla (a-d)


# ===== /reportes =====


def test_reporte_agregado_respeta_n_minimo(client):
    org_id, _ = _crear_org_y_usuario(client)
    r = client.get(f"/reportes/organizacion/{org_id}/agregado")
    assert r.status_code == 200
    body = r.json()
    assert "minimo_requerido" in body
    assert body["n_actual"] == 0
