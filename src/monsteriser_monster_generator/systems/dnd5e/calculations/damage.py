"""Calculate the raw average damage for D&D 5E 2024 monster actions."""

from collections.abc import Mapping
from dataclasses import dataclass

from ..models.actions import (
    AttackAction,
    LimitedUsage,
    MonsterAction,
    MultiattackAction,
    MultiattackRoutine,
    RechargeUsage,
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


def calculate_limited_use_average_damage(
    *,
    limited_damage: float,
    fallback_damage: float,
    uses: int,
    rounds: int = 3,
) -> float:
    """Calculate average damage across a fixed CR evaluation window.

    The standard window is 3, only change when necessary.

    Args:
        limited_damage: Damage from the limited use attack action.
        fallback_damage: Damage from attacks used when limited use attacks are no longer available.
        uses: the number of times a limited use action can be used.
        rounds: The CR evaluation window, meaning (3) rounds of combat.

    Returns:
        The average damage per round across the evaluation window.

    Raises:
        ValueError: If uses is negative or rounds is not posive.

    """
    if uses < 0:
        raise ValueError("Uses cannot be negative")
    if rounds < 1:
        raise ValueError("Rounds must be positive")
    if limited_damage <= fallback_damage:
        return fallback_damage

    limited_uses = min(uses, rounds)
    fallback_uses = rounds - limited_uses

    total_damage = limited_damage * limited_uses + fallback_damage * fallback_uses

    return total_damage / rounds


def calculate_limited_use_action_average_damage(
    *,
    limited_action: MonsterAction,
    fallback_action: MonsterAction,
    actions_by_id: Mapping[str, MonsterAction],
    rounds: int = 3,
) -> float:
    """Calculate CR-window damage for limited-use action.

    Args:
        limited_action: Limited-use action being evaluated.
        fallback_action: Repeatable action used when the limited action is unavailable or weaker.
        actions_by_id: Monster abilities indexed by identifier.
        rounds: Number of rounds in the CR evaluation window.

    Returns:
        Average damage per round across the evaluation window.

    Raises:
        TypeError: If the action does not use LimitedUsage.

    """
    if not isinstance(limited_action.usage, LimitedUsage):
        raise TypeError("Limited action must use LimitedUsage")
    limited_damage = calculate_action_average_damage(
        action=limited_action,
        actions_by_id=actions_by_id,
    )

    fallback_damage = calculate_action_average_damage(
        action=fallback_action,
        actions_by_id=actions_by_id,
    )

    return calculate_limited_use_average_damage(
        limited_damage=limited_damage,
        fallback_damage=fallback_damage,
        uses=limited_action.usage.uses,
        rounds=rounds,
    )


def calculate_recharge_average_damage(
    *, recharge_damage: float, fallback_damage: float, recharge_probability: float, rounds: int = 3
) -> float:
    """Calculate average recharge damage across a CR window.

    The recharge action is assumed to be available in the first round.
    In each later round, it contributes its damage according to its recharge
    probability; otherwise, the fallback action is used.

    Args:
        recharge_damage: Damage dealt by the recharge action.
        fallback_damage: Damage_dealt by the repeatable action.
        recharge_probability: Probability of recharging between rounds.
        rounds: Number of rounds in the CR evaluation window.

    Returns:
        Average damage per round across the evaluation window.

    Raises:
        ValueError: If the probability is outside zero to one or the number of rounds is not positive.

    """
    if not 0.0 <= recharge_probability <= 1.0:
        raise ValueError("Recharge probability must be between 0 and 1")

    if rounds < 1:
        raise ValueError("Rounds must be positive")

    if recharge_damage <= fallback_damage:
        return fallback_damage

    later_round_damage = recharge_damage * recharge_probability + fallback_damage * (
        1.0 - recharge_probability
    )

    total_damage = recharge_damage + later_round_damage * (rounds - 1)

    return total_damage / rounds


def calculate_recharge_action_average_damage(
    *,
    recharge_action: MonsterAction,
    fallback_action: MonsterAction,
    actions_by_id: Mapping[str, MonsterAction],
    rounds: int = 3,
) -> float:
    """Calculate the CR-window damage for a recharge action.

    Args:
        recharge_action: Recharge action being evaluated.
        fallback_action: Fallback action to use when Recharge action not available.
        actions_by_id: Monster abilities indexed by identifier.
        rounds: Number of rounds in the CR evaluation window. Defaults to 3.

    Returns:
        Average damage per round across the CR evaluation window

    Raises:
        TypeError: If the action does not use RechargeUsage.

    """
    if not isinstance(
        recharge_action.usage,
        RechargeUsage,
    ):
        raise TypeError("Recharge action must use RechargeUsage.")

    recharge_damage = calculate_action_average_damage(
        action=recharge_action, actions_by_id=actions_by_id
    )

    fallback_damage = calculate_action_average_damage(
        action=fallback_action, actions_by_id=actions_by_id
    )

    return calculate_recharge_average_damage(
        recharge_damage=recharge_damage,
        fallback_damage=fallback_damage,
        recharge_probability=recharge_action.usage.recharge_probability,
        rounds=rounds,
    )


@dataclass(kw_only=True, frozen=True, slots=True)
class OffensiveDamageResult:
    """Summarize damage used for offensive CR calculations.

    Attributes:
        average_damage_per_round: Average raw damage across the CR evaluation window.
        fallback_routine: Strongest repeatable turn routine.
        special_action_id: Limited-use or recharge action selected over the fallback, if any.

    """

    average_damage_per_round: float
    fallback_routine: TurnRoutine
    special_action_id: str | None = None
