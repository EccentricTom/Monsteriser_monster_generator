"""Calculate the raw average damage for D&D 5E 2024 monster actions."""

from collections.abc import Mapping

from ..models.actions import (
    AttackAction,
    MonsterAction,
    MultiattackAction,
    MultiattackRoutine,
    SavingThrowAction,
)
from ..models.base_monster import BaseMonster
from .combat_routines import TurnRoutine, generate_turn_routines


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
        _, maximum_damage = find_maximum_damage_multiattack_routine(
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


def find_monster_maximum_damage_turn(
    monster: BaseMonster,
) -> tuple[TurnRoutine, float]:
    """Return a monster's highest-damage basic turn.

    Args:
        monster: Monster whose available turns are evaluated.

    Returns:
        Highest-damage legal turn and its raw average damage.

    """
    actions_by_id = monster.get_abilities_by_id()
    routines = generate_turn_routines(monster)

    return find_maximum_damage_turn(
        routines=routines,
        actions_by_id=actions_by_id,
    )


def calculate_routine_average_damage(
    *,
    routine: MultiattackRoutine,
    actions_by_id: Mapping[str, MonsterAction],
) -> float:
    """Calculate average damage for one Multiattack routine.

    Args:
        routine: Concrete action sequence.
        actions_by_id: Available actions indexed by identifier.

    Returns:
        Combined average on-hit damage.

    Raises:
        TypeError: If a referenced ability is not an attack.

    """
    total_damage = 0.0

    for action_id in routine.action_ids:
        action = actions_by_id[action_id]
        if not isinstance(action, AttackAction):
            raise TypeError(f"Action {action_id!r} is not an AttackAction")
        total_damage += action.average_damage()
    return total_damage


def calculate_multiattack_routine_damage(
    *,
    routine: MultiattackRoutine,
    actions_by_id: Mapping[str, MonsterAction],
) -> float:
    """Calculate raw damage for one Multiattack routine.

    Non-damaging abilities contribute zero damage.

    Args:
        routine: Concrete Multiattack sequence.
        actions_by_id: Monster abilities indexed by identifier.

    Returns:
        Combined raw average damage of the sequence.

    """
    return sum(
        calculate_action_average_damage(
            action=actions_by_id[action_id],
            actions_by_id=actions_by_id,
        )
        for action_id in routine.action_ids
    )


def find_maximum_damage_multiattack_routine(
    *,
    multiattack: MultiattackAction,
    actions_by_id: Mapping[str, MonsterAction],
) -> tuple[MultiattackRoutine, float]:
    """Find the highest-damage legal Multiattack routine.

    Args:
        multiattack: Multiattack definition being evaluated.
        actions_by_id: Monster abilities indexed by identifier.

    Returns:
        Highest-damage routine and its raw average damage.

    """
    return max(
        (
            (
                routine,
                calculate_multiattack_routine_damage(
                    routine=routine,
                    actions_by_id=actions_by_id,
                ),
            )
            for routine in multiattack.valid_routines()
        ),
        key=lambda result: result[1],
    )
