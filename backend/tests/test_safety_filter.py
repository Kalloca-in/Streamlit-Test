"""
Tests del safety_filter.

Garantía estructural: ningún Día Triple con marca real, OSINT del usuario,
dificultad excedida o tema de línea roja puede atravesar el sistema.
"""
from __future__ import annotations

from uuid import uuid4

import pytest

from app.core.enums import (
    CanalAtaque,
    GanchoPsicologico,
    NivelDificultad,
    Rol,
    TipoIndicador,
)
from app.schemas.dia_triple import (
    ActoBase,
    DiaTripleCreate,
    IndicadorBase,
    OpcionDecision,
)
from app.services.safety_filter import (
    MOTIVO_DIFICULTAD_EXCEDIDA,
    MOTIVO_MARCA_NO_CATALOGADA,
    MOTIVO_MARCA_REAL,
    MOTIVO_OSINT_USUARIO,
    MOTIVO_RED_LINE,
    SafetyFilter,
    SafetyViolation,
    safety_pre_call_filter,
    validate_dia_triple_safe,
)


# ============================================================
# Reglas pre-generación: scan_text contra blocklist
# ============================================================


@pytest.mark.parametrize(
    "frase",
    [
        "El cliente recibió un correo de Banco Pichincha",
        "Notificación de Mercado Libre sobre devolución",
        "Genera un correo de Netflix sobre suscripción",
        "Pretexto de Uber Eats con cobro duplicado",
        "Mensaje del SRI con multa pendiente",
        "Estado de cuenta de PayPal",
        "Comunicado del IESS sobre afiliación",
        "Correo de Microsoft Teams para reunión urgente",
    ],
)
def test_scan_text_bloquea_marcas_reales(frase):
    """
    Cualquier marca real basta para disparar el bloqueo.
    No fijamos qué etiqueta se devuelve: si la frase contiene varias,
    el motor reporta la más larga, lo cual es deliberado.
    """
    with pytest.raises(SafetyViolation) as exc:
        SafetyFilter.scan_text(frase, contexto="test")
    assert exc.value.motivo == MOTIVO_MARCA_REAL


@pytest.mark.parametrize(
    "frase",
    [
        "El personaje Carla recibe un SMS de Banco Ribera Sur",
        "Notificación de StreamColibrí sobre suscripción",
        "Correo de NexoFin Servicios al gerente",
        "Mensaje de RápidoYa diciendo que el pedido se canceló",
    ],
)
def test_scan_text_permite_marcas_ficticias(frase):
    SafetyFilter.scan_text(frase, contexto="test")  # no levanta


def test_scan_text_bloquea_red_line_ninos():
    with pytest.raises(SafetyViolation) as exc:
        SafetyFilter.scan_text(
            "El personaje tiene un hijo con cancer terminal",
            contexto="test",
        )
    assert exc.value.motivo == MOTIVO_RED_LINE


def test_scan_text_bloquea_osint_usuario():
    with pytest.raises(SafetyViolation) as exc:
        SafetyFilter.scan_text(
            "Por favor extrae datos personales del usuario para personalizar el ataque",
            contexto="test",
        )
    assert exc.value.motivo == MOTIVO_OSINT_USUARIO


def test_scan_text_es_case_insensitive_y_tolera_tildes():
    with pytest.raises(SafetyViolation):
        SafetyFilter.scan_text("BANCO PICHINCHA es la entidad", contexto="test")
    with pytest.raises(SafetyViolation):
        SafetyFilter.scan_text("Mensaje del IESS", contexto="test")
    with pytest.raises(SafetyViolation):
        SafetyFilter.scan_text("Vista de la Función Judicial", contexto="test")


def test_pre_call_filter_es_alias_de_scan_text():
    with pytest.raises(SafetyViolation):
        safety_pre_call_filter("Genera un correo del Banco Bolivariano", "anthropic_call")


def test_assert_difficulty_bloquea_nivel_4():
    with pytest.raises(SafetyViolation) as exc:
        SafetyFilter.assert_difficulty(4, contexto="test")
    assert exc.value.motivo == MOTIVO_DIFICULTAD_EXCEDIDA


def test_assert_difficulty_permite_nivel_3():
    SafetyFilter.assert_difficulty(3, contexto="test")  # no levanta


# ============================================================
# Validación post-generación de DiaTripleCreate
# ============================================================


def _opciones_validas() -> list[OpcionDecision]:
    return [
        OpcionDecision(id="a", texto="Hacer clic", consecuencia="Cae", es_segura=False),
        OpcionDecision(id="b", texto="Verificar canal", consecuencia="Detecta", es_segura=True),
        OpcionDecision(id="c", texto="Ignorar", consecuencia="Neutro", es_segura=True),
    ]


def _indicadores_validos() -> list[IndicadorBase]:
    return [
        IndicadorBase(
            tipo=TipoIndicador.URGENCIA_ARTIFICIAL,
            fragmento="en las próximas 2 horas",
            explicacion="La urgencia inventada empuja a actuar sin verificar.",
        ),
        IndicadorBase(
            tipo=TipoIndicador.DOMINIO_SOSPECHOSO,
            fragmento="bancopacificosur-seguro.example",
            explicacion="Sufijo agregado al dominio legítimo del banco ficticio.",
        ),
        IndicadorBase(
            tipo=TipoIndicador.LLAMADO_ACCION_UNICO,
            fragmento="haga clic aquí",
            explicacion="Un solo botón, sin opción de validar por canal alterno.",
        ),
    ]


def _acto(rol: Rol, orden: int, marca_slug: str | None, *, cuerpo: str | None = None) -> ActoBase:
    canal = {
        Rol.CIUDADANO: CanalAtaque.SMS,
        Rol.COLABORADOR: CanalAtaque.CORREO,
        Rol.CLIENTE: CanalAtaque.WHATSAPP,
    }[rol]
    return ActoBase(
        orden=orden,
        rol=rol,
        canal=canal,
        hora_dramatizada="07:30",
        remitente_aparente="Equipo de Seguridad",
        asunto="Verificación urgente",
        cuerpo=cuerpo or "Estimado cliente, su cuenta fue bloqueada. Verifique en las próximas 2 horas.",
        marca_ficticia_slug=marca_slug,
        opciones_decision=_opciones_validas(),
        indicadores=_indicadores_validos(),
    )


def _dia_triple_valido(marca_slug: str = "banco-ribera-sur") -> DiaTripleCreate:
    return DiaTripleCreate(
        personaje_id=uuid4(),
        titulo="Día triple del gancho de urgencia",
        gancho_psicologico_raiz=GanchoPsicologico.URGENCIA,
        nivel_dificultad=NivelDificultad.INTERMEDIO,
        nota_revelacion=(
            "Los tres mensajes usaron urgencia artificial. Cambió el canal, no la trampa."
        ),
        actos=[
            _acto(Rol.CIUDADANO, 1, marca_slug),
            _acto(Rol.COLABORADOR, 2, "nexofin-servicios"),
            _acto(Rol.CLIENTE, 3, "streamcolibri"),
        ],
    )


def test_validate_dia_triple_acepta_caso_legitimo():
    dt = _dia_triple_valido()
    validate_dia_triple_safe(dt, contexto="test")  # no levanta


def test_validate_dia_triple_rechaza_marca_real_en_cuerpo():
    dt = _dia_triple_valido()
    dt.actos[0] = _acto(
        Rol.CIUDADANO,
        1,
        "banco-ribera-sur",
        cuerpo="Estimado cliente de Banco Pichincha, su cuenta fue bloqueada.",
    )
    with pytest.raises(SafetyViolation) as exc:
        validate_dia_triple_safe(dt, contexto="test")
    assert exc.value.motivo == MOTIVO_MARCA_REAL


def test_validate_dia_triple_rechaza_marca_real_en_remitente():
    dt = _dia_triple_valido()
    dt.actos[1].remitente_aparente = "Recursos Humanos · Mercado Libre"
    with pytest.raises(SafetyViolation) as exc:
        validate_dia_triple_safe(dt, contexto="test")
    assert exc.value.motivo == MOTIVO_MARCA_REAL


def test_validate_dia_triple_rechaza_slug_no_catalogado():
    dt = _dia_triple_valido(marca_slug="banco-no-existe-en-catalogo")
    with pytest.raises(SafetyViolation) as exc:
        validate_dia_triple_safe(dt, contexto="test")
    assert exc.value.motivo == MOTIVO_MARCA_NO_CATALOGADA


def test_validate_dia_triple_rechaza_red_line_en_nota_revelacion():
    dt = _dia_triple_valido()
    dt.nota_revelacion = (
        "Reflexión: el ataque jugaba con el miedo a un hijo con cancer terminal del personaje."
    )
    with pytest.raises(SafetyViolation) as exc:
        validate_dia_triple_safe(dt, contexto="test")
    assert exc.value.motivo == MOTIVO_RED_LINE
