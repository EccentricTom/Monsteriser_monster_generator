"""Calculate changes to effective hit points of D&D 5E 2024 monster due to regeneration."""

from dataclasses import dataclass

from ...models.base_monster import BaseMonster
from ...models.traits import RegenerationTrait


@dataclass(kw_only=True, frozen=True, slots=True)
class RegenerationAdjustmentResult:
    """Summarise effective HP contributed by regeneration."""

    hit_points_per_round: int
    rounds: int
    effective_hit_points: float


def calculate_regeneration_effective_hit_points(
    *,
    monster: BaseMonster,
    rounds: int = 3,
) -> RegenerationAdjustmentResult | None:
    """Calculate effective hit points contributed by regeneration."""
    if rounds < 1:
        raise ValueError("Rounds must be positive")

    regeneration_traits = [
        trait for trait in monster.traits if isinstance(trait, RegenerationTrait)
    ]

    if not regeneration_traits:
        return None

    if len(regeneration_traits) > 1:
        raise ValueError("Monster cannot have multiple regeneration traits")

    regeneration = regeneration_traits[0]

    effective_hit_points = regeneration.hit_points_per_round * rounds

    return RegenerationAdjustmentResult(
        hit_points_per_round=regeneration.hit_points_per_round,
        rounds=rounds,
        effective_hit_points=effective_hit_points,
    )
