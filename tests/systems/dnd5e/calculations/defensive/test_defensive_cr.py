"""Test simplified defensive CR calculations for D&D 5E 2024."""

import polars as pl
from pytest import raises

from monsteriser_monster_generator.systems.dnd5e.calculations.defensive.armor_class import (
    ArmorClassAdjustmentResult,
)
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
from monsteriser_monster_generator.systems.dnd5e.models.traits import RegenerationTrait
from monsteriser_monster_generator.systems.dnd5e.reference_data import (
    ChallengeRatingReference,
)


def create_reference() -> ChallengeRatingReference:
    """Create a small defensive CR reference."""
    return ChallengeRatingReference(
        reference=pl.DataFrame(
            [
                {
                    "challenge_rating": 1.0,
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
                    "challenge_rating": 2.0,
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
                {
                    "challenge_rating": 3.0,
                    "armor_class": 15,
                    "save_bonus": 1,
                    "hit_points_min": 55,
                    "hit_points_max": 72,
                    "attack_bonus": 6,
                    "save_dc": 14,
                    "dpr_min": 24,
                    "dpr_max": 28,
                    "dpr_legend_min": 29,
                    "dpr_legend_max": 36,
                },
            ]
        )
    )


def test_calculate_monster_defensive_cr_uses_effective_hit_points() -> None:
    """Derive defensive CR from effective hit points."""
    monster = BaseMonster(
        name="Test Monster",
        hitpoints=30,
        dexterity=18,
        expected_cr=1,
    )

    result = calculate_monster_defensive_cr(
        monster=monster,
        reference=create_reference(),
    )

    assert result == DefensiveChallengeRatingResult(
        hit_point_challenge_rating=1,
        challenge_rating=1,
        armor_class=ArmorClassAdjustmentResult(
            actual_armor_class=14,
            expected_armor_class=14,
            difference=0,
            challenge_rating_steps=0,
        ),
        health=DefensiveHealthResult(
            base_hit_points=30,
            bonus_hit_points=0.0,
            hit_point_multiplier=1.0,
            effective_hit_points=30.0,
            regeneration=None,
        ),
    )


def test_calculate_monster_defensive_cr_moves_to_next_hp_band() -> None:
    """Use the next defensive CR when effective HP crosses a boundary."""
    monster = BaseMonster(
        name="Test Monster",
        hitpoints=40,
        dexterity=20,
        expected_cr=2,
    )

    result = calculate_monster_defensive_cr(
        monster=monster,
        reference=create_reference(),
    )

    assert result.hit_point_challenge_rating == 2
    assert result.challenge_rating == 2
    assert result.health.effective_hit_points == 40.0
    assert result.armor_class.expected_armor_class == 15
    assert result.armor_class.actual_armor_class == 15


def test_calculate_monster_defensive_cr_applies_damage_adjustments() -> None:
    """Use adjusted hit points when determining defensive CR."""
    monster = BaseMonster(
        name="Test Monster",
        hitpoints=25,
        dexterity=20,
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

    assert result.hit_point_challenge_rating == 2
    assert result.challenge_rating == 2
    assert result.health.hit_point_multiplier == 2.0
    assert result.health.effective_hit_points == 50.0
    assert result.armor_class.expected_armor_class == 15


def test_calculate_monster_defensive_cr_increases_cr_for_high_ac() -> None:
    """Increase defensive CR when AC exceeds the expected value."""
    monster = BaseMonster(
        name="High AC Monster",
        hitpoints=30,
        dexterity=22,
        expected_cr=1,
    )

    result = calculate_monster_defensive_cr(
        monster=monster,
        reference=create_reference(),
    )

    assert result.hit_point_challenge_rating == 1
    assert result.armor_class.actual_armor_class == 16
    assert result.armor_class.expected_armor_class == 14
    assert result.armor_class.difference == 2
    assert result.armor_class.challenge_rating_steps == 1
    assert result.challenge_rating == 2


def test_calculate_monster_defensive_cr_decreases_cr_for_low_ac() -> None:
    """Decrease defensive CR when AC is below the expected value."""
    monster = BaseMonster(
        name="Low AC Monster",
        hitpoints=40,
        dexterity=16,
        expected_cr=2,
    )

    result = calculate_monster_defensive_cr(
        monster=monster,
        reference=create_reference(),
    )

    assert result.hit_point_challenge_rating == 2
    assert result.armor_class.actual_armor_class == 13
    assert result.armor_class.expected_armor_class == 15
    assert result.armor_class.difference == -2
    assert result.armor_class.challenge_rating_steps == -1
    assert result.challenge_rating == 1


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


def test_calculate_monster_defensive_cr_ignores_one_point_ac_difference() -> None:
    """Do not adjust defensive CR for a one-point AC difference."""
    monster = BaseMonster(
        name="Test Monster",
        hitpoints=30,
        dexterity=20,
        expected_cr=1,
    )

    result = calculate_monster_defensive_cr(
        monster=monster,
        reference=create_reference(),
    )

    assert result.hit_point_challenge_rating == 1
    assert result.armor_class.actual_armor_class == 15
    assert result.armor_class.expected_armor_class == 14
    assert result.armor_class.difference == 1
    assert result.armor_class.challenge_rating_steps == 0
    assert result.challenge_rating == 1


def test_calculate_monster_defensive_cr_includes_regeneration() -> None:
    """Include regeneration when determining HP-derived defensive CR."""
    monster = BaseMonster(
        name="Troll",
        hitpoints=30,
        expected_cr=1.0,
        traits=[
            RegenerationTrait(
                hit_points_per_round=10,
            )
        ],
    )

    result = calculate_monster_defensive_cr(
        monster=monster,
        reference=create_reference(),
        rounds=3,
    )

    assert result.health.base_hit_points == 30
    assert result.health.bonus_hit_points == 30
    assert result.health.effective_hit_points == 60.0
    assert result.hit_point_challenge_rating == 3.0


def test_calculate_monster_defensive_cr_forwards_round_count() -> None:
    """Forward the evaluation window to regeneration calculations."""
    monster = BaseMonster(
        name="Troll",
        hitpoints=30,
        expected_cr=1.0,
        traits=[
            RegenerationTrait(
                hit_points_per_round=10,
            )
        ],
    )

    one_round_result = calculate_monster_defensive_cr(
        monster=monster,
        reference=create_reference(),
        rounds=1,
    )

    three_round_result = calculate_monster_defensive_cr(
        monster=monster,
        reference=create_reference(),
        rounds=3,
    )

    assert one_round_result.health.effective_hit_points == 40.0
    assert three_round_result.health.effective_hit_points == 60.0
    assert (
        three_round_result.hit_point_challenge_rating > one_round_result.hit_point_challenge_rating
    )
