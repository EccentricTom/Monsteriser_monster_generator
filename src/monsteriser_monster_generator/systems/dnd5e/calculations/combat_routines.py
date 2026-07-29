"""Generate legal combat routines for D&D 5E 2024 monsters."""

from collections.abc import Mapping
from dataclasses import dataclass

from ..models import BaseMonster
from ..models.actions import (
    AtWillUsage,
    MonsterAction,
)


def action_is_repeatable(action: MonsterAction) -> bool:
    """Return whether an action is repeatable every round or not.

    Args:
        action: Monster ability being inspected.

    Returns:
        Whether the action uses at-will usage.

    """
    return isinstance(action.usage, AtWillUsage)


@dataclass(kw_only=True, frozen=True, slots=True)
class TurnRoutine:
    """Represent the abilities used during one monster turn.

    Attributes:
        primary_action_id: Identifier of the action used for the monster's primary action.
        bonus_action_id: Optional identifier of the bonus action used during the same turn.

    """

    primary_action_id: str
    bonus_action_id: str | None = None


def generate_turn_routines(
    monster: BaseMonster,
) -> tuple[TurnRoutine, ...]:
    """Generate legal action and bonus action combinations.

    Multiattack is treated like any other ability with "timing="action"". It is not expanded.

    Args:
        monster: Monster with actions to generate turn routines from.

    Returns:
        Every basic legal combination of one primary action and up to one bonus action.

    """
    primary_actions = monster.get_abilities_by_timing("action")
    bonus_actions = monster.get_abilities_by_timing("bonus_action")

    routines: list[TurnRoutine] = []

    for primary_action in primary_actions:
        routines.append(
            TurnRoutine(
                primary_action_id=primary_action.action_id,
            ),
        )
        routines.extend(
            TurnRoutine(
                primary_action_id=primary_action.action_id,
                bonus_action_id=bonus_action.action_id,
            )
            for bonus_action in bonus_actions
        )

    return tuple(routines)


def generate_repeatable_turn_routines(
    monster: BaseMonster,
) -> tuple[TurnRoutine, ...]:
    """Return turn routines containing only repeatable abilities.

    Args:
        monster: Monster whose routines are being evaluated.

    Returns:
        Repeatable primary and bonus-action combinations.

    """
    actions_by_id = monster.get_abilities_by_id()

    return tuple(
        routine
        for routine in generate_turn_routines(monster)
        if _turn_routine_is_repeatable(
            routine=routine,
            actions_by_id=actions_by_id,
        )
    )


def _turn_routine_is_repeatable(
    *,
    routine: TurnRoutine,
    actions_by_id: Mapping[str, MonsterAction],
) -> bool:
    """Return whether every action in a turn is repeatable.

    Args:
        routine: Turn routine being inspected.
        actions_by_id: Monster abilities indexed by identifier.

    Returns:
        Whether all actions in the routine are repeatable.

    """
    primary_action = actions_by_id[routine.primary_action_id]

    if not action_is_repeatable(primary_action):
        return False

    if routine.bonus_action_id is None:
        return True

    bonus_action = actions_by_id[routine.bonus_action_id]

    return action_is_repeatable(bonus_action)
