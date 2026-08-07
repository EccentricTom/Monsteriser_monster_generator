"""Test D&D 5E 2024 defensive health calculations."""

import pytest
from pytest import raises

from monsteriser_monster_generator.systems.dnd5e.calculations.defensive_health import (
    DefensiveHealthResult,
    calculate_effective_hit_points,
)
from monsteriser_monster_generator.systems.dnd5e.models.base_monster import (
    BaseMonster,
)


def test_calculate_effective_hit_points_without_multiplier() -> None:
    """Return base HP when no defensive multiplier applies."""
    monster = BaseMonster(
        name="Test Monster",
        hitpoints=40,
    )

    result = calculate_effective_hit_points(
        monster=monster,
    )

    assert result == DefensiveHealthResult(
        base_hit_points=40,
        hit_point_multiplier=1.0,
        effective_hit_points=40.0,
    )


def test_calculate_effective_hit_points_applies_multiplier() -> None:
    """Apply the supplied defensive HP multiplier."""
    monster = BaseMonster(
        name="Test Monster",
        hitpoints=40,
    )

    result = calculate_effective_hit_points(
        monster=monster,
        hit_point_multiplier=1.5,
    )

    assert result == DefensiveHealthResult(
        base_hit_points=40,
        hit_point_multiplier=1.5,
        effective_hit_points=60.0,
    )


def test_calculate_effective_hit_points_accepts_fractional_result() -> None:
    """Preserve fractional effective hit points."""
    monster = BaseMonster(
        name="Test Monster",
        hitpoints=35,
    )

    result = calculate_effective_hit_points(
        monster=monster,
        hit_point_multiplier=1.5,
    )

    assert result.effective_hit_points == 52.5


def test_calculate_effective_hit_points_rejects_zero_multiplier() -> None:
    """Reject a zero hit-point multiplier."""
    monster = BaseMonster(
        name="Test Monster",
        hitpoints=40,
    )

    with raises(
        ValueError,
        match="Hit-point multiplier must be positive",
    ):
        calculate_effective_hit_points(
            monster=monster,
            hit_point_multiplier=0.0,
        )


@pytest.mark.parametrize(
    "hitpoints",
    [0, -2],
)
def test_calculate_effective_hit_points_rejects_non_positive_hit_points(hitpoints: int) -> None:
    """Reject a monster with non-positive points"""
    monster = BaseMonster(
        name="Test Monster",
        hitpoints=hitpoints,
    )

    with raises(ValueError, match="Monster hit points must be positive"):
        calculate_effective_hit_points(monster=monster)


@pytest.mark.parametrize(
    "multiplier",
    [
        0.0,
        -1.0,
        -0.5,
    ],
)
def test_calculate_effective_hit_points_rejects_invalid_multiplier(
    multiplier: float,
) -> None:
    """Reject non-positive hit-point multipliers."""
    monster = BaseMonster(
        name="Test Monster",
        hitpoints=40,
    )

    with raises(
        ValueError,
        match="Hit-point multiplier must be positive",
    ):
        calculate_effective_hit_points(
            monster=monster,
            hit_point_multiplier=multiplier,
        )
