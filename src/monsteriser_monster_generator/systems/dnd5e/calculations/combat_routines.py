"""Generate legal combat routines for D&D 5E 2024 monsters."""

from dataclasses import dataclass

from ..models import BaseMonster


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
