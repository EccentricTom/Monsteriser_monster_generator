"""Calculate the raw average damage for D&D 5E 2024 monster actions."""

from collections.abc import Mapping

from ..models.actions import (
    AttackAction,
    MonsterAction,
    MultiattackAction,
    SavingThrowAction,
    find_maximum_damage_routine,
)
from .combat_routines import TurnRoutine


def calculate_action_average_damage(
    *,
    action: MonsterAction,
    actions_by_id: Mapping[str, MonsterAction],
) -> float:
    """Calculate the average raw damage for one action.

    Multiattack damage is based on the highest-damage legal routine.
    Saving Throw damage assumes that affected targets fail their save.

    Args:
        action: Action of which to calculate the average damage.
        actions_by_id: Monster actions indexed by action identifier.

    Returns:
        The raw average damage produced by the action.

    """
    if isinstance(action, AttackAction):
        return action.average_damage()

    if isinstance(action, MultiattackAction):
        _, maximum_damage = find_maximum_damage_routine(
            multiattack=action,
            actions_by_id=actions_by_id,
        )
        return maximum_damage

    if isinstance(action, SavingThrowAction):
        failed_save_damage = action.saving_throw.average_failed_save()

        return failed_save_damage * action.expected_targets

    return 0.0


def calculate_turn_routine_damage(
    *, routine: TurnRoutine, actions_by_id: Mapping[str, MonsterAction]
) -> float:
    """Calculate the raw average damage for a complet turn routine.

    The routine consists of one primary action (Multiattack is treated as one action) and up to one bonus action if present.

    Args:
        routine: Turn Routine whose damage is calculated.
        actions_by_id: Monster actions indexed by action identifier.

    Returns:
        The combined raw average damage of a turn routine.

    Raises:
        KeyError: If the routine references an unknown action.

    """
    primary_action = actions_by_id[routine.primary_action_id]

    total_damage = calculate_action_average_damage(
        action=primary_action,
        actions_by_id=actions_by_id,
    )

    if routine.bonus_action_id is None:
        return total_damage

    bonus_action = actions_by_id[routine.bonus_action_id]

    return total_damage + calculate_action_average_damage(
        action=bonus_action, actions_by_id=actions_by_id
    )


def find_maximum_damage_turn(
    *,
    routines: tuple[TurnRoutine, ...],
    actions_by_id: Mapping[str, MonsterAction],
) -> tuple[TurnRoutine, float]:
    """Return the legal turn routine with the highest average damage.

    Unless otherwise limited, it is expected to always do the maximum possible damage, as this is how CR calculations work.

    Args:
        routines: Legal Turn routines to compare.
        actions_by_id: Monster actions indexed by action identifier

    Returns:
        Highest damage turn routine and its raw average damage.

    Raises:
        ValueError: If no turn routines are provided.

    """
    if not routines:
        raise ValueError("No turn routines were provided")

    return max(
        (
            (
                routine,
                calculate_turn_routine_damage(routine=routine, actions_by_id=actions_by_id),
            )
            for routine in routines
        ),
        key=lambda result: result[1],
    )
