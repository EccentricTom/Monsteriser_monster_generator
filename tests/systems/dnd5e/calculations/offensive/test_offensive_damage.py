"""Calculate simplified monster damage for offensive CR."""

from dataclasses import replace

from pytest import approx, raises  # type: ignore

from monsteriser_monster_generator.systems.dnd5e.calculations import (
    OffensiveDamageResult,
    calculate_monster_offensive_damage,
)
from monsteriser_monster_generator.systems.dnd5e.calculations.combat_routines import TurnRoutine
from monsteriser_monster_generator.systems.dnd5e.models.actions import (
    AttackAction,
    DamageRoll,
    LimitedUsage,
    RechargeUsage,
)
from monsteriser_monster_generator.systems.dnd5e.models.base_monster import BaseMonster
from monsteriser_monster_generator.systems.dnd5e.models.model_types import (
    ActionTiming,
)


def create_attack(
    *,
    action_id: str,
    dice_count: int = 1,
    die_size: int = 4,
    modifier: int = 0,
    timing: ActionTiming = "action",
) -> AttackAction:
    """Create a configured attack for damage tests.

    Args:
        action_id: Unique identifier for the attack action.
        dice_count: the number of damage dice.
        die_size: the size of the damage dice, between 4 and 20.
        modifier: the flat damage modifier.
        timing: Action economy timing of the attack, either action or bonus_action

    Returns:
        A configured melee attack.

    """
    return AttackAction(
        action_id=action_id,
        name=action_id.replace("_", " ").title(),
        origin="natural",
        timing=timing,
        attack_range="melee",
        attack_bonus=5,
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


def test_offensive_damage_uses_repeatable_turn() -> None:
    """Use fallback damage when no special action is stronger."""
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

    result = calculate_monster_offensive_damage(monster)

    assert result == OffensiveDamageResult(
        average_damage_per_round=10.0,
        fallback_routine=TurnRoutine(
            primary_action_id="bite",
        ),
        special_action_id=None,
    )


def test_offensive_damage_selects_recharge_action() -> None:
    """Select a stronger recharge action."""
    bite = create_attack(
        action_id="bite",
        dice_count=2,
        die_size=6,
        modifier=2,
    )

    breath_weapon = replace(
        create_attack(
            action_id="breath_weapon",
            dice_count=4,
            die_size=6,
            modifier=4,
        ),
        usage=RechargeUsage(
            recharge_minimum=5,
        ),
    )

    monster = BaseMonster(
        name="Dragon",
        abilities=[
            bite,
            breath_weapon,
        ],
    )

    result = calculate_monster_offensive_damage(monster)

    assert result.average_damage_per_round == 14.0
    assert result.special_action_id == "breath_weapon"
    assert result.fallback_routine == TurnRoutine(
        primary_action_id="bite",
    )


def test_offensive_damage_selects_limited_action() -> None:
    """Select a stronger limited action."""
    bite = create_attack(
        action_id="bite",
        dice_count=2,
        die_size=6,
        modifier=2,
    )

    fire_barrage = replace(
        create_attack(
            action_id="fire_barrage",
            dice_count=10,
            die_size=10,
            modifier=3,
        ),
        usage=LimitedUsage(uses=1, period="day"),
    )

    monster = BaseMonster(
        name="Dragon",
        abilities=[
            bite,
            fire_barrage,
        ],
    )

    result = calculate_monster_offensive_damage(monster)

    assert result.average_damage_per_round == approx(25.3, rel=0.01, abs=0.01)
    assert result.special_action_id == "fire_barrage"
    assert result.fallback_routine == TurnRoutine(
        primary_action_id="bite",
    )


def test_offensive_damage_selects_fallback_action() -> None:
    """Select a stronger fallback action."""
    bite = create_attack(
        action_id="bite",
        dice_count=2,
        die_size=6,
        modifier=3,
    )

    bad_breath = replace(
        create_attack(
            action_id="bad_breath",
            dice_count=1,
            die_size=4,
            modifier=0,
        ),
        usage=RechargeUsage(
            recharge_minimum=5,
        ),
    )

    monster = BaseMonster(
        name="Dragon",
        abilities=[
            bite,
            bad_breath,
        ],
    )

    result = calculate_monster_offensive_damage(monster)

    assert result == OffensiveDamageResult(
        average_damage_per_round=10.0,
        fallback_routine=TurnRoutine(
            primary_action_id="bite",
        ),
        special_action_id=None,
    )


def test_offensvie_damage_rejects_non_positive_rounds() -> None:
    """Reject a calculation that has a non-positive value for rounds."""
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

    with raises(ValueError, match="Rounds must be positive"):
        calculate_monster_offensive_damage(
            monster,
            rounds=0,
        )


def test_offensive_damage_selects_strongest_special_option() -> None:
    """Select the special action with the highest CR-window average."""
    fallback = create_attack(
        action_id="bite",
        dice_count=2,
        die_size=6,
        modifier=2,
    )

    limited_attack = replace(
        create_attack(
            action_id="limited_attack",
            dice_count=6,
            die_size=6,
            modifier=0,
        ),
        usage=LimitedUsage(
            uses=1,
            period="day",
        ),
    )

    recharge_attack = replace(
        create_attack(
            action_id="recharge_attack",
            dice_count=4,
            die_size=6,
            modifier=4,
        ),
        usage=RechargeUsage(
            recharge_minimum=5,
        ),
    )

    monster = BaseMonster(
        name="Hybrid Monster",
        abilities=[
            fallback,
            limited_attack,
            recharge_attack,
        ],
    )

    result = calculate_monster_offensive_damage(monster)

    assert result.special_action_id == "recharge_attack"
    assert result.average_damage_per_round == 14.0
