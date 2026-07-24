"""Test the validation of D&D 5E 2024 Multiattack definitions."""

from pytest import raises

from monsteriser_monster_generator.systems.dnd5e.models.actions import (
    ActionSubstitution,
    AttackAction,
    ChoiceActionUse,
    DamageRoll,
    FixedActionUse,
    MonsterAction,
    MultiattackAction,
)
from monsteriser_monster_generator.systems.dnd5e.models.base_monster import BaseMonster
from monsteriser_monster_generator.systems.dnd5e.models.model_types import (
    ActionTiming,
)
from monsteriser_monster_generator.systems.dnd5e.services.multiattack_validation import (
    validate_monster_multiattacks,
)


def create_attack(*, action_id: str, timing: ActionTiming = "action") -> AttackAction:
    """Create a minimal attack for validation tests.

    Args:
        action_id: Unique identifier for the attack.
        timing: Action-economy timing of the attack.

    Returns:
        Minimal configured attack.

    """
    return AttackAction(
        action_id=action_id,
        name=action_id.replace("_", " ").title(),
        origin="natural",
        attack_range="melee",
        attack_bonus=5,
        reach_ft=5,
        timing=timing,
        damage=(
            DamageRoll(
                dice_count=1,
                die_size=6,
                modifier=3,
                damage_type="slashing",
            ),
        ),
    )


def test_validate_monster_multiattacks_accepts_valid_multiattack() -> None:
    """Accept a multiatack whose references are valid attacks."""
    bite = create_attack(action_id="bite")
    claw = create_attack(action_id="claw")

    multiattack = MultiattackAction(
        action_id="multiattack",
        name="Multiattack",
        origin="natural",
        steps=(
            FixedActionUse(action_id="bite"),
            FixedActionUse(action_id="claw"),
        ),
    )

    monster = BaseMonster(
        name="Wolf",
        abilities=[
            bite,
            claw,
            multiattack,
        ],
    )

    validate_monster_multiattacks(monster)


def test_validate_monster_multiattacks_accepts_valid_substitution() -> None:
    """Accept a substitution that references valid attacks."""
    bite = create_attack(action_id="bite")
    claw = create_attack(action_id="claw")
    tail = create_attack(action_id="tail")

    multiattack = MultiattackAction(
        action_id="multiattack",
        name="Multiattack",
        origin="natural",
        steps=(
            FixedActionUse(action_id="bite"),
            FixedActionUse(action_id="claw"),
        ),
        substitutions=(
            ActionSubstitution(
                replaced_action_id="claw",
                replacement_action_ids=("tail",),
                maximum_replacements=1,
            ),
        ),
    )

    monster = BaseMonster(
        name="Wolf",
        abilities=[
            bite,
            claw,
            tail,
            multiattack,
        ],
    )

    validate_monster_multiattacks(monster)


def test_validate_monster_multiattacks_accepts_monster_no_multiattack() -> None:
    """Accept a monster with no multiattack."""
    bite = create_attack(action_id="bite")

    monster = BaseMonster(
        name="Wolf",
        abilities=[
            bite,
        ],
    )

    validate_monster_multiattacks(monster)


def test_validate_monster_multiattack_rejects_unknown_base_action() -> None:
    """Reject an unknown action in the base sequence."""
    bite = create_attack(action_id="bite")

    multiattack = MultiattackAction(
        action_id="multiattack",
        name="Multiattack",
        origin="natural",
        steps=(
            FixedActionUse(action_id="bite"),
            FixedActionUse(action_id="missing_claw"),
        ),
    )

    monster = BaseMonster(
        name="Invalid Wolf",
        abilities=[
            bite,
            multiattack,
        ],
    )

    with raises(
        ValueError,
        match="Multiattack references unknown actions: missing_claw",
    ):
        validate_monster_multiattacks(monster)


def test_validate_monster_multiattack_rejects_unknown_replaced_action() -> None:
    """Reject an unknown action targeted by a substitution."""
    bite = create_attack(action_id="bite")
    tail = create_attack(action_id="tail")

    multiattack = MultiattackAction(
        action_id="multiattack",
        name="Multiattack",
        origin="natural",
        steps=(FixedActionUse(action_id="bite"),),
        substitutions=(
            ActionSubstitution(
                replaced_action_id="missing_claw",
                replacement_action_ids=("tail",),
            ),
        ),
    )

    monster = BaseMonster(
        name="Invalid Wolf",
        abilities=[
            bite,
            tail,
            multiattack,
        ],
    )

    with raises(
        ValueError,
        match="Multiattack references unknown actions: missing_claw",
    ):
        validate_monster_multiattacks(monster)


def test_validate_monster_multiattack_rejects_unknown_replacement() -> None:
    """Reject an unknown replacement action."""
    bite = create_attack(action_id="bite")
    claw = create_attack(action_id="claw")

    multiattack = MultiattackAction(
        action_id="multiattack",
        name="Multiattack",
        origin="natural",
        steps=(
            FixedActionUse(action_id="bite"),
            FixedActionUse(action_id="claw"),
        ),
        substitutions=(
            ActionSubstitution(
                replaced_action_id="claw",
                replacement_action_ids=("missing_tail",),
            ),
        ),
    )

    monster = BaseMonster(
        name="Invalid Wolf",
        abilities=[
            bite,
            claw,
            multiattack,
        ],
    )

    with raises(
        ValueError,
        match="Multiattack references unknown actions: missing_tail",
    ):
        validate_monster_multiattacks(monster)


def test_validate_monster_multiattacks_lists_all_unknown_actions() -> None:
    """Report all missing action references in sorted order."""
    bite = create_attack(action_id="bite")

    multiattack = MultiattackAction(
        action_id="multiattack",
        name="Multiattack",
        origin="natural",
        steps=(
            FixedActionUse(action_id="missing_tentacle"),
            FixedActionUse(action_id="bite"),
        ),
        substitutions=(
            ActionSubstitution(
                replaced_action_id="missing_claw",
                replacement_action_ids=("missing_tail",),
            ),
        ),
    )

    monster = BaseMonster(
        name="Invalide Tentacled Wolf",
        abilities=[
            bite,
            multiattack,
        ],
    )

    with raises(
        ValueError,
        match=(
            "Multiattack references unknown actions: missing_claw, missing_tail, missing_tentacle"
        ),
    ):
        validate_monster_multiattacks(monster)


def test_validate_monster_multiattacks_rejects_self_reference() -> None:
    """Reject a Multiattack that references itself."""
    multiattack = MultiattackAction(
        action_id="multiattack",
        name="Multiattack",
        origin="natural",
        steps=(FixedActionUse(action_id="multiattack"),),
    )

    monster = BaseMonster(
        name="Invalid Wolf",
        abilities=[multiattack],
    )

    with raises(
        ValueError,
        match="Multiattack cannot reference itself",
    ):
        validate_monster_multiattacks(monster)


def test_validate_monster_multiattacks_accepts_non_damage_action() -> None:
    """Allow a normal non-damaging action inside Multiattack."""
    dominate_mind = MonsterAction(
        action_id="dominate_mind",
        name="Dominate Mind",
        category="special",
        origin="special",
        timing="action",
    )

    multiattack = MultiattackAction(
        action_id="multiattack",
        name="Multiattack",
        origin="natural",
        steps=(
            FixedActionUse(
                action_id="dominate_mind",
            ),
        ),
    )

    monster = BaseMonster(
        name="Aboleth",
        abilities=[
            dominate_mind,
            multiattack,
        ],
    )

    validate_monster_multiattacks(monster)


def test_validate_monster_multiattacks_accepts_non_attack_replacement() -> None:
    """Allow a substitution replacement that is not an attack."""
    bite = create_attack(action_id="bite")

    teleport = MonsterAction(
        action_id="teleport",
        name="Teleport",
        category="special",
        origin="special",
    )

    multiattack = MultiattackAction(
        action_id="multiattack",
        name="Multiattack",
        origin="natural",
        steps=(
            FixedActionUse(
                action_id="bite",
            ),
        ),
        substitutions=(
            ActionSubstitution(
                replaced_action_id="bite",
                replacement_action_ids=("teleport",),
            ),
        ),
    )

    monster = BaseMonster(
        name="Teleporting Wolf",
        abilities=[
            bite,
            teleport,
            multiattack,
        ],
    )

    validate_monster_multiattacks(monster)


def test_validate_monster_multiattacks_validates_every_multiattack() -> None:
    """Validate every multiattack belonging to a monster."""
    bite = create_attack(action_id="bite")
    claw = create_attack(action_id="claw")

    valid_multiattack = MultiattackAction(
        action_id="multiattack-standard",
        name="Standard Multiattack",
        origin="natural",
        steps=(
            FixedActionUse(action_id="bite"),
            FixedActionUse(action_id="claw"),
        ),
    )

    invalid_multiattack = MultiattackAction(
        action_id="multiattack_invalid",
        name="Invalid Multiattack",
        origin="natural",
        steps=(FixedActionUse(action_id="missing_tail"),),
    )

    monster = BaseMonster(
        name="Complex Wolf",
        abilities=[
            bite,
            claw,
            valid_multiattack,
            invalid_multiattack,
        ],
    )
    with raises(
        ValueError,
        match="Multiattack references unknown actions: missing_tail",
    ):
        validate_monster_multiattacks(monster)


def test_validate_monster_multiattacks_accepts_choice_actions() -> None:
    """Allow all valid alternatives in a choice step."""
    tentacle = create_attack(action_id="tentacle")

    dominate_mind = MonsterAction(
        action_id="dominate_mind",
        name="Dominate Mind",
        category="special",
        origin="special",
        timing="action",
    )

    consume_memories = create_attack(action_id="consume_memories")

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

    monster = BaseMonster(
        name="Aboleth",
        abilities=[
            tentacle,
            dominate_mind,
            consume_memories,
            multiattack,
        ],
    )

    validate_monster_multiattacks(monster)


def test_validate_monster_multiattacks_rejects_unknown_choice_action() -> None:
    """Reject an unknown action inside a choice step."""
    tentacle = create_attack(action_id="tentacle")

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
                    "missing_consume_memories",
                ),
            ),
        ),
    )

    monster = BaseMonster(
        name="Invalid Aboleth",
        abilities=[
            tentacle,
            multiattack,
        ],
    )

    with raises(
        ValueError,
        match=("Multiattack references unknown actions: dominate_mind, missing_consume_memories"),
    ):
        validate_monster_multiattacks(monster)


def test_validate_monster_multiattacks_rejects_nested_multiattack() -> None:
    """Reject a Multiattack that references another Multiattack."""
    bite = create_attack(action_id="bite")

    inner_multiattack = MultiattackAction(
        action_id="inner_multiattack",
        name="Inner Multiattack",
        origin="natural",
        steps=(
            FixedActionUse(
                action_id="bite",
            ),
        ),
    )

    outer_multiattack = MultiattackAction(
        action_id="outer_multiattack",
        name="Outer Multiattack",
        origin="natural",
        steps=(
            FixedActionUse(
                action_id="inner_multiattack",
            ),
        ),
    )

    monster = BaseMonster(
        name="Recursive Creature",
        abilities=[
            bite,
            inner_multiattack,
            outer_multiattack,
        ],
    )

    with raises(
        ValueError,
        match=("Multiattack cannot reference another Multiattack: inner_multiattack"),
    ):
        validate_monster_multiattacks(monster)


def test_validate_monster_multiattacks_rejects_bonus_action() -> None:
    """Reject a bonus action referenced inside Multiattack."""
    quick_bite = create_attack(
        action_id="quick_bite",
        timing="bonus_action",
    )

    multiattack = MultiattackAction(
        action_id="multiattack",
        name="Multiattack",
        origin="natural",
        steps=(
            FixedActionUse(
                action_id="quick_bite",
            ),
        ),
    )

    monster = BaseMonster(
        name="Invalid Predator",
        abilities=[
            quick_bite,
            multiattack,
        ],
    )

    with raises(
        ValueError,
        match=("Multiattack may only reference action-timing abilities: quick_bite"),
    ):
        validate_monster_multiattacks(monster)
