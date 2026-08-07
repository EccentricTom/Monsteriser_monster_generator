"""Test simplified defensive CR calculations for D&D 5E 2024."""

import polars as pl
from pytest import raises

from monsteriser_monster_generator.systems.dnd5e.calculations.defensive.defensive_cr import (
    DefensiveChallengeRatingResult,
    calculate_monster_defensive_cr,
)
from monsteriser_monster_generator.systems.dnd5e.calculations.defensive.effective_health import (
    DefensiveHealthResult,
)
from monsteriser_monster_generator.systems.dnd5e.models.base_monster import (
    BaseMonster,
)
from monsteriser_monster_generator.systems.dnd5e.models.damage_adjustments import (
    Resistance,
)
from monsteriser_monster_generator.systems.dnd5e.reference_data import (
    ChallengeRatingReference,
)


def create_reference() -> ChallengeRatingReference:
    """Create a small defensive CR reference."""
    return ChallengeRatingReference(
        reference=pl.DataFrame(
            [
                {
                    "challenge_rating": 1,
                    "armor_class": 14,
                    "save_bonus": 1,
                    "hit_points_min": 20,
                    "hit_points_max": 36,
                    "attack_bonus": 5,
                    "save_dc": 13,
                    "dpr_min": 12,
                    "dpr_max": 17,
                    "dpr_legend_min": 15,
                    "dpr_legend_max": 21,
                },
                {
                    "challenge_rating": 2,
                    "armor_class": 15,
                    "save_bonus": 1,
                    "hit_points_min": 37,
                    "hit_points_max": 54,
                    "attack_bonus": 5,
                    "save_dc": 13,
                    "dpr_min": 18,
                    "dpr_max": 23,
                    "dpr_legend_min": 22,
                    "dpr_legend_max": 28,
                },
            ]
        )
    )


def test_calculate_monster_defensive_cr_uses_effective_hit_points() -> None:
    """Derive defensive CR from effective hit points."""
    monster = BaseMonster(
        name="Test Monster",
        hitpoints=30,
        dexterity=12,
        expected_cr=1,
    )

    result = calculate_monster_defensive_cr(
        monster=monster,
        reference=create_reference(),
    )

    assert result == DefensiveChallengeRatingResult(
        challenge_rating=1,
        expected_armor_class=14,
        actual_armor_class=11,
        health=DefensiveHealthResult(
            base_hit_points=30,
            hit_point_multiplier=1.0,
            effective_hit_points=30.0,
        ),
    )


def test_calculate_monster_defensive_cr_moves_to_next_hp_band() -> None:
    """Use the next defensive CR when effective HP crosses a boundary."""
    monster = BaseMonster(
        name="Test Monster",
        hitpoints=40,
        expected_cr=2,
    )

    result = calculate_monster_defensive_cr(
        monster=monster,
        reference=create_reference(),
    )

    assert result.challenge_rating == 2
    assert result.health.effective_hit_points == 40.0
    assert result.expected_armor_class == 15


def test_calculate_monster_defensive_cr_applies_damage_adjustments() -> None:
    """Use adjusted hit points when determining defensive CR."""
    monster = BaseMonster(
        name="Test Monster",
        hitpoints=25,
        expected_cr=1,
        resistances=[
            Resistance(damage_type="fire"),
            Resistance(damage_type="cold"),
            Resistance(damage_type="lightning"),
        ],
    )

    result = calculate_monster_defensive_cr(
        monster=monster,
        reference=create_reference(),
    )

    assert result.challenge_rating == 2
    assert result.health.hit_point_multiplier == 2.0
    assert result.health.effective_hit_points == 50.0
    assert result.expected_armor_class == 15


def test_calculate_monster_defensive_cr_does_not_adjust_cr_for_ac_yet() -> None:
    """Keep defensive CR HP-based before AC adjustment is implemented."""
    low_ac_monster = BaseMonster(
        name="Low AC Monster",
        hitpoints=40,
        dexterity=6,
        expected_cr=2,
    )
    high_ac_monster = BaseMonster(
        name="High AC Monster",
        hitpoints=40,
        dexterity=20,
        expected_cr=2,
    )

    reference = create_reference()

    low_ac_result = calculate_monster_defensive_cr(
        monster=low_ac_monster,
        reference=reference,
    )
    high_ac_result = calculate_monster_defensive_cr(
        monster=high_ac_monster,
        reference=reference,
    )

    assert low_ac_result.challenge_rating == 2
    assert high_ac_result.challenge_rating == 2
    assert low_ac_result.actual_armor_class == 8
    assert high_ac_result.actual_armor_class == 15


def test_calculate_monster_defensive_cr_rejects_unmapped_effective_hp() -> None:
    """Propagate errors when effective HP falls outside the reference."""
    monster = BaseMonster(
        name="Test Monster",
        hitpoints=100,
        expected_cr=2,
    )

    with raises(
        ValueError,
        match=("Hit points fall outside the challenge-rating reference"),
    ):
        calculate_monster_defensive_cr(
            monster=monster,
            reference=create_reference(),
        )


def test_calculate_monster_defensive_cr_rejects_non_positive_hp() -> None:
    """Propagate invalid monster hit-point errors."""
    monster = BaseMonster(
        name="Test Monster",
        hitpoints=0,
        expected_cr=1,
    )

    with raises(
        ValueError,
        match="Monster hit points must be positive",
    ):
        calculate_monster_defensive_cr(
            monster=monster,
            reference=create_reference(),
        )
