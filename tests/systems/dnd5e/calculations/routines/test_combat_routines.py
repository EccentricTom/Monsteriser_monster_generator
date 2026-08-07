"""Test D&D 5E combat-routine generation."""

from dataclasses import replace

from monsteriser_monster_generator.systems.dnd5e.calculations import (
    TurnRoutine,
    generate_repeatable_turn_routines,
    generate_turn_routines,
)
from monsteriser_monster_generator.systems.dnd5e.models import BaseMonster
from monsteriser_monster_generator.systems.dnd5e.models.actions import (
    AttackAction,
    DamageRoll,
    LimitedUsage,
    MonsterAction,
)
from monsteriser_monster_generator.systems.dnd5e.models.model_types import (
    ActionTiming,
)


def create_action(
    *,
    action_id: str,
    timing: ActionTiming = "action",
) -> MonsterAction:
    """Create a minimal monster action for routine-generation tests.

    Args:
        action_id: Unique identifier for the action.
        timing: Action-econmy timing assigned to the action.

    Returns:
        A minimal configured monster action.

    """
    return MonsterAction(
        action_id=action_id,
        name=action_id.replace("_", " ").title(),
        category="special",
        origin="custom",
        timing=timing,
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


def test_generate_turn_routines_empty_tuple_without_actions() -> None:
    """Return no routines when the monster has no primary actions."""
    monster = BaseMonster(name="Passive creature")

    result = generate_turn_routines(monster)

    assert result == ()


def test_generate_turn_routines_creates_one_primary_action() -> None:
    """Create one routine for one primary action."""
    bite = create_action(action_id="bite")

    monster = BaseMonster(name="Wolf", abilities=[bite])

    result = generate_turn_routines(monster)

    assert result == (
        TurnRoutine(
            primary_action_id="bite",
        ),
    )


def test_generate_turn_routines_create_routine_for_each_primary_action() -> None:
    """Create a routine for each primary action of a monster."""
    bite = create_action(action_id="bite")
    claw = create_action(action_id="claw")

    monster = BaseMonster(
        name="Wolf Alpha",
        abilities=[
            bite,
            claw,
        ],
    )

    result = generate_turn_routines(monster)

    assert result == (
        TurnRoutine(
            primary_action_id="bite",
        ),
        TurnRoutine(
            primary_action_id="claw",
        ),
    )


def test_create_turn_routines_combines_action_with_bonus_action() -> None:
    """Combine a primary action with a bonus action."""
    bite = create_action(action_id="bite")
    quick_step = create_action(
        action_id="quick_step",
        timing="bonus_action",
    )

    monster = BaseMonster(
        name="Swift Wolf",
        abilities=[bite, quick_step],
    )

    result = generate_turn_routines(monster)

    assert result == (
        TurnRoutine(
            primary_action_id="bite",
        ),
        TurnRoutine(
            primary_action_id="bite",
            bonus_action_id="quick_step",
        ),
    )


def test_create_turn_routines_combine_all_actions_with_bonus_actions() -> None:
    """Create every action and bonus action combination available."""
    bite = create_action(
        action_id="bite",
    )
    claw = create_action(
        action_id="claw",
    )
    quick_bite = create_action(
        action_id="quick_bite",
        timing="bonus_action",
    )
    quick_step = create_action(
        action_id="quick_step",
        timing="bonus_action",
    )

    monster = BaseMonster(
        name="Swift Wolf Alpha",
        abilities=[
            bite,
            claw,
            quick_bite,
            quick_step,
        ],
    )

    result = generate_turn_routines(monster)

    assert result == (
        TurnRoutine(
            primary_action_id="bite",
        ),
        TurnRoutine(
            primary_action_id="bite",
            bonus_action_id="quick_bite",
        ),
        TurnRoutine(
            primary_action_id="bite",
            bonus_action_id="quick_step",
        ),
        TurnRoutine(
            primary_action_id="claw",
        ),
        TurnRoutine(
            primary_action_id="claw",
            bonus_action_id="quick_bite",
        ),
        TurnRoutine(
            primary_action_id="claw",
            bonus_action_id="quick_step",
        ),
    )


def test_create_turn_routines_does_not_create_bonus_action_only_routines() -> None:
    """Do not create a turn routine containing only bonus actions."""
    quick_step = create_action(
        action_id="quick_step",
        timing="bonus_action",
    )

    monster = BaseMonster(
        name="Defanged Wolf",
        abilities=[
            quick_step,
        ],
    )

    result = generate_turn_routines(monster)

    assert result == ()


def test_create_turn_routines_excludes_reactions() -> None:
    """Exclude reactions when creating a turn routine."""
    bite = create_action(
        action_id="bite",
    )
    parry = create_action(action_id="parry", timing="reaction")

    monster = BaseMonster(
        name="Parrying Wolf",
        abilities=[
            bite,
            parry,
        ],
    )

    result = generate_turn_routines(monster)

    assert result == (
        TurnRoutine(
            primary_action_id="bite",
        ),
    )


def test_generate_repeatable_turn_routines_excludes_limited_action() -> None:
    """Exclude limited-use primary actions from a fallback routine."""
    bite = create_attack(action_id="bite")

    powerful_bite = replace(
        create_attack(
            action_id="powerful_bite",
        ),
        usage=LimitedUsage(
            uses=1,
            period="day",
        ),
    )

    monster = BaseMonster(
        name="wolf",
        abilities=[bite, powerful_bite],
    )

    result = generate_repeatable_turn_routines(monster)

    assert result == (
        TurnRoutine(
            primary_action_id="bite",
        ),
    )


def test_generate_repeatable_turn_routines_excludes_limited_action_with_bonus_action() -> None:
    """Exclude limited-use primary actions from a fallback routine and including a bonus action."""
    bite = create_attack(
        action_id="bite",
    )

    quick_bite = create_action(action_id="quick_bite", timing="bonus_action")

    powerful_bite = replace(
        create_attack(
            action_id="powerful_bite",
        ),
        usage=LimitedUsage(
            uses=1,
            period="day",
        ),
    )

    monster = BaseMonster(
        name="wolf",
        abilities=[bite, powerful_bite, quick_bite],
    )

    result = generate_repeatable_turn_routines(monster)

    assert result == (
        TurnRoutine(
            primary_action_id="bite",
        ),
        TurnRoutine(
            primary_action_id="bite",
            bonus_action_id="quick_bite",
        ),
    )
