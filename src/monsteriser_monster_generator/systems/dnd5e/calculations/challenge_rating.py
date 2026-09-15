"""Calculate the final D&D 5E 2024 monster challenge rating."""

from dataclasses import dataclass

from ..models.base_monster import BaseMonster
from ..reference_data import ChallengeRatingReference
from .defensive import (
    DefensiveChallengeRatingResult,
    calculate_monster_defensive_cr,
)
from .offensive import (
    OffensiveChallengeRatingResult,
    calculate_monster_offensive_cr,
)


@dataclass(frozen=True, slots=True)
class ChallengeRatingPolicy:
    """Define how offensive and defensive CR combine.

    Currently follows the previous rules in 5E until rules
    are clarified. This means that offensive and defensive
    CR are equally weighted, and floats are rounded down.
    """

    offensive_weight: float = 0.5
    defensive_weight: float = 0.5
    round_down: bool = True


CHALLENGE_RATING_POLICY = ChallengeRatingPolicy()


@dataclass(kw_only=True, frozen=True, slots=True)
class ChallengeRatingResult:
    """Summarise the complete monster CR calculations.

    Attributes:
        offensive: Offensive CR calculation details
        defensive: Defensive CR calculation details
        average_challenge_rating: Unrounded average CR
        challenge_rating: Final rounded challenge rating

    """

    offensive: OffensiveChallengeRatingResult
    defensive: DefensiveChallengeRatingResult
    average_challenge_rating: float
    challenge_rating: float


def combine_challenge_ratings(
    *,
    offensive_challenge_rating: float,
    defensive_challenge_rating: float,
    reference: ChallengeRatingReference,
) -> tuple[float, float]:
    """Combine offensive and defensive CR into average and final CR.

    Args:
        offensive_challenge_rating: Calculated offensive CR
        defensive_challenge_rating: Calculated defensive CR
        reference: The Challenge rating reference table for adjusting CR

    Returns:
        Unrounded average and final rounded challenge rating.

    Raises:
        ValueError: If either challenge rating is negative.

    """
    if offensive_challenge_rating < 0:
        raise ValueError("Offensive challenge rating cannot be negative")

    if defensive_challenge_rating < 0:
        raise ValueError("Defensive challenge rating cannot be negative")

    policy = CHALLENGE_RATING_POLICY

    average_challenge_rating = (
        offensive_challenge_rating * policy.offensive_weight
        + defensive_challenge_rating * policy.defensive_weight
    )

    if policy.round_down:
        challenge_rating = reference.get_challenge_rating_at_or_below(average_challenge_rating)
    else:
        challenge_rating = min(
            (float(rating) for rating in reference.reference["challenge_rating"].to_list()),
            key=lambda rating: abs(rating - average_challenge_rating),
        )

    return (
        average_challenge_rating,
        challenge_rating,
    )


def calculate_monster_challenge_rating(
    *,
    monster: BaseMonster,
    reference: ChallengeRatingReference,
    rounds: int = 3,
) -> ChallengeRatingResult:
    """Calculate a monster's complete challenge rating."""
    offensive_result = calculate_monster_offensive_cr(
        monster=monster,
        reference=reference,
        legendary=monster.is_legendary,
        rounds=rounds,
    )
    defensive_result = calculate_monster_defensive_cr(
        monster=monster,
        reference=reference,
        rounds=rounds,
    )

    average_challenge_rating, challenge_rating = combine_challenge_ratings(
        offensive_challenge_rating=offensive_result.challenge_rating,
        defensive_challenge_rating=defensive_result.challenge_rating,
        reference=reference,
    )

    return ChallengeRatingResult(
        offensive=offensive_result,
        defensive=defensive_result,
        average_challenge_rating=average_challenge_rating,
        challenge_rating=challenge_rating,
    )
