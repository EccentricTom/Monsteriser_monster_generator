"""Calculate the simplified defensive CR of a D&D 5E 2024 monster."""

from dataclasses import dataclass

from ...models.base_monster import BaseMonster
from ...reference_data import ChallengeRatingReference
from .effective_health import (
    DefensiveHealthResult,
    calculate_effective_hit_points,
)


@dataclass(kw_only=True, frozen=True, slots=True)
class DefensiveChallengeRatingResult:
    """Summarize a simplified defensive CR calculation.

    Attributes:
        challenge_rating: CR derived from effective hit points.
        expected_armor_class: Expected AC for the HP-derived CR.
        actual_armor_class: Monster's current armor class.
        health: Effective hit-point result used for the calculation.

    """

    challenge_rating: int
    expected_armor_class: int
    actual_armor_class: int
    health: DefensiveHealthResult


def calculate_monster_defensive_cr(
    *,
    monster: BaseMonster,
    reference: ChallengeRatingReference,
) -> DefensiveChallengeRatingResult:
    """Calculate preliminary defensive CR from effective hit points.

    Args:
        monster: Monster being evaluated.
        reference: Challenge-rating reference data.

    Returns:
        Preliminary defensive CR and supporting defensive statistics.

    Raises:
        ValueError: If effective hit points cannot be calculated or fall
            outside the challenge-rating reference.

    """
    health_result = calculate_effective_hit_points(
        monster=monster,
    )

    challenge_rating = reference.get_hit_point_cr(
        health_result.effective_hit_points,
    )

    expected_armor_class = reference.get_expected_armor_class(
        challenge_rating=challenge_rating,
    )

    return DefensiveChallengeRatingResult(
        challenge_rating=challenge_rating,
        expected_armor_class=expected_armor_class,
        actual_armor_class=monster.armor_class,
        health=health_result,
    )
