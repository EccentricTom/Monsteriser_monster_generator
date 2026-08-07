"""Calculate armor-class adjustments for defensive CR."""

from dataclasses import dataclass


@dataclass(kw_only=True, frozen=True, slots=True)
class ArmorClassAdjustmentResult:
    """Summarise and armor-class defensive CR adjustment.

    Attributes:
        actual_armor_class: Monster's effective armor class.
        expected_armor_class: Expected AC for the HP-derived CR.
        difference: Difference between actual and expected AC.
        challenge_rating_adjustment: CR adjustment caused by AC.

    """

    actual_armor_class: int
    expected_armor_class: int
    difference: int
    challenge_rating_adjustment: int


def calculate_armor_class_adjustment(
    *,
    actual_armor_class: int,
    expected_armor_class: int,
) -> ArmorClassAdjustmentResult:
    """Calculate the defensive CR adjustment caused by armor class."""
    difference = actual_armor_class - expected_armor_class

    challenge_rating_adjustment = int(difference / 2)

    return ArmorClassAdjustmentResult(
        actual_armor_class=actual_armor_class,
        expected_armor_class=expected_armor_class,
        difference=difference,
        challenge_rating_adjustment=challenge_rating_adjustment,
    )
