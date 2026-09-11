import pytest

from monsteriser_monster_generator.systems.dnd5e.calculations.offensive.accuracy import (
    OffensiveAccuracy,
    OffensiveAccuracyAdjustment,
    calculate_offensive_accuracy_adjustment,
    get_action_offensive_accuracy,
)
from monsteriser_monster_generator.systems.dnd5e.models.actions import (
    AttackAction,
    MonsterAction,
    SavingThrowAction,
)


@pytest.mark.parametrize(
    ("actual", "expected", "difference", "expected_steps"),
    [
        (5, 5, 0, 0),
        (6, 5, 1, 0),
        (7, 5, 2, 1),
        (8, 5, 3, 1),
        (9, 5, 4, 2),
        (4, 5, -1, 0),
        (3, 5, -2, -1),
        (2, 5, -3, -1),
        (1, 5, -4, -2),
    ],
)
def test_calculate_offensive_accuracy_adjustment(
    actual: int,
    expected: int,
    difference: int,
    expected_steps: int,
) -> None:
    """Adjust Offensive CR one step for every two accuracy points."""
    result = calculate_offensive_accuracy_adjustment(
        accuracy_type="attack_bonus", actual_value=actual, expected_value=expected
    )

    assert result == OffensiveAccuracyAdjustment(
        accuracy_type="attack_bonus",
        actual_value=actual,
        expected_value=expected,
        difference=difference,
        challenge_rating_steps=expected_steps,
    )


def test_calculate_offensive_accuracy_adjustment_supports_save_dc() -> None:
    """Use save DC as the offensive accuracy statistic."""
    result = calculate_offensive_accuracy_adjustment(
        accuracy_type="save_dc",
        actual_value=15,
        expected_value=13,
    )

    assert result.accuracy_type == "save_dc"
    assert result.challenge_rating_steps == 1


def test_get_attack_action_offensive_accuracy() -> None:
    """Return attack bonus for an attack action."""
    action = AttackAction(
        name="bite",
        action_id="bite",
        origin="natural",
        attack_range="melee",
        attack_bonus=7,
        damage=(),
    )

    assert get_action_offensive_accuracy(action) == OffensiveAccuracy(
        accuracy_type="attack_bonus",
        value=7,
    )


def test_get_saving_throw_action_offensive_accuracy() -> None:
    """Return save DC for a saving throw action."""
    action = SavingThrowAction(
        action_id="fire_breath",
        name="Fire Breath",
        origin="natural",
        difficulty_class=15,
        ability="dexterity",
    )

    assert get_action_offensive_accuracy(action) == OffensiveAccuracy(
        accuracy_type="save_dc", value=15
    )


def test_get_none_offensive_accuracy() -> None:
    """Return None for an action that has neither an attack bonus or save DC."""
    action = MonsterAction(
        action_id="misty_step",
        name="Misty Step",
        category="special",
        origin="spell",
    )

    assert get_action_offensive_accuracy(action) is None
