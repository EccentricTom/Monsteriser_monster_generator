"""Test simplified offensive challenge-rating calculations."""

from dataclasses import replace

import polars as pl
from pytest import raises

from monsteriser_monster_generator.systems.dnd5e.calculations import (
    calculate_monster_offensive_cr,
)
from monsteriser_monster_generator.systems.dnd5e.models.actions import (
    AttackAction,
    DamageRoll,
    LimitedUsage,
    SavingThrowAction,
    SavingThrowDamage,
)
from monsteriser_monster_generator.systems.dnd5e.models.base_monster import (
    BaseMonster,
)
from monsteriser_monster_generator.systems.dnd5e.models.model_types import (
    ActionTiming,
)
from monsteriser_monster_generator.systems.dnd5e.reference_data import ChallengeRatingReference


def create_attack(
    *,
    action_id: str,
    dice_count: int = 1,
    die_size: int = 4,
    modifier: int = 0,
    attack_bonus: int = 5,
    timing: ActionTiming = "action",
) -> AttackAction:
    """Create an attack for offensive CR tests."""
    return AttackAction(
        action_id=action_id,
        name=action_id.replace("_", " ").title(),
        origin="natural",
        timing=timing,
        attack_range="melee",
        attack_bonus=attack_bonus,
        reach_ft=5,
        damage=(
            DamageRoll(
                dice_count=dice_count,
                die_size=die_size,
                modifier=modifier,
                damage_type="slashing",
            ),
        ),
    )


def create_reference() -> ChallengeRatingReference:
    """Create a small valid CR reference for tests."""
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
                    "dpr_min": 1,
                    "dpr_max": 10,
                    "dpr_legend_min": 1,
                    "dpr_legend_max": 12,
                },
                {
                    "challenge_rating": 2,
                    "armor_class": 15,
                    "save_bonus": 1,
                    "hit_points_min": 37,
                    "hit_points_max": 54,
                    "attack_bonus": 5,
                    "save_dc": 13,
                    "dpr_min": 11,
                    "dpr_max": 20,
                    "dpr_legend_min": 13,
                    "dpr_legend_max": 24,
                },
            ]
        )
    )


def test_calculate_monster_offensive_cr_uses_standard_dpr_band() -> None:
    """Map average monster damage to a standard offensive CR."""
    bite = create_attack(
        action_id="bite",
        dice_count=2,
        die_size=6,
        modifier=3,
    )

    monster = BaseMonster(
        name="Wolf",
        abilities=[bite],
    )

    result = calculate_monster_offensive_cr(
        monster=monster,
        reference=create_reference(),
    )

    assert result.damage_challenge_rating == 1.0
    assert result.challenge_rating == 1.0
    assert result.damage.average_damage_per_round == 10.0


def test_calculate_monster_offensive_cr_moves_to_next_band() -> None:
    """Use the next CR when damage crosses the DPR boundary."""
    slam = create_attack(
        action_id="slam",
        dice_count=3,
        die_size=6,
        modifier=1,
    )

    monster = BaseMonster(
        name="Construct",
        abilities=[slam],
    )

    result = calculate_monster_offensive_cr(
        monster=monster,
        reference=create_reference(),
    )

    assert result.challenge_rating == 2.0
    assert result.damage.average_damage_per_round == 11.5


def test_calculate_monster_offensive_cr_uses_legendary_band() -> None:
    """Use legendary DPR bands when requested."""
    slam = create_attack(
        action_id="slam",
        dice_count=3,
        die_size=6,
        modifier=1,
    )

    monster = BaseMonster(
        name="Legendary Construct",
        abilities=[slam],
    )

    result = calculate_monster_offensive_cr(
        monster=monster,
        reference=create_reference(),
        legendary=True,
    )

    assert result.challenge_rating == 1
    assert result.damage.average_damage_per_round == 11.5


def test_calculate_monster_offensive_cr_uses_limited_action_damage() -> None:
    """Use limited-action average damage for the CR lookup."""
    bite = create_attack(
        action_id="bite",
        dice_count=1,
        die_size=6,
        modifier=2,
    )

    limited_attack = replace(
        create_attack(
            action_id="power_strike",
            dice_count=3,
            die_size=6,
            modifier=1,
        ),
        usage=LimitedUsage(
            uses=1,
            period="day",
        ),
    )

    monster = BaseMonster(
        name="Predator",
        abilities=[
            bite,
            limited_attack,
        ],
    )

    result = calculate_monster_offensive_cr(
        monster=monster,
        reference=create_reference(),
    )

    assert result.damage.special_action_id == "power_strike"


def test_calculate_monster_offensive_cr_forwards_round_count() -> None:
    """Forward the custom evaluation window to damage calculation."""
    bite = create_attack(
        action_id="bite",
        dice_count=1,
        die_size=6,
        modifier=2,
    )

    limited_attack = replace(
        create_attack(
            action_id="power_strike",
            dice_count=3,
            die_size=6,
            modifier=1,
        ),
        usage=LimitedUsage(
            uses=1,
            period="day",
        ),
    )

    monster = BaseMonster(
        name="Predator",
        abilities=[
            bite,
            limited_attack,
        ],
    )

    three_round_result = calculate_monster_offensive_cr(
        monster=monster,
        reference=create_reference(),
        rounds=3,
    )

    one_round_result = calculate_monster_offensive_cr(
        monster=monster,
        reference=create_reference(),
        rounds=1,
    )

    assert (
        one_round_result.damage.average_damage_per_round
        > three_round_result.damage.average_damage_per_round
    )


def test_calculate_monster_offensive_cr_rejects_non_positive_rounds() -> None:
    """Propagate invalid damage-window errors."""
    bite = create_attack(
        action_id="bite",
    )

    monster = BaseMonster(
        name="Wolf",
        abilities=[bite],
    )

    with raises(
        ValueError,
        match="Rounds must be positive",
    ):
        calculate_monster_offensive_cr(
            monster=monster,
            reference=create_reference(),
            rounds=0,
        )


def test_calculate_monster_offensive_cr_rejects_unmapped_damage() -> None:
    """Propagate errors when damage is outside the reference."""
    devastating_attack = create_attack(
        action_id="devastating_attack",
        dice_count=10,
        die_size=20,
        modifier=20,
    )

    monster = BaseMonster(
        name="Overpowered Monster",
        abilities=[devastating_attack],
    )

    with raises(
        ValueError,
        match=("Damage per round falls outside the challenge-rating reference"),
    ):
        calculate_monster_offensive_cr(
            monster=monster,
            reference=create_reference(),
        )


def test_calculate_monster_offensive_cr_increases_cr_for_high_attack_bonus() -> None:
    """Increase offensive CR when attack bonus exceeds the expected value."""
    bite = create_attack(
        action_id="bite",
        dice_count=2,
        die_size=6,
        modifier=3,
        attack_bonus=7,
    )

    monster = BaseMonster(
        name="Accurate Wolf",
        abilities=[bite],
    )

    result = calculate_monster_offensive_cr(
        monster=monster,
        reference=create_reference(),
    )

    assert result.damage_challenge_rating == 1.0
    assert result.accuracy is not None
    assert result.accuracy.actual_value == 7
    assert result.accuracy.expected_value == 5
    assert result.accuracy.challenge_rating_steps == 1
    assert result.challenge_rating == 2.0


def test_calculate_monster_offensive_cr_decreases_cr_for_low_attack_bonus() -> None:
    """Decrease offensive CR when attack bonus is below the expected value."""
    slam = create_attack(
        action_id="slam",
        dice_count=3,
        die_size=6,
        modifier=1,
        attack_bonus=3,
    )

    monster = BaseMonster(
        name="Inaccurate Construct",
        abilities=[slam],
    )

    result = calculate_monster_offensive_cr(
        monster=monster,
        reference=create_reference(),
    )

    assert result.damage_challenge_rating == 2.0
    assert result.accuracy is not None
    assert result.accuracy.actual_value == 3
    assert result.accuracy.expected_value == 5
    assert result.accuracy.challenge_rating_steps == -1
    assert result.challenge_rating == 1.0


def test_calculate_monster_offensive_cr_uses_save_dc() -> None:
    """Adjust offensive CR using save DC for saving-throw damage."""
    fire_breath = SavingThrowAction(
        action_id="fire_breath",
        name="Fire Breath",
        origin="natural",
        ability="dexterity",
        difficulty_class=15,
        saving_throw=SavingThrowDamage(
            damage=(
                DamageRoll(
                    dice_count=2,
                    die_size=6,
                    modifier=3,
                    damage_type="fire",
                ),
            ),
            success_outcome="half",
        ),
    )

    monster = BaseMonster(
        name="Fire Monster",
        abilities=[fire_breath],
    )

    result = calculate_monster_offensive_cr(
        monster=monster,
        reference=create_reference(),
    )

    assert result.damage_challenge_rating == 1.0
    assert result.accuracy is not None
    assert result.accuracy.accuracy_type == "save_dc"
    assert result.accuracy.actual_value == 15
    assert result.accuracy.expected_value == 13
    assert result.accuracy.challenge_rating_steps == 1
    assert result.challenge_rating == 2.0
