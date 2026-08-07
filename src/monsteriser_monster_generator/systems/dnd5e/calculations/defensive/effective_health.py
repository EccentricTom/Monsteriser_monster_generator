"""Calculate effective defensive health for D&D 5E 2024 monsters.

Damage-adjustment policy:
- Duplicate damage types within one category count once.
- A damage type cannot appear in more than one adjustment category.
- Fewer than three unique resistances do not affect effective HP.
- Three or more unique resistances use the CR-based resistance multiplier.
- Fewer than three unique immunities do not affect effective HP.
- Three or more unique immunities use the CR-based immunity multiplier.
- If both resistance and immunity qualify, use the immunity multiplier only.
- Fewer than three unique vulnerabilities do not affect effective HP.
- Three or more unique vulnerabilities multiply effective HP by 0.5.
- Physical and non-physical damage types are currently weighted equally.

Conditional adjustments such as resistance only to nonmagical attacks are not
currently supported.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from ...models.base_monster import BaseMonster
from ...models.damage_adjustments import DamageAdjustment
from ...models.model_types import DamageType
from .damage_adjustments import calculate_damage_adjustment_multiplier


@dataclass(kw_only=True, frozen=True, slots=True)
class DefensiveHealthResult:
    """Summarise the effective hit-point calculations.

    Attributes:
        base_hit_points: The unmodified hit points of a monster
        hit_point_multiplier: Multiplier applied to base hit points
        effective_hit_points: The effective HP used for defensive CR calculations

    """

    base_hit_points: int
    hit_point_multiplier: float
    effective_hit_points: float


def calculate_effective_hit_points(
    *,
    monster: BaseMonster,
) -> DefensiveHealthResult:
    """Calculate a monster's effective hit points.

    Args:
        monster: The monster being evaluated

    Returns:
        Effective hit-point calculation details.

    Raises:
        ValueError: If hit points or the multiplier are invalid.

    """
    if monster.hitpoints <= 0:
        raise ValueError("Monster hit points must be positive")

    hit_point_multiplier = calculate_damage_adjustment_multiplier(
        monster=monster,
    )

    effective_hit_points = monster.hitpoints * hit_point_multiplier

    return DefensiveHealthResult(
        base_hit_points=monster.hitpoints,
        hit_point_multiplier=hit_point_multiplier,
        effective_hit_points=effective_hit_points,
    )


def get_adjusted_damage_types(
    adjustments: Sequence[DamageAdjustment],
) -> frozenset[DamageType]:
    """Return the unique damage types represented by adjustments.

    Args:
        adjustments: Damage adjustments to normalize

    Returns:
        Unique damage types represented by the adjustments

    """
    return frozenset(adjustment.damage_type for adjustment in adjustments)
