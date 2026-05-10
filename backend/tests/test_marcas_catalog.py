"""
Tests del catálogo cerrado de marcas ficticias.

Garantizan que:
- El catálogo tiene >= 30 entradas.
- La distribución por sector cumple con los mínimos de la especificación.
- Los slugs son únicos.
- Los dominios usan TLDs reservados (.example, .test, .invalid).
- Ningún nombre del catálogo colisiona con la blocklist de marcas reales.
"""
from __future__ import annotations

from collections import Counter

import pytest

from app.services.marcas_catalog import cargar_catalogo
from app.services.safety_filter import catalogo_es_seguro_contra_blocklist


SAFE_TLDS = {"example", "test", "invalid", "localhost"}


@pytest.fixture(scope="module")
def catalogo():
    return cargar_catalogo()


def test_catalogo_minimo_30(catalogo):
    assert len(catalogo) >= 30, f"El catálogo tiene {len(catalogo)} entradas, mínimo 30"


def test_distribucion_minima_por_sector(catalogo):
    contador = Counter(m.sector for m in catalogo)
    minimos = {
        "banco": 5,
        "retail": 5,
        "utilities": 5,
        "educacion": 5,
        "empleador": 5,
        "streaming": 3,
        "delivery": 2,
    }
    for sector, minimo in minimos.items():
        assert contador[sector] >= minimo, (
            f"Sector '{sector}' tiene {contador[sector]} entradas, mínimo {minimo}"
        )


def test_slugs_unicos(catalogo):
    slugs = [m.slug for m in catalogo]
    duplicados = [s for s, n in Counter(slugs).items() if n > 1]
    assert not duplicados, f"Slugs duplicados: {duplicados}"


def test_dominios_usan_tld_reservado(catalogo):
    inválidos = []
    for m in catalogo:
        tld = m.dominio.rsplit(".", 1)[-1].lower()
        if tld not in SAFE_TLDS:
            inválidos.append((m.slug, m.dominio))
    assert not inválidos, (
        "Todas las entradas deben usar TLD reservado RFC 2606 "
        f"(.example/.test/.invalid). Violan: {inválidos}"
    )


def test_catalogo_no_colisiona_con_marcas_reales():
    """
    Self-check: ninguna entrada del catálogo ficticio activa la blocklist.
    Si alguna lo hace, hay que renombrar la marca ficticia.
    """
    ok, colisiones = catalogo_es_seguro_contra_blocklist()
    assert ok, f"Colisiones del catálogo con la blocklist: {colisiones}"


def test_nombres_no_vacios_y_descripcion_minima(catalogo):
    for m in catalogo:
        assert m.nombre.strip(), f"Nombre vacío en {m.slug}"
        assert len(m.descripcion) >= 20, f"Descripción demasiado corta en {m.slug}"
