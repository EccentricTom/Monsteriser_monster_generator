import pytest

from monsteriser_monster_generator.systems.dnd5e.calculations.defensive.armor_class import (
    ArmorClassAdjustmentResult,
    calculate_armor_class_adjustment,
)


@pytest.mark.parametrize(
    ("actual_ac", "expected_ac", "expected_difference", "expected_adjustment"),
    [
        (14, 14, 0, 0),
        (15, 14, 1, 0),
        (16, 14, 2, 1),
        (17, 14, 3, 1),
        (18, 14, 4, 2),
        (13, 14, -1, 0),
        (12, 14, -2, -1),
        (11, 14, -3, -1),
        (10, 14, -4, -2),
    ],
)
def test_calculate_armor_class_adjustment(
    actual_ac: int,
    expected_ac: int,
    expected_difference: int,
    expected_adjustment: int,
) -> None:
    """Adjust defensive CR by one for every two AC points."""
    result = calculate_armor_class_adjustment(
        actual_armor_class=actual_ac, expected_armor_class=expected_ac
    )

    assert result == ArmorClassAdjustmentResult(
        actual_armor_class=actual_ac,
        expected_armor_class=expected_ac,
        difference=expected_difference,
        challenge_rating_adjustment=expected_adjustment,
    )
