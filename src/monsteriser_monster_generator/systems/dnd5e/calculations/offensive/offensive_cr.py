"""Calculate the simplified offensive CR of a D&D 5E 2024 monster."""

from dataclasses import dataclass

from ...models.base_monster import BaseMonster
from ...reference_data import ChallengeRatingReference
from .offensive_damage import (
    OffensiveDamageResult,
    calculate_monster_offensive_damage,
)


@dataclass(kw_only=True, frozen=True, slots=True)
class OffensiveChallengeRatingResult:
    """Summarize the simplified offensive CR calculation.

    Attributes:
        challenge_rating: CR determined by the average damage per round.
        damage: Damage result used to determine the CR.

    """

    challenge_rating: int
    damage: OffensiveDamageResult


def calculate_monster_offensive_cr(
    *,
    monster: BaseMonster,
    reference: ChallengeRatingReference,
    legendary: bool = False,
    rounds: int = 3,
) -> OffensiveChallengeRatingResult:
    """Calculate offensive CR from the monster's average damage.

    Args:
        monster: Monster being evaluated.
        reference: Challenge rating reference data.
        legendary: Whether to use base or legendary dpr bands.
        rounds: Number of rounds in the damage evaluation window.

    Returns:
        Offensive CR and the damage result used to determine it.

    Raises:
        ValueError: If the damage window is invalid, the monster has no
        repeatable turn, or its DPR falls outside the reference.

    """
    damage_result = calculate_monster_offensive_damage(
        monster=monster,
        rounds=rounds,
    )

    challenge_rating = reference.get_offensive_cr(
        damage_result.average_damage_per_round,
        legendary=legendary,
    )

    return OffensiveChallengeRatingResult(
        challenge_rating=challenge_rating,
        damage=damage_result,
    )
