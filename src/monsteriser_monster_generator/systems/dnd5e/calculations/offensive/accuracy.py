"""Calculate offensive accuracy adjustments for D&D 5E 2024 Monsters."""

from dataclasses import dataclass
from typing import Literal

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
