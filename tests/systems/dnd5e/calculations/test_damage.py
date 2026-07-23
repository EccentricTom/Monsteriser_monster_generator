"""Test raw average damage calculations for D&D 5E 2024 monster."""

from pytest import raises

from monsteriser_monster_generator.systems.dnd5e.calculations import (
    TurnRoutine,
    calculate_action_average_damage,
    calculate_turn_routine_damage,
    find_maximum_damage_turn,
)
from monsteriser_monster_generator.systems.dnd5e.models.actions import (
    ActionSubstitution,
    ActionUse,
    AttackAction,
    DamageRoll,
    MonsterAction,
    MultiattackAction,
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


def test_calculate_action_average_damage_for_attack() -> None:
    """Return the total average damage of an attack action."""
    bite = create_attack(
        action_id="bite",
        dice_count=2,
        die_size=6,
        modifier=3,
    )

    actions_by_id: dict[str, MonsterAction] = {
        bite.action_id: bite,
    }

    result = calculate_action_average_damage(
        action=bite,
        actions_by_id=actions_by_id,
    )

    assert result == 10.0


def test_calculate_action_average_damage_sums_damage_components() -> None:
    """Sum all damage components belonging to an attack."""
    venomous_bite = AttackAction(
        action_id="venomous_bite",
        name="Venemous Bite",
        origin="natural",
        attack_range="melee",
        attack_bonus=6,
        reach_ft=5,
        damage=(
            DamageRoll(
                dice_count=1,
                die_size=8,
                modifier=4,
                damage_type="piercing",
            ),
            DamageRoll(
                dice_count=2,
                die_size=6,
                modifier=0,
                damage_type="poison",
            ),
        ),
    )

    actions_by_id: dict[str, MonsterAction] = {
        venomous_bite.action_id: venomous_bite,
    }

    result = calculate_action_average_damage(
        action=venomous_bite,
        actions_by_id=actions_by_id,
    )

    assert result == 15.5


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
        base_sequence=(
            ActionUse(action_id="bite"),
            ActionUse(action_id="claw"),
            ActionUse(action_id="claw"),
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
        base_sequence=(
            ActionUse(action_id="claw"),
            ActionUse(action_id="claw"),
            ActionUse(action_id="bite"),
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


def test_calculate_average_damage_for_saving_throw() -> None:
    """Use failed-save damage multiplied by expected targets."""
    fire_breath = SavingThrowAction(
        action_id="fire_breath",
        name="Fire Breath",
        origin="special",
        target_description="Each creature in a 30ft cone",
        expected_targets=2.0,
        saving_throw=SavingThrowDamage(
            ability="dexterity",
            difficulty_class=15,
            damage=(
                DamageRoll(
                    dice_count=6,
                    die_size=6,
                    damage_type="fire",
                ),
            ),
            success_outcome="half",
        ),
    )

    actions_by_id: dict[str, MonsterAction] = {
        fire_breath.action_id: fire_breath,
    }

    result = calculate_action_average_damage(
        action=fire_breath,
        actions_by_id=actions_by_id,
    )

    assert result == 42.0


def test_calculate_action_average_damage_returns_zero_for_non_damage_action() -> None:
    """Return zero for an action without modeled damage."""
    dash = MonsterAction(
        action_id="quick_step",
        name="Quick Step",
        category="special",
        origin="special",
        timing="bonus_action",
    )

    actions_by_id: dict[str, MonsterAction] = {
        dash.action_id: dash,
    }

    result = calculate_action_average_damage(
        action=dash,
        actions_by_id=actions_by_id,
    )

    assert result == 0.0


def test_caculate_turn_routine_damage_for_primary_action() -> None:
    """Calculate damage for a turn containing only a primary action."""
    bite = create_attack(
        action_id="bite",
        dice_count=2,
        die_size=6,
        modifier=3,
    )

    routine = TurnRoutine(
        primary_action_id="bite",
    )

    actions_by_id: dict[str, MonsterAction] = {
        bite.action_id: bite,
    }

    result = calculate_turn_routine_damage(
        routine=routine,
        actions_by_id=actions_by_id,
    )

    assert result == 10.0


def test_calculate_turn_routine_damage_adds_bonus_action() -> None:
    """Add bonus-action damage to primary-action damage."""
    bite = create_attack(action_id="bite", dice_count=2, die_size=6, modifier=3)

    quick_claw = create_attack(
        action_id="quick_claw",
        dice_count=1,
        die_size=4,
        modifier=3,
        timing="bonus_action",
    )

    routine = TurnRoutine(
        primary_action_id="bite",
        bonus_action_id="quick_claw",
    )

    actions_by_id: dict[str, MonsterAction] = {
        bite.action_id: bite,
        quick_claw.action_id: quick_claw,
    }

    result = calculate_turn_routine_damage(
        routine=routine,
        actions_by_id=actions_by_id,
    )

    assert result == 15.5


def test_find_maximum_damage_turn_return_strongest_routine() -> None:
    """Return the legal attack routine with the strongest average damage."""
    bite = create_attack(action_id="bite", dice_count=1, die_size=8, modifier=3)
    claw = create_attack(action_id="claw", dice_count=1, die_size=6, modifier=3)
    quick_claw = create_attack(
        action_id="quick_claw",
        dice_count=1,
        die_size=4,
        modifier=3,
        timing="bonus_action",
    )

    multiattack = MultiattackAction(
        action_id="multiattack",
        name="Multiattack",
        origin="natural",
        base_sequence=(
            ActionUse(action_id="bite"),
            ActionUse(action_id="claw"),
        ),
    )

    routines = (
        TurnRoutine(primary_action_id="bite"),
        TurnRoutine(
            primary_action_id="bite",
            bonus_action_id="quick_claw",
        ),
        TurnRoutine(primary_action_id="multiattack"),
        TurnRoutine(
            primary_action_id="multiattack",
            bonus_action_id="quick_claw",
        ),
    )

    actions_by_id: dict[str, MonsterAction] = {
        bite.action_id: bite,
        claw.action_id: claw,
        multiattack.action_id: multiattack,
        quick_claw.action_id: quick_claw,
    }

    routine, damage = find_maximum_damage_turn(routines=routines, actions_by_id=actions_by_id)

    assert routine == TurnRoutine(
        primary_action_id="multiattack",
        bonus_action_id="quick_claw",
    )
    assert damage == 19.5


def test_find_maximum_damage_turn_raises_for_empty_routine() -> None:
    """Reject maximum-damage calculation without turn routines."""
    with raises(
        ValueError,
        match="No turn routines were provided",
    ):
        find_maximum_damage_turn(
            routines=(),
            actions_by_id={},
        )


def test_calculate_turn_routine_damage_raises_for_unknown_primary_action() -> None:
    """Raises KeyError for an unknown primary action identifier."""
    routine = TurnRoutine(primary_action_id="missing_action")

    with raises(KeyError, match="missing_action"):
        calculate_turn_routine_damage(
            routine=routine,
            actions_by_id={},
        )


def test_calculate_turn_routine_damage_raises_for_unknown_bonus_action() -> None:
    """Raise KeyError for an unknown bonus-action identifier."""
    bite = create_attack(action_id="bite")

    routine = TurnRoutine(
        primary_action_id="bite",
        bonus_action_id="missing_bonus_action",
    )

    actions_by_id: dict[str, MonsterAction] = {
        bite.action_id: bite,
    }

    with raises(KeyError, match="missing_bonus_action"):
        calculate_turn_routine_damage(
            routine=routine,
            actions_by_id=actions_by_id,
        )
