"""Calculate the damage of limited-use and recharge use actions for D&D 5E 2024 Monsters."""

from collections.abc import Mapping

from ...models.actions import (
    LimitedUsage,
    MonsterAction,
    RechargeUsage,
)
from .damage import calculate_action_average_damage


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
