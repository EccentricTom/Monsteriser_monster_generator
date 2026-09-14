"""Calculate the simplified offensive CR of a D&D 5E 2024 monster."""

from dataclasses import dataclass

from ...models.base_monster import BaseMonster
from ...reference_data import ChallengeRatingReference
from .accuracy import (
    OffensiveAccuracyAdjustment,
    calculate_offensive_accuracy_adjustment,
    calculate_offensive_accuracy_contributions,
    calculate_representative_offensive_accuracies,
    select_offensive_accuracy,
)
from .offensive_damage import (
    OffensiveDamageResult,
    calculate_monster_offensive_damage,
)


@dataclass(kw_only=True, frozen=True, slots=True)
class OffensiveChallengeRatingResult:
    """Summarize the simplified offensive CR calculation.

    Attributes:
        damage_challenge_rating:CR determined by the average damage per round.
        challenge_rating: CR combined with defensive CR.
        damage: Damage result used to determine the CR.
        accuracy: Statistic with value used to adjust offensive CR based on accuracy.

    """

    damage_challenge_rating: float
    challenge_rating: float
    damage: OffensiveDamageResult
    accuracy: OffensiveAccuracyAdjustment | None


def calculate_monster_offensive_cr(
    *,
    monster: BaseMonster,
    reference: ChallengeRatingReference,
    legendary: bool = False,
    rounds: int = 3,
) -> OffensiveChallengeRatingResult:
    """Calculate offensive CR from damage and offensive accuracy.

    Args:
        monster: Monster being evaluated.
        reference: Challenge-rating reference data.
        legendary: Whether to use legendary DPR reference values.
        rounds: Number of rounds in the CR evaluation window.

    Returns:
        Offensive CR and supporting calculation details.

    """
    damage_result = calculate_monster_offensive_damage(
        monster=monster,
        rounds=rounds,
    )

    damage_challenge_rating = reference.get_offensive_cr(
        damage_result.average_damage_per_round,
        legendary=legendary,
    )

    contributions = calculate_offensive_accuracy_contributions(
        monster=monster,
        damage_result=damage_result,
        rounds=rounds,
    )

    representative_accuracies = calculate_representative_offensive_accuracies(
        contributions,
    )

    selected_accuracy = select_offensive_accuracy(
        accuracies=representative_accuracies,
        challenge_rating=damage_challenge_rating,
        reference=reference,
    )

    if selected_accuracy is None:
        return OffensiveChallengeRatingResult(
            damage_challenge_rating=damage_challenge_rating,
            challenge_rating=damage_challenge_rating,
            damage=damage_result,
            accuracy=None,
        )

    if selected_accuracy.accuracy_type == "attack_bonus":
        expected_value = reference.get_expected_attack_bonus(
            challenge_rating=damage_challenge_rating,
        )
    else:
        expected_value = reference.get_expected_save_dc(
            challenge_rating=damage_challenge_rating,
        )

    accuracy_adjustment = calculate_offensive_accuracy_adjustment(
        accuracy_type=selected_accuracy.accuracy_type,
        actual_value=selected_accuracy.value,
        expected_value=expected_value,
    )

    challenge_rating = reference.adjust_challenge_rating(
        challenge_rating=damage_challenge_rating,
        steps=accuracy_adjustment.challenge_rating_steps,
    )

    return OffensiveChallengeRatingResult(
        damage_challenge_rating=damage_challenge_rating,
        challenge_rating=challenge_rating,
        damage=damage_result,
        accuracy=accuracy_adjustment,
    )
