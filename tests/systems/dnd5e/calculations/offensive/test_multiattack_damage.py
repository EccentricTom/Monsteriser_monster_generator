"""Calculate the raw average damage for D&D 5E 2024 monster actions for Multiattacks."""

from monsteriser_monster_generator.systems.dnd5e.calculations import (
    calculate_action_average_damage,
    calculate_multiattack_routine_damage,
    find_maximum_damage_multiattack_routine,
)
from monsteriser_monster_generator.systems.dnd5e.models.actions import (
    ActionSubstitution,
    AttackAction,
    ChoiceActionUse,
    DamageRoll,
    FixedActionUse,
    MonsterAction,
    MultiattackAction,
    MultiattackRoutine,
    SavingThrowAction,
    SavingThrowDamage,
)
from monsteriser_monster_generator.systems.dnd5e.models.model_types import (
    ActionTiming,
)


def create_attack(
    *,
    action_id: str,
    dice_count: int = 1,
    die_size: int = 4,
    modifier: int = 0,
    timing: ActionTiming = "action",
) -> AttackAction:
    """Create a configured attack for damage tests.

    Args:
        action_id: Unique identifier for the attack action.
        dice_count: the number of damage dice.
        die_size: the size of the damage dice, between 4 and 20.
        modifier: the flat damage modifier.
        timing: Action economy timing of the attack, either action or bonus_action

    Returns:
        A configured melee attack.

    """
    return AttackAction(
        action_id=action_id,
        name=action_id.replace("_", " ").title(),
        origin="natural",
        timing=timing,
        attack_range="melee",
        attack_bonus=5,
        reach_ft=5,
        damage=(
            DamageRoll(
                dice_count=dice_count,
                die_size=die_size,
                modifier=modifier,
                damage_type="slashing",
            ),
        ),
    )


def test_calculate_multiattack_routine_damage_for_attacks() -> None:
    """Add damage from every attack in a Multiattack routine."""
    bite = create_attack(
        action_id="bite",
        dice_count=1,
        die_size=8,
        modifier=3,
    )
    claw = create_attack(
        action_id="claw",
        dice_count=1,
        die_size=6,
        modifier=2,
    )

    actions_by_id: dict[str, MonsterAction] = {
        bite.action_id: bite,
        claw.action_id: claw,
    }

    routine = MultiattackRoutine(
        action_ids=(
            "bite",
            "claw",
            "claw",
        ),
    )

    result = calculate_multiattack_routine_damage(
        routine=routine,
        actions_by_id=actions_by_id,
    )

    assert result == 18.5


def test_calculate_multiattack_routine_damage_ignores_non_damage_action() -> None:
    """Treat a non-damaging ability as zero raw damage."""
    tentacle = create_attack(
        action_id="tentacle",
        dice_count=2,
        die_size=6,
        modifier=3,
    )

    dominate_mind = MonsterAction(
        action_id="dominate_mind",
        name="Dominate Mind",
        category="special",
        origin="special",
    )

    actions_by_id: dict[str, MonsterAction] = {
        tentacle.action_id: tentacle,
        dominate_mind.action_id: dominate_mind,
    }

    routine = MultiattackRoutine(
        action_ids=(
            "tentacle",
            "tentacle",
            "dominate_mind",
        ),
    )

    result = calculate_multiattack_routine_damage(
        routine=routine,
        actions_by_id=actions_by_id,
    )

    assert result == 20.0


def test_calculate_multiattack_routine_damage_includes_saving_throw_action() -> None:
    """Include saving-throw damage in a Multiattack routine."""
    tentacle = create_attack(
        action_id="tentacle",
        dice_count=2,
        die_size=6,
        modifier=3,
    )

    consume_memories = SavingThrowAction(
        action_id="consume_memories",
        name="Consume Memories",
        origin="special",
        target_description="one creature within 60 feet.",
        saving_throw=SavingThrowDamage(
            ability="wisdom",
            difficulty_class=15,
            damage=(
                DamageRoll(
                    dice_count=4,
                    die_size=8,
                    modifier=0,
                    damage_type="psychic",
                ),
            ),
        ),
        expected_targets=1.0,
    )

    actions_by_id: dict[str, MonsterAction] = {
        tentacle.action_id: tentacle,
        consume_memories.action_id: consume_memories,
    }

    routine = MultiattackRoutine(
        action_ids=(
            "tentacle",
            "tentacle",
            "consume_memories",
        ),
    )

    result = calculate_multiattack_routine_damage(
        routine=routine,
        actions_by_id=actions_by_id,
    )

    assert result == 38.0


def test_calculate_action_average_damage_for_multiattack() -> None:
    """Return damage from the strongest legal Multiattack routine."""
    bite = create_attack(
        action_id="bite",
        dice_count=1,
        die_size=8,
        modifier=3,
    )

    claw = create_attack(
        action_id="claw",
        dice_count=1,
        die_size=6,
        modifier=3,
    )

    multiattack = MultiattackAction(
        action_id="multiattack",
        name="Multiattack",
        origin="natural",
        steps=(
            FixedActionUse(
                action_id="bite",
            ),
            FixedActionUse(
                action_id="claw",
                count=2,
            ),
        ),
    )

    actions_by_id: dict[str, MonsterAction] = {
        bite.action_id: bite,
        claw.action_id: claw,
        multiattack.action_id: multiattack,
    }

    result = calculate_action_average_damage(
        action=multiattack,
        actions_by_id=actions_by_id,
    )

    assert result == 20.5


def test_multiattack_uses_highest_damage_substitution() -> None:
    """Select the strongest valid substitution within Multiattack."""
    bite = create_attack(
        action_id="bite",
        dice_count=1,
        die_size=8,
        modifier=3,
    )

    claw = create_attack(
        action_id="claw",
        dice_count=1,
        die_size=6,
        modifier=3,
    )

    tail = create_attack(
        action_id="tail",
        dice_count=2,
        die_size=6,
        modifier=3,
    )

    multiattack = MultiattackAction(
        action_id="multiattack",
        name="Multiattack",
        origin="natural",
        steps=(
            FixedActionUse(
                action_id="claw",
                count=2,
            ),
            FixedActionUse(
                action_id="bite",
            ),
        ),
        substitutions=(
            ActionSubstitution(
                replaced_action_id="claw",
                replacement_action_ids=("tail",),
                maximum_replacements=1,
            ),
        ),
    )

    actions_by_id: dict[str, MonsterAction] = {
        bite.action_id: bite,
        claw.action_id: claw,
        tail.action_id: tail,
        multiattack.action_id: multiattack,
    }

    result = calculate_action_average_damage(
        action=multiattack,
        actions_by_id=actions_by_id,
    )

    # Result should be claw + bite + tail
    assert result == 24.0


def test_find_maximum_damage_multiattack_routine_selects_damaging_choice() -> None:
    """Choose a damaging ability over a non-damaging alternative."""
    tentacle = create_attack(
        action_id="tentacle",
        dice_count=2,
        die_size=6,
        modifier=3,
    )

    consume_memories = SavingThrowAction(
        action_id="consume_memories",
        name="Consume Memories",
        origin="special",
        target_description="One Creature within 60 feet.",
        saving_throw=SavingThrowDamage(
            ability="wisdom",
            difficulty_class=15,
            damage=(
                DamageRoll(
                    dice_count=4,
                    die_size=8,
                    modifier=0,
                    damage_type="psychic",
                ),
            ),
        ),
        expected_targets=1.0,
    )

    dominate_mind = MonsterAction(
        action_id="dominate_mind", name="Dominate Mind", category="special", origin="special"
    )

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

    actions_by_id: dict[str, MonsterAction] = {
        tentacle.action_id: tentacle,
        consume_memories.action_id: consume_memories,
        dominate_mind.action_id: dominate_mind,
        multiattack.action_id: multiattack,
    }

    routine, damage = find_maximum_damage_multiattack_routine(
        multiattack=multiattack, actions_by_id=actions_by_id
    )

    assert routine == MultiattackRoutine(
        action_ids=(
            "tentacle",
            "tentacle",
            "consume_memories",
        ),
    )
    assert damage == 38.0
