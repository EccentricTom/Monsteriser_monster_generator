"""Calculate offensive accuracy adjustments for D&D 5E 2024 Monsters."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

from ...models.actions import (
    AttackAction,
    LimitedUsage,
    MonsterAction,
    MultiattackAction,
    RechargeUsage,
    SavingThrowAction,
)
from ...models.base_monster import BaseMonster
from ...reference_data import ChallengeRatingReference
from ..combat_routines import TurnRoutine
from ..offensive.damage import (
    calculate_action_average_damage,
    find_maximum_damage_multiattack_routine,
)
from ..offensive.offensive_damage import OffensiveDamageResult

OffensiveAccuracyType = Literal[
    "attack_bonus",
    "save_dc",
]


@dataclass(kw_only=True, frozen=True, slots=True)
class OffensiveAccuracyAdjustment:
    """Summarise an offensive accuracy CR adjustment.

    Attributes:
        accuracy_type: Whether accuracy uses attack bonus or save DC
        actual_value: Monsters attack bonus or save DC.
        expected_value: Expected value for the DPR-derived CR.
        difference: Difference between actual and expected values.
        challenge_rating_steps: CR steps caused by the difference.

    """

    accuracy_type: OffensiveAccuracyType
    actual_value: int
    expected_value: int
    difference: int
    challenge_rating_steps: int


def calculate_offensive_accuracy_adjustment(
    *,
    accuracy_type: OffensiveAccuracyType,
    actual_value: int,
    expected_value: int,
) -> OffensiveAccuracyAdjustment:
    """Calculate CR steps caused by offensive accuracy."""
    difference = actual_value - expected_value

    return OffensiveAccuracyAdjustment(
        accuracy_type=accuracy_type,
        actual_value=actual_value,
        expected_value=expected_value,
        difference=difference,
        challenge_rating_steps=int(difference / 2),
    )


@dataclass(kw_only=True, frozen=True, slots=True)
class OffensiveAccuracy:
    """Represent the accuracy statistic used by an offensive action."""

    accuracy_type: OffensiveAccuracyType
    value: int


def get_action_offensive_accuracy(
    action: MonsterAction,
) -> OffensiveAccuracy | None:
    """Return the offensive accuracy statistic used by an action.

    Args:
        action: Monster action being inspected

    Returns:
        Attack bonus or save DC used by the action, or None if the action does not use either mechanic

    """
    if isinstance(action, AttackAction):
        return OffensiveAccuracy(
            accuracy_type="attack_bonus",
            value=action.attack_bonus,
        )

    if isinstance(action, SavingThrowAction):
        return OffensiveAccuracy(
            accuracy_type="save_dc",
            value=action.difficulty_class,
        )

    return None


@dataclass(kw_only=True, frozen=True, slots=True)
class OffensiveAccuracyContribution:
    """Represent damage associated with one offensive accuracy value."""

    accuracy: OffensiveAccuracy
    damage: float


def get_action_accuracy_contributions(
    *,
    action: MonsterAction,
    actions_by_id: Mapping[str, MonsterAction],
) -> tuple[OffensiveAccuracyContribution, ...]:
    """Return all accuracy contributions produced by an action.

    Args:
        action: Action being evaluated.
        actions_by_id: Monster actions indexed by identifier.

    Returns:
        Accuracy contributions produced by the action.

    """
    if isinstance(action, MultiattackAction):
        return get_multiattack_accuracy_contributions(
            multiattack=action,
            actions_by_id=actions_by_id,
        )

    contribution = get_action_accuracy_contribution(
        action=action,
        actions_by_id=actions_by_id,
    )

    if contribution is None:
        return ()

    return (contribution,)


def get_action_accuracy_contribution(
    *,
    action: MonsterAction,
    actions_by_id: Mapping[str, MonsterAction],
) -> OffensiveAccuracyContribution | None:
    """Return offensive accuracy and damage contributed by an action.

    Args:
        action: Action being evaluated
        actions_by_id: Monster actions indexed by identitier

    Returns:
        Accuracy contribution, or None if the aciton has no relevant offensive
        accuracy or deals no damage.

    """
    accuracy = get_action_offensive_accuracy(action)

    if accuracy is None:
        return None

    damage = calculate_action_average_damage(
        action=action,
        actions_by_id=actions_by_id,
    )
    if damage <= 0:
        return None

    return OffensiveAccuracyContribution(
        accuracy=accuracy,
        damage=damage,
    )


def get_multiattack_accuracy_contributions(
    *,
    multiattack: MultiattackAction,
    actions_by_id: Mapping[str, MonsterAction],
) -> tuple[OffensiveAccuracyContribution, ...]:
    """Return accuracy contribution for the strongest multiattack routine.

    Args:
        multiattack: Multiattack aciton being evaluated
        actions_by_id: Monster actions indexed by identifier

    Returns:
        Tuple for each compenent action in a multiattack along with the accuracy statistic it uses

    """
    maximum_damage_routine, _ = find_maximum_damage_multiattack_routine(
        multiattack=multiattack,
        actions_by_id=actions_by_id,
    )

    contributions: list[OffensiveAccuracyContribution] = []

    for action_id in maximum_damage_routine.action_ids:
        action = actions_by_id[action_id]

        contribution = get_action_accuracy_contribution(
            action=action,
            actions_by_id=actions_by_id,
        )

        if contribution is not None:
            contributions.append(contribution)

    return tuple(contributions)


@dataclass(kw_only=True, frozen=True, slots=True)
class RepresentativeOffensiveAccuracy:
    """Represent the accuracy value used for offensive CR adjustment."""

    accuracy_type: OffensiveAccuracyType
    value: int
    damage: float


def _calculate_representative_accuracy(
    contributions: tuple[OffensiveAccuracyContribution, ...],
    *,
    accuracy_type: OffensiveAccuracyType,
) -> RepresentativeOffensiveAccuracy | None:
    """Calculate damage-weighted accuracy for one accuracy type."""
    selected_contributions = tuple(
        contribution
        for contribution in contributions
        if contribution.accuracy.accuracy_type == accuracy_type
    )

    if not selected_contributions:
        return None

    total_damage = sum(contribution.damage for contribution in selected_contributions)

    weighted_value = (
        sum(
            contribution.accuracy.value * contribution.damage
            for contribution in selected_contributions
        )
        / total_damage
    )

    return RepresentativeOffensiveAccuracy(
        accuracy_type=accuracy_type,
        value=int(weighted_value),
        damage=total_damage,
    )


def calculate_representative_offensive_accuracies(
    contributions: tuple[OffensiveAccuracyContribution, ...],
) -> tuple[RepresentativeOffensiveAccuracy, ...]:
    """Return representative offensive accuracies by damage type."""
    representatives: list[RepresentativeOffensiveAccuracy] = []

    for accuracy_type in ("attack_bonus", "save_dc"):
        representative = _calculate_representative_accuracy(
            contributions, accuracy_type=accuracy_type
        )

        if representative is not None:
            representatives.append(representative)

    return tuple(representatives)


def select_offensive_accuracy(
    *,
    accuracies: tuple[RepresentativeOffensiveAccuracy, ...],
    challenge_rating: float,
    reference: ChallengeRatingReference,
) -> RepresentativeOffensiveAccuracy | None:
    """Select the accuracy statistic used to adjust offensive CR."""
    if not accuracies:
        return None

    maximum_damage = max(accuracy.damage for accuracy in accuracies)

    candidates = tuple(accuracy for accuracy in accuracies if accuracy.damage == maximum_damage)

    if len(candidates) == 1:
        return candidates[0]

    best_accuracy: RepresentativeOffensiveAccuracy | None = None
    best_adjustment: int | None = None

    for accuracy in candidates:
        if accuracy.accuracy_type == "attack_bonus":
            expected_value = reference.get_expected_attack_bonus(challenge_rating=challenge_rating)
        else:
            expected_value = reference.get_expected_save_dc(challenge_rating=challenge_rating)

        adjustment = calculate_offensive_accuracy_adjustment(
            accuracy_type=accuracy.accuracy_type,
            actual_value=accuracy.value,
            expected_value=expected_value,
        )

        if best_adjustment is None or adjustment.challenge_rating_steps > best_adjustment:
            best_accuracy = accuracy
            best_adjustment = adjustment.challenge_rating_steps

    return best_accuracy


def get_turn_routine_accuracy_contributions(
    *,
    routine: TurnRoutine,
    actions_by_id: Mapping[str, MonsterAction],
) -> tuple[OffensiveAccuracyContribution, ...]:
    """Return accuracy contributions for a turn routine."""
    contributions: list[OffensiveAccuracyContribution] = []

    primary_action = actions_by_id[routine.primary_action_id]

    contributions.extend(
        get_action_accuracy_contributions(
            action=primary_action,
            actions_by_id=actions_by_id,
        )
    )

    if routine.bonus_action_id is not None:
        bonus_action = actions_by_id[routine.bonus_action_id]

        contributions.extend(
            get_action_accuracy_contributions(
                action=bonus_action,
                actions_by_id=actions_by_id,
            )
        )

    return tuple(contributions)


def scale_accuracy_contributions(
    contributions: tuple[OffensiveAccuracyContribution, ...],
    *,
    multiplier: float,
) -> tuple[OffensiveAccuracyContribution, ...]:
    """Scale the damage represented by accuracy contributions.

    Args:
        contributions: Accuracy contributions to scale.
        multiplier: Expected number of times the contributions occur.

    Returns:
        Accuracy contributions with scaled damage.

    """
    return tuple(
        OffensiveAccuracyContribution(
            accuracy=contribution.accuracy,
            damage=contribution.damage * multiplier,
        )
        for contribution in contributions
    )


def calculate_offensive_accuracy_contributions(
    *,
    monster: BaseMonster,
    damage_result: OffensiveDamageResult,
    rounds: int = 3,
) -> tuple[OffensiveAccuracyContribution, ...]:
    """Calculate accuracy contributions across the offensive CR window.

    Args:
        monster: Monster being evaluated.
        damage_result: Offensive damage result selected for CR calculation.
        rounds: Number of rounds in the CR evaluation window.

    Returns:
        Expected accuracy contributions across the full CR window.

    Raises:
        ValueError: If rounds is not positive.
        TypeError: If the selected special action has unsupported usage.

    """
    if rounds < 1:
        raise ValueError("Rounds must be positive")

    actions_by_id = monster.get_abilities_by_id()

    fallback_contributions = get_turn_routine_accuracy_contributions(
        routine=damage_result.fallback_routine,
        actions_by_id=actions_by_id,
    )

    if damage_result.special_action_id is None:
        return scale_accuracy_contributions(
            fallback_contributions,
            multiplier=float(rounds),
        )

    special_action = actions_by_id[damage_result.special_action_id]

    special_contributions = get_action_accuracy_contributions(
        action=special_action,
        actions_by_id=actions_by_id,
    )

    if isinstance(special_action.usage, LimitedUsage):
        special_uses = min(
            special_action.usage.uses,
            rounds,
        )
        fallback_uses = rounds - special_uses

        return (
            *scale_accuracy_contributions(
                special_contributions,
                multiplier=float(special_uses),
            ),
            *scale_accuracy_contributions(
                fallback_contributions,
                multiplier=float(fallback_uses),
            ),
        )

    if isinstance(special_action.usage, RechargeUsage):
        expected_special_uses = 1.0 + special_action.usage.recharge_probability * (rounds - 1)

        expected_fallback_uses = (1.0 - special_action.usage.recharge_probability) * (rounds - 1)

        return (
            *scale_accuracy_contributions(
                special_contributions,
                multiplier=expected_special_uses,
            ),
            *scale_accuracy_contributions(
                fallback_contributions,
                multiplier=expected_fallback_uses,
            ),
        )

    raise TypeError("Selected special action must use LimitedUsage or RechargeUsage")
