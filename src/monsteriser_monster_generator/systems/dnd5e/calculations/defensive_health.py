"""Calculate effective defensive health for D&D 5E 2024 monsters."""

from dataclasses import dataclass

from ..models.base_monster import BaseMonster


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
    hit_point_multiplier: float = 1.0,
) -> DefensiveHealthResult:
    """Calculate a monster's effective hit points.

    Args:
        monster: The monster being evaluated
        hit_point_multiplier: How much the base hit_points are multiplied by, derived from monster resistances, immunities and vulernabilities.

    Returns:
        Effective hit-point calculation details.

    Raises:
        ValueError: If hit points or the multiplier are invalid.

    """
    if monster.hitpoints <= 0:
        raise ValueError("Monster hit points must be positive")

    if hit_point_multiplier <= 0:
        raise ValueError("Hit-point multiplier must be positive")

    effective_hit_points = monster.hitpoints * hit_point_multiplier

    return DefensiveHealthResult(
        base_hit_points=monster.hitpoints,
        hit_point_multiplier=hit_point_multiplier,
        effective_hit_points=effective_hit_points,
    )


def calculate_defensive_hit_point_multiplier(
    *, monster: BaseMonster, challenge_rating: int
) -> float:
    """Calculate the HP multiplier from defensive properties"""
    return 3.0
