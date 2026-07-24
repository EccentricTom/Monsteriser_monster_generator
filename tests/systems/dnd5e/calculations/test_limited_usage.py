"""Calculate the raw average damage for D&D 5E 2024 monster actions regarding limited use attacks."""

from dataclasses import replace

from pytest import raises

from monsteriser_monster_generator.systems.dnd5e.calculations import (
    calculate_limited_use_action_average_damage,
    calculate_limited_use_average_damage,
)
from monsteriser_monster_generator.systems.dnd5e.models.actions import (
    AttackAction,
    DamageRoll,
    LimitedUsage,
    MonsterAction,
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


def test_limited_use_damage_once_over_three_rounds() -> None:
    """Average one limited use and two fallback turns."""
    result = calculate_limited_use_average_damage(
        limited_damage=30.0,
        fallback_damage=12.0,
        uses=1,
    )

    assert result == 18.0


def test_limited_use_damage_twice_over_three_rounds() -> None:
    """Average of two lmiited use and one fallback turn."""
    result = calculate_limited_use_average_damage(
        limited_damage=30.0,
        fallback_damage=12.0,
        uses=2,
    )

    assert result == 24.0


def test_limited_use_damage_uses_fallback_when_stronger() -> None:
    """Use the fallback option when it does more damage."""
    result = calculate_limited_use_average_damage(
        limited_damage=8.0,
        fallback_damage=12.0,
        uses=2,
    )

    assert result == 12.0


def test_limited_use_damage_uses_fallback_when_equal() -> None:
    """Use the fallback option when the damage is equal."""
    result = calculate_limited_use_average_damage(
        limited_damage=12.0,
        fallback_damage=12.0,
        uses=2,
    )

    assert result == 12.0


def test_limited_use_damage_accepts_zero_uses() -> None:
    """Use fallback damage when no limited uses are available."""
    result = calculate_limited_use_average_damage(
        limited_damage=30.0,
        fallback_damage=12.0,
        uses=0,
    )

    assert result == 12.0


def test_limited_use_damage_supports_custom_round_count() -> None:
    """Calculate average damage over a custom evaluation window."""
    result = calculate_limited_use_average_damage(
        limited_damage=30.0,
        fallback_damage=10.0,
        uses=2,
        rounds=4,
    )

    assert result == 20.0


def test_limited_use_damage_rejects_negative_uses() -> None:
    """Reject a negative limited-use_count."""
    with raises(
        ValueError,
        match="Uses cannot be negative",
    ):
        calculate_limited_use_average_damage(
            limited_damage=30.0,
            fallback_damage=12.0,
            uses=-1,
        )


def test_limited_use_damage_rejects_zero_rounds() -> None:
    """Reject an empty evaluation window."""
    with raises(
        ValueError,
        match="Rounds must be positive",
    ):
        calculate_limited_use_average_damage(
            limited_damage=30.0,
            fallback_damage=12.0,
            uses=1,
            rounds=0,
        )


def test_calculate_limited_action_average_damage_once() -> None:
    """Average one limited attack and two fallback attacks."""
    powerful_bite = create_attack(
        action_id="powerful_bite",
        dice_count=4,
        die_size=8,
        modifier=2,
    )

    powerful_bite = replace(powerful_bite, usage=LimitedUsage(uses=1, period="day"))

    claw = create_attack(
        action_id="claw",
        dice_count=2,
        die_size=6,
        modifier=3,
    )

    actions_by_id: dict[str, MonsterAction] = {
        powerful_bite.action_id: powerful_bite,
        claw.action_id: claw,
    }

    result = calculate_limited_use_action_average_damage(
        limited_action=powerful_bite, fallback_action=claw, actions_by_id=actions_by_id
    )

    assert result == 40 / 3


def test_calculate_limited_action_average_damage_twice() -> None:
    """Average two limited attacks and one fallback attack."""
    limited_attack = replace(
        create_attack(
            action_id="limited_attack",
            dice_count=3,
            die_size=6,
            modifier=1,
        ),
        usage=LimitedUsage(
            uses=2,
            period="day",
        ),
    )

    fallback = create_attack(
        action_id="fallback",
        dice_count=1,
        die_size=6,
        modifier=2,
    )

    actions_by_id: dict[str, MonsterAction] = {
        limited_attack.action_id: limited_attack,
        fallback.action_id: fallback,
    }

    result = calculate_limited_use_action_average_damage(
        limited_action=limited_attack,
        fallback_action=fallback,
        actions_by_id=actions_by_id,
    )

    assert result == 9.5


def test_calculate_limited_action_uses_stronger_fallback() -> None:
    """Use the fallback every round when it deals more damage."""
    limited_attack = replace(
        create_attack(
            action_id="limited_attack",
            dice_count=1,
            die_size=4,
        ),
        usage=LimitedUsage(
            uses=2,
            period="day",
        ),
    )

    fallback = create_attack(
        action_id="fallback",
        dice_count=2,
        die_size=6,
        modifier=3,
    )

    actions_by_id: dict[str, MonsterAction] = {
        limited_attack.action_id: limited_attack,
        fallback.action_id: fallback,
    }

    result = calculate_limited_use_action_average_damage(
        limited_action=limited_attack,
        fallback_action=fallback,
        actions_by_id=actions_by_id,
    )

    assert result == 10.0


def test_calculate_limited_action_rejects_at_will_action() -> None:
    """Reject an action without LimitedUsage."""
    bite = create_attack(
        action_id="bite",
    )

    claw = create_attack(
        action_id="claw",
    )

    actions_by_id: dict[str, MonsterAction] = {
        bite.action_id: bite,
        claw.action_id: claw,
    }

    with raises(
        TypeError,
        match="Limited action must use LimitedUsage",
    ):
        calculate_limited_use_action_average_damage(
            limited_action=bite,
            fallback_action=claw,
            actions_by_id=actions_by_id,
        )
