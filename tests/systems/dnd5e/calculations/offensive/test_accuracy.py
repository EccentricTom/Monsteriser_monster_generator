"""Tests for accuracy.py."""

import pytest

from monsteriser_monster_generator.systems.dnd5e.calculations.offensive.accuracy import (
    OffensiveAccuracy,
    OffensiveAccuracyAdjustment,
    OffensiveAccuracyContribution,
    RepresentativeOffensiveAccuracy,
    calculate_offensive_accuracy_adjustment,
    calculate_representative_offensive_accuracies,
    get_action_accuracy_contribution,
    get_action_offensive_accuracy,
    get_multiattack_accuracy_contributions,
    scale_accuracy_contributions,
    select_offensive_accuracy,
)
from monsteriser_monster_generator.systems.dnd5e.models.actions import (
    AttackAction,
    DamageRoll,
    FixedActionUse,
    MonsterAction,
    MultiattackAction,
    SavingThrowAction,
    SavingThrowDamage,
)
from monsteriser_monster_generator.systems.dnd5e.reference_data import (
    load_challenge_rating_reference,
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


def test_get_attack_accuracy_contribution() -> None:
    """Return attack accuracy weighted by action damage."""
    action = AttackAction(
        name="bite",
        action_id="bite",
        origin="natural",
        attack_range="melee",
        attack_bonus=7,
        damage=(
            DamageRoll(
                dice_count=1,
                die_size=12,
                modifier=2,
                damage_type="piercing",
            ),
        ),
    )

    actions_by_id = {action.action_id: action}

    result = get_action_accuracy_contribution(
        action=action,
        actions_by_id=actions_by_id,
    )

    assert result == OffensiveAccuracyContribution(
        accuracy=OffensiveAccuracy(
            accuracy_type="attack_bonus",
            value=7,
        ),
        damage=8.5,
    )


def test_get_saving_throw_accuracy_contribution() -> None:
    """Return save DC weighted by action damage."""
    action = SavingThrowAction(
        action_id="fire_breath",
        name="Fire Breath",
        origin="natural",
        difficulty_class=15,
        ability="dexterity",
        saving_throw=SavingThrowDamage(
            damage=(
                DamageRoll(
                    dice_count=8,
                    die_size=6,
                    modifier=0,
                    damage_type="fire",
                ),
            ),
            success_outcome="half",
        ),
    )

    actions_by_id = {action.action_id: action}

    result = get_action_accuracy_contribution(
        action=action,
        actions_by_id=actions_by_id,
    )

    assert result == OffensiveAccuracyContribution(
        accuracy=OffensiveAccuracy(
            accuracy_type="save_dc",
            value=15,
        ),
        damage=28.0,
    )


def test_get_non_damaging_accuracy_contribution() -> None:
    """Ignore an accuracy statistic when the action deals no damage."""
    action = SavingThrowAction(
        action_id="fire_breath",
        name="Fire Breath",
        origin="natural",
        difficulty_class=15,
        ability="dexterity",
    )

    result = get_action_accuracy_contribution(
        action=action,
        actions_by_id={action.action_id: action},
    )

    assert result is None


def test_get_action_without_accuracy_contribution() -> None:
    """Ignore actions without an offensive accuracy statistic."""
    action = MonsterAction(
        action_id="misty_step",
        name="Misty Step",
        category="special",
        origin="spell",
    )

    result = get_action_accuracy_contribution(
        action=action,
        actions_by_id={action.action_id: action},
    )

    assert result is None


def test_get_multiattack_accuracy_contributions() -> None:
    """Return accuracy contributions for the strongest multiattack routine."""
    bite = AttackAction(
        action_id="bite",
        name="Bite",
        origin="natural",
        attack_range="melee",
        attack_bonus=7,
        damage=(
            DamageRoll(
                dice_count=1,
                die_size=12,
                modifier=2,
                damage_type="piercing",
            ),
        ),
    )

    claw = AttackAction(
        action_id="claw",
        name="Claw",
        origin="natural",
        attack_range="melee",
        attack_bonus=5,
        damage=(
            DamageRoll(
                dice_count=1,
                die_size=6,
                modifier=2,
                damage_type="slashing",
            ),
        ),
    )

    multiattack = MultiattackAction(
        action_id="multiattack",
        name="Multiattack",
        origin="natural",
        steps=(
            FixedActionUse(
                action_id="bite",
                count=2,
            ),
            FixedActionUse(
                action_id="claw",
            ),
        ),
    )

    actions_by_id: dict[str, MonsterAction] = {
        bite.action_id: bite,
        claw.action_id: claw,
        multiattack.action_id: multiattack,
    }

    result = get_multiattack_accuracy_contributions(
        multiattack=multiattack,
        actions_by_id=actions_by_id,
    )

    assert result == (
        OffensiveAccuracyContribution(
            accuracy=OffensiveAccuracy(
                accuracy_type="attack_bonus",
                value=7,
            ),
            damage=8.5,
        ),
        OffensiveAccuracyContribution(
            accuracy=OffensiveAccuracy(
                accuracy_type="attack_bonus",
                value=7,
            ),
            damage=8.5,
        ),
        OffensiveAccuracyContribution(
            accuracy=OffensiveAccuracy(
                accuracy_type="attack_bonus",
                value=5,
            ),
            damage=5.5,
        ),
    )


def test_select_offensive_accuracy_breaks_damage_tie_by_cr_adjustment() -> None:
    """Use the stronger CR adjustment when damage contributions tie."""
    accuracies = (
        RepresentativeOffensiveAccuracy(
            accuracy_type="attack_bonus",
            value=7,
            damage=20.0,
        ),
        RepresentativeOffensiveAccuracy(
            accuracy_type="save_dc",
            value=13,
            damage=20.0,
        ),
    )

    result = select_offensive_accuracy(
        accuracies=accuracies,
        challenge_rating=1.0,
        reference=load_challenge_rating_reference(),
    )

    assert result == accuracies[0]


def test_calculate_representative_offensive_accuracies() -> None:
    """Calculate damage-weighted representatives for each accuracy type."""
    contributions = (
        OffensiveAccuracyContribution(
            accuracy=OffensiveAccuracy(
                accuracy_type="attack_bonus",
                value=8,
            ),
            damage=12.0,
        ),
        OffensiveAccuracyContribution(
            accuracy=OffensiveAccuracy(
                accuracy_type="attack_bonus",
                value=6,
            ),
            damage=6.0,
        ),
        OffensiveAccuracyContribution(
            accuracy=OffensiveAccuracy(
                accuracy_type="save_dc",
                value=15,
            ),
            damage=20.0,
        ),
        OffensiveAccuracyContribution(
            accuracy=OffensiveAccuracy(
                accuracy_type="save_dc",
                value=13,
            ),
            damage=10.0,
        ),
    )

    result = calculate_representative_offensive_accuracies(
        contributions,
    )

    assert result == (
        RepresentativeOffensiveAccuracy(
            accuracy_type="attack_bonus",
            value=7,
            damage=18.0,
        ),
        RepresentativeOffensiveAccuracy(
            accuracy_type="save_dc",
            value=14,
            damage=30.0,
        ),
    )


def test_calculate_representative_offensive_accuracies_returns_empty_tuple() -> None:
    """Return no representatives when there are no contributions."""
    assert calculate_representative_offensive_accuracies(()) == ()


def test_scale_accuracy_contributions() -> None:
    """Scale contribution damage by expected usage."""
    contributions = (
        OffensiveAccuracyContribution(
            accuracy=OffensiveAccuracy(
                accuracy_type="attack_bonus",
                value=7,
            ),
            damage=8.0,
        ),
    )

    result = scale_accuracy_contributions(
        contributions,
        multiplier=2.5,
    )

    assert result == (
        OffensiveAccuracyContribution(
            accuracy=OffensiveAccuracy(
                accuracy_type="attack_bonus",
                value=7,
            ),
            damage=20.0,
        ),
    )


def test_get_action_accuracy_contributions_expands_multiattack() -> None:
    """Return individual contributions from a multiattack action."""
    ...
