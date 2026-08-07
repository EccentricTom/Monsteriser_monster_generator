"""Test recharge-action damage calculations."""

from dataclasses import replace

from pytest import raises

from monsteriser_monster_generator.systems.dnd5e.calculations import (
    calculate_recharge_action_average_damage,
    calculate_recharge_average_damage,
)
from monsteriser_monster_generator.systems.dnd5e.models.actions import (
    AttackAction,
    DamageRoll,
    MonsterAction,
    RechargeUsage,
)
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


def test_recharge_damage_over_three_rounds() -> None:
    """Average an initially available Recharge 5-6 action."""
    result = calculate_recharge_average_damage(
        recharge_damage=30.0,
        fallback_damage=12.0,
        recharge_probability=2 / 6,
    )

    assert result == 22.0


def test_recharge_damage_for_recharge_six() -> None:
    """Average an initially available Recharge 6 action."""
    result = calculate_recharge_average_damage(
        recharge_damage=30.0,
        fallback_damage=12.0,
        recharge_probability=1 / 6,
    )

    assert result == 20.0


def test_recharge_damage_uses_fallback_when_stronger() -> None:
    """Use the fallback every round when it deals more damage."""
    result = calculate_recharge_average_damage(
        recharge_damage=8.0,
        fallback_damage=12.0,
        recharge_probability=2 / 6,
    )

    assert result == 12.0


def test_recharge_damage_with_zero_probability() -> None:
    """Use the recharge action once when it cannot recharge."""
    result = calculate_recharge_average_damage(
        recharge_damage=30.0,
        fallback_damage=12.0,
        recharge_probability=0.0,
    )

    assert result == 18.0


def test_recharge_damage_with_certain_recharge() -> None:
    """Use the recharge action every round when recharge is certain."""
    result = calculate_recharge_average_damage(
        recharge_damage=30.0,
        fallback_damage=12.0,
        recharge_probability=1.0,
    )

    assert result == 30.0


def test_recharge_damage_supports_one_round() -> None:
    """Use the initially available action in a one-round window."""
    result = calculate_recharge_average_damage(
        recharge_damage=30.0,
        fallback_damage=12.0,
        recharge_probability=1 / 6,
        rounds=1,
    )

    assert result == 30.0


def test_recharge_damage_rejects_probability_below_zero() -> None:
    """Reject a negative recharge probability."""
    with raises(
        ValueError,
        match="Recharge probability must be between 0 and 1",
    ):
        calculate_recharge_average_damage(
            recharge_damage=30.0,
            fallback_damage=12.0,
            recharge_probability=-0.1,
        )


def test_recharge_damage_rejects_probability_above_one() -> None:
    """Reject a recharge probability greater than one."""
    with raises(
        ValueError,
        match="Recharge probability must be between 0 and 1",
    ):
        calculate_recharge_average_damage(
            recharge_damage=30.0,
            fallback_damage=12.0,
            recharge_probability=1.1,
        )


def test_recharge_damage_rejects_zero_rounds() -> None:
    """Reject an empty CR evaluation window."""
    with raises(
        ValueError,
        match="Rounds must be positive",
    ):
        calculate_recharge_average_damage(
            recharge_damage=30.0,
            fallback_damage=12.0,
            recharge_probability=2 / 6,
            rounds=0,
        )


def test_calculate_recharge_action_average_damage_for_recharge_five() -> None:
    """Average a Recharge 5-6 action against its fallback."""
    breath_weapon = replace(
        create_attack(
            action_id="breath_weapon",
            dice_count=10,
            die_size=6,
            modifier=0,
        ),
        usage=RechargeUsage(recharge_minimum=5),
    )

    bite = create_attack(
        action_id="bite",
        dice_count=4,
        die_size=6,
        modifier=3,
    )

    actions_by_id: dict[str, MonsterAction] = {
        breath_weapon.action_id: breath_weapon,
        bite.action_id: bite,
    }

    result = calculate_recharge_action_average_damage(
        recharge_action=breath_weapon, fallback_action=bite, actions_by_id=actions_by_id
    )

    assert result == 27.0


def test_calculate_recharge_action_average_damage_for_recharge_six() -> None:
    """Average a Recharge 6 action against its fallback."""
    breath_weapon = replace(
        create_attack(
            action_id="breath_weapon",
            dice_count=10,
            die_size=6,
            modifier=1,
        ),
        usage=RechargeUsage(recharge_minimum=6),
    )

    bite = create_attack(
        action_id="bite",
        dice_count=3,
        die_size=6,
        modifier=3,
    )

    actions_by_id: dict[str, MonsterAction] = {
        breath_weapon.action_id: breath_weapon,
        bite.action_id: bite,
    }

    result = calculate_recharge_action_average_damage(
        recharge_action=breath_weapon,
        fallback_action=bite,
        actions_by_id=actions_by_id,
    )

    assert result == 23.5


def test_calculate_recharge_action_uses_stronger_fallback() -> None:
    """Use the fallback every round when it deals more damage."""
    breath_weapon = replace(
        create_attack(
            action_id="breath_weapon",
            dice_count=1,
            die_size=4,
            modifier=0,
        ),
        usage=RechargeUsage(recharge_minimum=5),
    )

    bite = create_attack(
        action_id="bite",
        dice_count=2,
        die_size=6,
        modifier=3,
    )

    actions_by_id: dict[str, MonsterAction] = {
        breath_weapon.action_id: breath_weapon,
        bite.action_id: bite,
    }

    result = calculate_recharge_action_average_damage(
        recharge_action=breath_weapon,
        fallback_action=bite,
        actions_by_id=actions_by_id,
    )

    assert result == 10.0


def test_calculate_recharge_action_rejects_at_will_action() -> None:
    """Reject an action without RechargeUsage."""
    claw = create_attack(action_id="claw", dice_count=1, die_size=6, modifier=3)

    bite = create_attack(
        action_id="bite",
        dice_count=5,
        die_size=6,
        modifier=3,
    )

    actions_by_id: dict[str, MonsterAction] = {
        claw.action_id: claw,
        bite.action_id: bite,
    }

    with raises(
        TypeError,
        match="Recharge action must use RechargeUsage",
    ):
        calculate_recharge_action_average_damage(
            recharge_action=claw,
            fallback_action=bite,
            actions_by_id=actions_by_id,
        )
