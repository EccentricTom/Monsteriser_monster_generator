"""Calculations related to legendary resistances for legendary monsters in D&D 5E 2024."""

from dataclasses import dataclass

from ...models.base_monster import BaseMonster
from ...models.traits import LegendaryResistanceTrait


@dataclass(kw_only=True, frozen=True, slots=True)
class LegendaryResistanceAdjustmentResult:
    """Summarise the effective HP contribution of a Legendary Resistance."""

    uses: int
    hit_points_per_use: float
    effective_hit_points: float


def get_legendary_resistance_hit_points_per_use(
    *,
    expected_challenge_rating: float,
) -> int:
    """Return effective hit points contributed by each use of legendary resistance.

    Args:
        expected_challenge_rating: Monster's intended challenge rating.

    Returns:
        Effective hit points contributed for each use.

    Raises:
        ValueError: If expected challenge rating is below 1.

    """
    if expected_challenge_rating < 1:
        raise ValueError("Legendary Resistance requires an expected challenge rating of at least 1")

    if expected_challenge_rating <= 4:
        return 10

    if expected_challenge_rating <= 10:
        return 20

    return 30


def calculate_legendary_resistance_effective_hit_points(
    *,
    monster: BaseMonster,
) -> LegendaryResistanceAdjustmentResult | None:
    """Calculate the effective HP contributed by Legendary Resistance."""
    legendary_resistance_traits: tuple[LegendaryResistanceTrait, ...] = tuple(
        trait for trait in monster.traits if isinstance(trait, LegendaryResistanceTrait)
    )

    if not legendary_resistance_traits:
        return None

    if len(legendary_resistance_traits) > 1:
        raise ValueError("Monster cannot have multiple Legendary Resistance traits")

    legendary_resistance = next(iter(legendary_resistance_traits))

    hit_points_per_use = get_legendary_resistance_hit_points_per_use(
        expected_challenge_rating=monster.expected_cr
    )

    effective_hit_points = legendary_resistance.uses * hit_points_per_use

    return LegendaryResistanceAdjustmentResult(
        uses=legendary_resistance.uses,
        hit_points_per_use=hit_points_per_use,
        effective_hit_points=float(effective_hit_points),
    )
