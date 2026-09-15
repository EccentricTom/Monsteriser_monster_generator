"""Test calculations for Regeneration for monsters in D&D 5E 2024."""

from pytest import raises

from monsteriser_monster_generator.systems.dnd5e.calculations.defensive.regeneration import (
    RegenerationAdjustmentResult,
    calculate_regeneration_effective_hit_points,
)
from monsteriser_monster_generator.systems.dnd5e.models.base_monster import BaseMonster
from monsteriser_monster_generator.systems.dnd5e.models.traits import RegenerationTrait


def test_calculate_regeneration_effective_hit_points() -> None:
    """Calculate effective HP gained from regeneration."""
    monster = BaseMonster(
        name="Troll",
        traits=[
            RegenerationTrait(
                hit_points_per_round=10,
            )
        ],
    )

    result = calculate_regeneration_effective_hit_points(
        monster=monster,
        rounds=3,
    )

    assert result == RegenerationAdjustmentResult(
        hit_points_per_round=10,
        rounds=3,
        effective_hit_points=30,
    )


def test_calculate_regeneration_effective_hit_points_returns_none_without_regeneration() -> None:
    """Return no adjustment when the monster has no regeneration."""
    monster = BaseMonster(
        name="Wolf",
    )

    result = calculate_regeneration_effective_hit_points(
        monster=monster,
    )

    assert result is None


def test_calculate_regeneration_effective_hit_points_rejects_non_positive_rounds() -> None:
    """Reject invalid regeneration evaluation windows."""
    monster = BaseMonster(
        name="Troll",
        traits=[
            RegenerationTrait(
                hit_points_per_round=10,
            )
        ],
    )

    with raises(
        ValueError,
        match="Rounds must be positive",
    ):
        calculate_regeneration_effective_hit_points(
            monster=monster,
            rounds=0,
        )


def test_calculate_regeneration_effective_hit_points_rejects_multiple_regeneration_traits() -> None:
    """Reject monsters with multiple regeneration traits."""
    monster = BaseMonster(
        name="Troll",
        traits=[
            RegenerationTrait(
                hit_points_per_round=10,
            ),
            RegenerationTrait(
                hit_points_per_round=5,
            ),
        ],
    )

    with raises(
        ValueError,
        match="Monster cannot have multiple regeneration traits",
    ):
        calculate_regeneration_effective_hit_points(
            monster=monster,
        )
