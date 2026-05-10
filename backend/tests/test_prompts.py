"""
Tests de los prompts del sistema. No llaman al modelo.
Validan que los prompts contengan las restricciones no negociables y
que produzcan estructuras de salida bien formadas.
"""
from __future__ import annotations

from app.core.enums import Arquetipo, GanchoPsicologico, NivelDificultad
from app.prompts import (
    PROMPT_VERSIONS,
    dia_triple_writer,
    disector,
    personaje_builder,
    safety_filter_llm,
)


def test_versiones_publicadas():
    assert set(PROMPT_VERSIONS.keys()) == {
        "personaje_builder",
        "dia_triple_writer",
        "disector",
        "safety_filter_llm",
    }
    for v in PROMPT_VERSIONS.values():
        assert v.count(".") == 2  # semver simple


def test_personaje_builder_incluye_principios_y_catalogo():
    sysp = personaje_builder.SYSTEM_PROMPT
    user = personaje_builder.build_user_prompt(
        Arquetipo.GUARDIAN_FINANCIERO,
        NivelDificultad.INTERMEDIO,
        semilla_narrativa="vive en una ciudad costera ficticia",
    )
    # Principios no negociables
    for marker in ["NUNCA atacar", "catálogo cerrado", "techo absoluto"]:
        assert marker.lower() in (sysp + user).lower()
    # Una marca ficticia conocida del catálogo aparece en el render del user prompt.
    assert "banco-ribera-sur" in user
    assert "GUARDIAN_FINANCIERO".lower() in user.lower() or "guardian_financiero" in user


def test_dia_triple_writer_describe_los_tres_actos():
    sysp = dia_triple_writer.SYSTEM_PROMPT
    user = dia_triple_writer.build_user_prompt(
        personaje={"nombre": "Carla Núñez", "edad": 38, "arquetipo": "guardian_financiero"},
        gancho=GanchoPsicologico.URGENCIA,
        nivel=NivelDificultad.INTERMEDIO,
    )
    for marker in ["ACTO 1", "ACTO 2", "ACTO 3", "07:30", "11:00", "19:00"]:
        assert marker in sysp
    assert "urgencia" in user
    assert "Carla N" in user
    assert "techo absoluto" in user


def test_disector_indicadores_catalogo_cerrado():
    sysp = disector.SYSTEM_PROMPT
    for tipo in [
        "dominio_sospechoso",
        "urgencia_artificial",
        "llamado_accion_unico",
        "autoridad_no_verificable",
        "incongruencia_canal",
    ]:
        assert tipo in sysp


def test_safety_filter_llm_categorias_canonicas():
    sysp = safety_filter_llm.SYSTEM_PROMPT
    for cat in [
        "marca_real_detectada",
        "marca_real_disfrazada",
        "tema_linea_roja",
        "osint_usuario_real",
        "dificultad_excedida",
        "marca_ficticia_no_catalogada",
    ]:
        assert cat in sysp


def test_user_prompts_renderizan_catalogo_completo():
    """Cualquier user prompt que use render_catalogo_marcas debe listar las 30."""
    user_p = personaje_builder.build_user_prompt(
        Arquetipo.OPERADOR_CONFIANZA, NivelDificultad.INTRODUCTORIO
    )
    # 4 columnas separadas por 3 pipes, x (1 cabecera + 30 entradas) = 93
    assert user_p.count("|") >= 30 * 3
