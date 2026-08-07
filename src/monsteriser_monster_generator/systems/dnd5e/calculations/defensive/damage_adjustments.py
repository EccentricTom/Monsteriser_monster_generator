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


@dataclass(frozen=True, slots=True)
class DamageAdjustmentPolicy:
    """Define how damage adjustments affect effective hit points."""

    significance_threshold: int = 3
    vulnerability_multiplier: float = 0.5
    immunity_overrides_resistance: bool = True
    allow_cross_category_duplicates: bool = False
    distinguish_physical_damage: bool = False


DAMAGE_ADJUSTMENT_POLICY = DamageAdjustmentPolicy()


def describe_damage_adjustment_policy() -> str:
    """Return a user-facing description of the damage-adjustment policy."""
    policy = DAMAGE_ADJUSTMENT_POLICY

    return (
        f"At least {policy.significance_threshold} unique damage types "
        "are required for resistances, immunities, or vulnerabilities "
        "to affect effective hit points. If both resistance and immunity "
        "qualify, immunity takes precedence. Significant vulnerabilities "
        f"apply a ×{policy.vulnerability_multiplier:g} hit-point multiplier. "
        "Physical and non-physical damage types are currently weighted equally."
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


def validate_damage_adjustment_categories(
    *,
    monster: BaseMonster,
) -> None:
    """Validate that damage types do not span mulitple categories.

    Args:
        monster: Monster whose damage adjustments are being validated.

    Raises:
        ValueError: If a damage type appears in more than one adjustment category.

    """
    if DAMAGE_ADJUSTMENT_POLICY.allow_cross_category_duplicates:
        return

    resistance_types = get_adjusted_damage_types(
        monster.resistances,
    )

    immune_types = get_adjusted_damage_types(monster.immunities)

    vulnerability_types = get_adjusted_damage_types(monster.vulnerabilities)

    resistence_immunity_overlaps = resistance_types & immune_types

    resistance_vulnerability_overlaps = resistance_types & vulnerability_types

    immunity_vulnerability_overaps = immune_types & vulnerability_types

    overlapping_types = (
        resistence_immunity_overlaps
        | resistance_vulnerability_overlaps
        | immunity_vulnerability_overaps
    )

    if overlapping_types:
        formatted_types = ", ".join(sorted(overlapping_types))
        raise ValueError(
            f"Damage types cannot appear in multiple adjustment categories: {formatted_types}"
        )


def get_resistance_hit_point_multiplier(
    *,
    expected_challenge_rating: int,
) -> float:
    """Return the effective-HP multiplier for resistance.

    Args:
        expected_challenge_rating: Monster's intended challenge rating.

    Returns:
        Effective hit-point multiplier for resistance.

    Raises:
        ValueError: If the challenge rating is invalid.

    """
    if expected_challenge_rating <= 0:
        raise ValueError("Expected challenge rating must be positive")

    if expected_challenge_rating <= 4:
        return 2.0

    if expected_challenge_rating <= 10:
        return 1.5

    if expected_challenge_rating <= 16:
        return 1.25

    return 1.0


def get_immunity_hit_point_multiplier(
    *,
    expected_challenge_rating: int,
) -> float:
    """Return the effective-HP multiplier for immunity.

    Args:
        expected_challenge_rating: Monster's intended challenge rating.

    Returns:
        Effective hit-point multiplier for immunity.

    Raises:
        ValueError: If the challenge rating is invalid.

    """
    if expected_challenge_rating <= 0:
        raise ValueError("Expected challenge rating must be positive")

    if expected_challenge_rating <= 10:
        return 2.0

    if expected_challenge_rating <= 16:
        return 1.5

    return 1.25


def has_significant_damage_adjustments(
    adjustments: Sequence[DamageAdjustment],
) -> bool:
    """Return whether a monster has enough damage adjustments to be significant for CR calculations.

    Args:
        adjustments: Damage adjustments to evaluate.

    Returns:
        Whether enough unique damage types are adjusted to affect CR.

    """
    adjusted_types = get_adjusted_damage_types(adjustments=adjustments)

    return len(adjusted_types) >= DAMAGE_ADJUSTMENT_POLICY.significance_threshold


def calculate_damage_adjustment_multiplier(
    *,
    monster: BaseMonster,
) -> float:
    """Calculate the effective-HP multiplier from damage adjustments.

    Args:
        monster: Monster being evaluated

    Returns:
        Combined effective-HP multiplier from resistances, immunities,
        and vulnerabilities

    Raises:
        ValueError: If the challenge rating is non-positive or damage adjustment categories contain conflicting damage types.

    """
    expected_challenge_rating = monster.expected_cr

    if expected_challenge_rating <= 0:
        raise ValueError("Expected challenge rating must be positive")

    validate_damage_adjustment_categories(monster=monster)

    resistance_qualifies = has_significant_damage_adjustments(monster.resistances)

    immunity_qualifies = has_significant_damage_adjustments(monster.immunities)

    vulnerability_qualifies = has_significant_damage_adjustments(monster.vulnerabilities)

    defensive_multiplier = 1.0

    if immunity_qualifies:
        defensive_multiplier = get_immunity_hit_point_multiplier(
            expected_challenge_rating=expected_challenge_rating,
        )
    elif resistance_qualifies:
        defensive_multiplier = get_resistance_hit_point_multiplier(
            expected_challenge_rating=expected_challenge_rating
        )
    if vulnerability_qualifies:
        defensive_multiplier *= DAMAGE_ADJUSTMENT_POLICY.vulnerability_multiplier

    return defensive_multiplier
