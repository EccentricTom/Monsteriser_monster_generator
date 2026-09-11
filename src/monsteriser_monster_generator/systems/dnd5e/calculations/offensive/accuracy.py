"""Calculate offensive accuracy adjustments for D&D 5E 2024 Monsters."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

from ...models.actions import AttackAction, MonsterAction, MultiattackAction, SavingThrowAction
from ..offensive.damage import (
    calculate_action_average_damage,
    find_maximum_damage_multiattack_routine,
)

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


def calculate_representative_offensive_accuracy(
    contributions: tuple[OffensiveAccuracyContribution, ...],
) -> RepresentativeOffensiveAccuracy | None:
    """Calculate the representative offensive accuracy.

    Args:
        contributions: Damage contributions associated with attack bonuses or save DCs

    Returns:
        Representative offensive accuracy, or None when no damaging accuracy contributions exist.

    """
    if not contributions:
        return None

    damage_by_type: dict[OffensiveAccuracyType, float] = {"attack_bonus": 0.0, "save_dc": 0.0}

    for contribution in contributions:
        damage_by_type[contribution.accuracy.accuracy_type] += contribution.damage

    accuracy_type = max(
        damage_by_type,
        key=lambda key: damage_by_type[key],
    )

    selected_contributions = tuple(
        contribution
        for contribution in contributions
        if contribution.accuracy.accuracy_type == accuracy_type
    )

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
