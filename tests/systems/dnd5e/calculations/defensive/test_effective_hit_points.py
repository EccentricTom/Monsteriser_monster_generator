"""Test D&D 5E 2024 defensive health calculations."""

import pytest
from pytest import raises

from monsteriser_monster_generator.systems.dnd5e.calculations.defensive.effective_health import (
    DefensiveHealthResult,
    calculate_effective_hit_points,
)
from monsteriser_monster_generator.systems.dnd5e.models.base_monster import (
    BaseMonster,
)
from monsteriser_monster_generator.systems.dnd5e.models.damage_adjustments import (
    Immunity,
    Resistance,
    Vulnerability,
)


def test_calculate_effective_hit_points_without_adjustments() -> None:
    """Return base HP when no damage adjustments apply."""
    monster = BaseMonster(
        name="Test Monster",
        hitpoints=40,
        expected_cr=5,
    )

    result = calculate_effective_hit_points(
        monster=monster,
    )

    assert result == DefensiveHealthResult(
        base_hit_points=40,
        hit_point_multiplier=1.0,
        effective_hit_points=40.0,
    )


def test_calculate_effective_hit_points_applies_resistance_multiplier() -> None:
    """Apply qualifying resistance to effective hit points."""
    monster = BaseMonster(
        name="Test Monster",
        hitpoints=40,
        expected_cr=5,
        resistances=[
            Resistance(damage_type="fire"),
            Resistance(damage_type="cold"),
            Resistance(damage_type="lightning"),
        ],
    )

    result = calculate_effective_hit_points(
        monster=monster,
    )

    assert result == DefensiveHealthResult(
        base_hit_points=40,
        hit_point_multiplier=1.5,
        effective_hit_points=60.0,
    )


def test_calculate_effective_hit_points_applies_immunity_multiplier() -> None:
    """Apply qualifying immunity to effective hit points."""
    monster = BaseMonster(
        name="Test Monster",
        hitpoints=40,
        expected_cr=5,
        immunities=[
            Immunity(damage_type="fire"),
            Immunity(damage_type="cold"),
            Immunity(damage_type="lightning"),
        ],
    )

    result = calculate_effective_hit_points(
        monster=monster,
    )

    assert result == DefensiveHealthResult(
        base_hit_points=40,
        hit_point_multiplier=2.0,
        effective_hit_points=80.0,
    )


def test_calculate_effective_hit_points_applies_vulnerability_multiplier() -> None:
    """Apply qualifying vulnerability to effective hit points."""
    monster = BaseMonster(
        name="Test Monster",
        hitpoints=40,
        expected_cr=5,
        vulnerabilities=[
            Vulnerability(damage_type="fire"),
            Vulnerability(damage_type="cold"),
            Vulnerability(damage_type="radiant"),
        ],
    )

    result = calculate_effective_hit_points(
        monster=monster,
    )

    assert result == DefensiveHealthResult(
        base_hit_points=40,
        hit_point_multiplier=0.5,
        effective_hit_points=20.0,
    )


def test_calculate_effective_hit_points_uses_immunity_over_resistance() -> None:
    """Use immunity rather than stacking qualifying defensive adjustments."""
    monster = BaseMonster(
        name="Test Monster",
        hitpoints=40,
        expected_cr=5,
        resistances=[
            Resistance(damage_type="fire"),
            Resistance(damage_type="cold"),
            Resistance(damage_type="lightning"),
        ],
        immunities=[
            Immunity(damage_type="poison"),
            Immunity(damage_type="psychic"),
            Immunity(damage_type="necrotic"),
        ],
    )

    result = calculate_effective_hit_points(
        monster=monster,
    )

    assert result.hit_point_multiplier == 2.0
    assert result.effective_hit_points == 80.0


@pytest.mark.parametrize(
    "hitpoints",
    [0, -2],
)
def test_calculate_effective_hit_points_rejects_non_positive_hit_points(hitpoints: int) -> None:
    """Reject a monster with non-positive points."""
    monster = BaseMonster(
        name="Test Monster",
        hitpoints=hitpoints,
    )

    with raises(ValueError, match="Monster hit points must be positive"):
        calculate_effective_hit_points(monster=monster)
