"""Test D&D 5e Multiattack models."""

import pytest

from monsteriser_monster_generator.systems.dnd5e.models.actions import (
    ActionSubstitution,
    ChoiceActionUse,
    FixedActionUse,
    MultiattackAction,
    MultiattackRoutine,
)


def test_fixed_action_use_defaults_to_one_use() -> None:
    """Default a fixed Multiattack step to one ability use."""
    step = FixedActionUse(
        action_id="bite",
    )

    assert step.action_id == "bite"
    assert step.count == 1


def test_fixed_action_use_accepts_repeated_uses() -> None:
    """Allow a fixed ability to be used multiple times."""
    step = FixedActionUse(
        action_id="claw",
        count=3,
    )

    assert step.count == 3


def test_fixed_action_use_rejects_zero_uses() -> None:
    """Reject a fixed step that never uses its ability."""
    with pytest.raises(
        ValueError,
        match="Fixed action-use count must be positive",
    ):
        FixedActionUse(
            action_id="claw",
            count=0,
        )


def test_fixed_action_use_rejects_negative_uses() -> None:
    """Reject a negative fixed-action count."""
    with pytest.raises(
        ValueError,
        match="Fixed action-use count must be positive",
    ):
        FixedActionUse(
            action_id="claw",
            count=-1,
        )


def test_choice_action_use_accepts_multiple_options() -> None:
    """Store all alternatives available to a choice step."""
    step = ChoiceActionUse(
        action_ids=(
            "dominate_mind",
            "consume_memories",
        ),
    )

    assert step.action_ids == (
        "dominate_mind",
        "consume_memories",
    )
    assert step.count == 1


def test_choice_action_use_accepts_repeated_uses() -> None:
    """Allow the selected ability to be used repeatedly."""
    step = ChoiceActionUse(
        action_ids=(
            "claw",
            "bite",
        ),
        count=2,
    )

    assert step.count == 2


def test_choice_action_use_rejects_empty_options() -> None:
    """Reject a choice step without any alternatives."""
    with pytest.raises(
        ValueError,
        match="A Multiattack choice requires at least one action",
    ):
        ChoiceActionUse(
            action_ids=(),
        )


def test_choice_action_use_rejects_zero_uses() -> None:
    """Reject a choice step with a zero count."""
    with pytest.raises(
        ValueError,
        match="Choice action-use count must be positive",
    ):
        ChoiceActionUse(
            action_ids=("bite",),
            count=0,
        )


def test_multiattack_accepts_mixed_step_types() -> None:
    """Allow fixed and choice steps in one Multiattack."""
    multiattack = MultiattackAction(
        action_id="multiattack",
        name="Multiattack",
        origin="natural",
        steps=(
            FixedActionUse(
                action_id="tentacle",
                count=2,
            ),
            ChoiceActionUse(
                action_ids=(
                    "dominate_mind",
                    "consume_memories",
                ),
            ),
        ),
    )

    assert multiattack.steps == (
        FixedActionUse(
            action_id="tentacle",
            count=2,
        ),
        ChoiceActionUse(
            action_ids=(
                "dominate_mind",
                "consume_memories",
            ),
        ),
    )


def test_multiattack_rejects_empty_steps() -> None:
    """Reject a Multiattack without any component steps."""
    with pytest.raises(
        ValueError,
        match="Multiattack must contain at least one step",
    ):
        MultiattackAction(
            action_id="multiattack",
            name="Multiattack",
            origin="natural",
            steps=(),
        )


def test_valid_routiens_expands_fixed_steps() -> None:
    """Expand repeated fixed steps into one concrete sequence."""
    multiattack = MultiattackAction(
        action_id="multiattack",
        name="Multiattack",
        origin="natural",
        steps=(
            FixedActionUse(action_id="bite"),
            FixedActionUse(
                action_id="claw",
                count=2,
            ),
        ),
    )

    result = multiattack.valid_routines()

    assert result == (
        MultiattackRoutine(
            action_ids=(
                "bite",
                "claw",
                "claw",
            ),
        ),
    )


def test_valid_routines_preserves_step_order() -> None:
    """Preserve the order of separate fixed steps."""
    multiattack = MultiattackAction(
        action_id="multiattack",
        name="Multiattack",
        origin="natural",
        steps=(
            FixedActionUse(action_id="bite"),
            FixedActionUse(action_id="claw"),
            FixedActionUse(action_id="bite"),
        ),
    )

    result = multiattack.valid_routines()

    assert result == (
        MultiattackRoutine(
            action_ids=(
                "bite",
                "claw",
                "bite",
            ),
        ),
    )


def test_valid_routines_expands_choice_step() -> None:
    """Generate one routine for each choice-step alternative."""
    multiattack = MultiattackAction(
        action_id="multiattack",
        name="Multiattack",
        origin="natural",
        steps=(
            FixedActionUse(
                action_id="tentacle",
                count=2,
            ),
            ChoiceActionUse(
                action_ids=(
                    "consume_memories",
                    "dominate_mind",
                ),
            ),
        ),
    )

    result = multiattack.valid_routines()

    assert result == (
        MultiattackRoutine(
            action_ids=(
                "tentacle",
                "tentacle",
                "consume_memories",
            ),
        ),
        MultiattackRoutine(
            action_ids=(
                "tentacle",
                "tentacle",
                "dominate_mind",
            ),
        ),
    )


def test_valid_routines_expands_multiple_choice_steps() -> None:
    """Generate the Cartesian product of multiple choice steps."""
    multiattack = MultiattackAction(
        action_id="multiattack",
        name="Multiattack",
        origin="natural",
        steps=(
            ChoiceActionUse(
                action_ids=(
                    "bite",
                    "claw",
                ),
            ),
            ChoiceActionUse(
                action_ids=(
                    "tail",
                    "slam",
                ),
            ),
        ),
    )

    result = multiattack.valid_routines()

    assert result == (
        MultiattackRoutine(
            action_ids=(
                "bite",
                "slam",
            ),
        ),
        MultiattackRoutine(
            action_ids=(
                "bite",
                "tail",
            ),
        ),
        MultiattackRoutine(
            action_ids=(
                "claw",
                "slam",
            ),
        ),
        MultiattackRoutine(
            action_ids=(
                "claw",
                "tail",
            ),
        ),
    )


def test_valid_routines_repeats_selected_choice() -> None:
    """Repeat the selected choice according to the step count."""
    multiattack = MultiattackAction(
        action_id="multiattack",
        name="Multiattack",
        origin="natural",
        steps=(
            ChoiceActionUse(
                action_ids=(
                    "claw",
                    "bite",
                ),
                count=2,
            ),
        ),
    )

    result = multiattack.valid_routines()

    assert result == (
        MultiattackRoutine(
            action_ids=(
                "bite",
                "bite",
            ),
        ),
        MultiattackRoutine(
            action_ids=(
                "claw",
                "claw",
            ),
        ),
    )


def test_valid_routines_applies_substitution_after_step_expansion() -> None:
    """Apply substitution to the expanded fixed sequence."""
    multiattack = MultiattackAction(
        action_id="multiattack",
        name="Multiattack",
        origin="natural",
        steps=(
            FixedActionUse(
                action_id="claw",
                count=3,
            ),
        ),
        substitutions=(
            ActionSubstitution(
                replaced_action_id="claw",
                replacement_action_ids=("bite",),
                maximum_replacements=1,
            ),
        ),
    )

    result = multiattack.valid_routines()

    assert result == (
        MultiattackRoutine(
            action_ids=(
                "bite",
                "claw",
                "claw",
            ),
        ),
        MultiattackRoutine(
            action_ids=(
                "claw",
                "bite",
                "claw",
            ),
        ),
        MultiattackRoutine(
            action_ids=(
                "claw",
                "claw",
                "bite",
            ),
        ),
        MultiattackRoutine(
            action_ids=(
                "claw",
                "claw",
                "claw",
            ),
        ),
    )


def test_valid_routine_applies_subtitution_to_choice_routines() -> None:
    """Apply substitutions to every sequence generated by choices."""
    multiattack = MultiattackAction(
        action_id="multiattack",
        name="Multiattack",
        origin="natural",
        steps=(
            ChoiceActionUse(
                action_ids=(
                    "claw",
                    "slam",
                ),
            ),
            FixedActionUse(
                action_id="claw",
            ),
        ),
        substitutions=(
            ActionSubstitution(
                replaced_action_id="claw",
                replacement_action_ids=("bite",),
                maximum_replacements=1,
            ),
        ),
    )

    result = multiattack.valid_routines()

    assert result == (
        MultiattackRoutine(
            action_ids=(
                "bite",
                "claw",
            ),
        ),
        MultiattackRoutine(
            action_ids=(
                "claw",
                "bite",
            ),
        ),
        MultiattackRoutine(
            action_ids=(
                "claw",
                "claw",
            ),
        ),
        MultiattackRoutine(
            action_ids=(
                "slam",
                "bite",
            ),
        ),
        MultiattackRoutine(
            action_ids=(
                "slam",
                "claw",
            ),
        ),
    )
