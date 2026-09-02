"""Calculate the simplified defensive CR of a D&D 5E 2024 monster."""

from dataclasses import dataclass

from ...models.base_monster import BaseMonster
from ...reference_data import ChallengeRatingReference
from .armor_class import (
    ArmorClassAdjustmentResult,
    calculate_armor_class_adjustment,
)
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

    hit_point_challenge_rating: int
    adjusted_challenge_rating: int
    challenge_rating: int
    armor_class: ArmorClassAdjustmentResult
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

    hit_point_challenge_rating = reference.get_hit_point_cr(
        health_result.effective_hit_points,
    )

    expected_armor_class = reference.get_expected_armor_class(
        challenge_rating=hit_point_challenge_rating,
    )

    armor_class_result = calculate_armor_class_adjustment(
        actual_armor_class=monster.armor_class,
        expected_armor_class=expected_armor_class,
    )

    adjusted_challenge_rating = (
        hit_point_challenge_rating + armor_class_result.challenge_rating_adjustment
    )

    challenge_rating = reference.clamp_challenge_rating(
        adjusted_challenge_rating,
    )

    return DefensiveChallengeRatingResult(
        hit_point_challenge_rating=hit_point_challenge_rating,
        adjusted_challenge_rating=adjusted_challenge_rating,
        challenge_rating=challenge_rating,
        armor_class=armor_class_result,
        health=health_result,
    )
