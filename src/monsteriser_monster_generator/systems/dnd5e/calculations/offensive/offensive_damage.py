"""Calculate simplified monster damage for offensive CR."""

from collections.abc import Mapping
from dataclasses import dataclass

from ...models.actions import LimitedUsage, MonsterAction, RechargeUsage
from ...models.base_monster import BaseMonster
from ..combat_routines import (
    TurnRoutine,
    generate_repeatable_turn_routines,
)
from .damage import (
    calculate_action_average_damage,
    find_maximum_damage_turn,
)
from .usage_damage import (
    calculate_limited_use_average_damage,
    calculate_recharge_average_damage,
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


def calculate_monster_offensive_damage(
    monster: BaseMonster,
    *,
    rounds: int = 3,
) -> OffensiveDamageResult:
    """Calculate simplified raw damage for offensive CR.

    The strongest repeatable turn is used as the fallback. Each
    limited-use and recharge action is evaluated independently against
    that fallback.

    Args:
        monster: Monster being evaluated
        rounds: Number of rounds in the CR evaluation window. Defaults to 3.

    Returns:
        Strongest simplified offensive-damage result

    Raises:
        ValueError: If rounds value is invalid or no repeatable turn exists

    """
    if rounds < 1:
        raise ValueError("Rounds must be positive")

    actions_by_id = monster.get_abilities_by_id()

    repeatable_routines = generate_repeatable_turn_routines(monster)

    fallback_routine, fallback_damage = find_maximum_damage_turn(
        routines=repeatable_routines,
        actions_by_id=actions_by_id,
    )

    best_result = OffensiveDamageResult(
        average_damage_per_round=fallback_damage, fallback_routine=fallback_routine
    )

    for action in monster.get_abilities_by_timing("action"):
        candidate_damage = _calculate_special_action_damage(
            action=action,
            fallback_damage=fallback_damage,
            actions_by_id=actions_by_id,
            rounds=rounds,
        )

        if candidate_damage is None:
            continue

        if candidate_damage <= best_result.average_damage_per_round:
            continue

        best_result = OffensiveDamageResult(
            average_damage_per_round=candidate_damage,
            fallback_routine=fallback_routine,
            special_action_id=action.action_id,
        )

    return best_result


def _calculate_special_action_damage(
    *,
    action: MonsterAction,
    fallback_damage: float,
    actions_by_id: Mapping[str, MonsterAction],
    rounds: int,
) -> float | None:
    """Calculate CR-window damage for one special-use action.

    Args:
        action: Limited-usage or recharge-usage action.
        fallback_damage: Strongest repeatable turn damage.
        actions_by_id: Monster abilities indexed by identifier.
        rounds: Number of rounds in the evaluation window.

    Returns:
        Candidate average damage, or None for unsupported usage.

    """
    action_damage = calculate_action_average_damage(
        action=action,
        actions_by_id=actions_by_id,
    )

    if isinstance(action.usage, LimitedUsage):
        return calculate_limited_use_average_damage(
            limited_damage=action_damage,
            fallback_damage=fallback_damage,
            uses=action.usage.uses,
            rounds=rounds,
        )

    if isinstance(action.usage, RechargeUsage):
        return calculate_recharge_average_damage(
            recharge_damage=action_damage,
            fallback_damage=fallback_damage,
            recharge_probability=action.usage.recharge_probability,
            rounds=rounds,
        )

    return None
