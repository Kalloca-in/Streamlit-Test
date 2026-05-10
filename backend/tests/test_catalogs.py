"""Validate the JSON catalogs ship coherent, complete data."""

from __future__ import annotations

from app.data_catalogs import (
    attacker_catalog,
    attacker_objectives,
    fictitious_brands,
    organizational_controls,
    universal_characters,
)
from app.models.attacker import AttackerArchetype, AttackerObjective


def test_six_attacker_archetypes_present():
    catalog = attacker_catalog()
    assert set(catalog.keys()) == set(AttackerArchetype)
    for code, card in catalog.items():
        assert card.code == code
        assert card.display_name
        assert card.sample_opening
        assert card.psychological_profile


def test_four_attacker_objectives_present():
    catalog = attacker_objectives()
    assert set(catalog.keys()) == set(AttackerObjective)


def test_universal_characters_count():
    chars = universal_characters()
    assert 6 <= len(chars) <= 8
    for code, card in chars.items():
        assert card.code == code
        assert card.role_title
        assert card.fictional_company is None or "ficticia" in card.fictional_company.lower()


def test_fictitious_brands_min_30():
    brands = fictitious_brands()
    assert len(brands) >= 30, f"Need >=30 fictitious brands, found {len(brands)}"
    for b in brands:
        assert b["domain"].endswith((".example", ".test"))


def test_organizational_controls_present():
    controls = organizational_controls()
    assert len(controls) >= 5
    required_keys = {"code", "display_name", "description", "when_to_apply", "expected_outcome"}
    for c in controls:
        assert required_keys.issubset(c.keys())


def test_no_real_brand_leaked_in_catalog_descriptions():
    """The fictitious brand catalog must not name real brands."""
    from app.services.safety_filter import filter_attacker_message

    for b in fictitious_brands():
        result = filter_attacker_message(f"Marca: {b['display_name']}")
        assert not result.intercepted, (
            f"Catalog brand '{b['display_name']}' triggered safety filter"
        )
