"""Test D&D 5E combat-routine generation."""

from monsteriser_monster_generator.systems.dnd5e.calculations import (
    TurnRoutine,
    generate_turn_routines,
)
from monsteriser_monster_generator.systems.dnd5e.models import BaseMonster
from monsteriser_monster_generator.systems.dnd5e.models.actions import MonsterAction
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


def test_generate_turn_routines_empty_tuple_without_actions() -> None:
    """Return no routines when the monster has no primary actions."""
    monster = BaseMonster(name="Passive creature")

    result = generate_turn_routines(monster)

    assert result == ()


def test_generate_turn_routines_creates_one_primary_action() -> None:
    """ "Create one routine for one primary action."""
    bite = create_action(action_id="bite")

    monster = BaseMonster(name="Wolf", abilities=[bite])

    result = generate_turn_routines(monster)

    assert result == (
        TurnRoutine(
            primary_action_id="bite",
        ),
    )
