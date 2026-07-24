"""Test raw average damage calculations for D&D 5E 2024 monster."""

from pytest import raises

from monsteriser_monster_generator.systems.dnd5e.calculations import (
    TurnRoutine,
    calculate_action_average_damage,
    calculate_limited_use_average_damage,
    calculate_multiattack_routine_damage,
    calculate_turn_routine_damage,
    find_maximum_damage_multiattack_routine,
    find_maximum_damage_turn,
    find_monster_maximum_damage_turn,
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
from monsteriser_monster_generator.systems.dnd5e.models.base_monster import (
    BaseMonster,
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
        name="Venomous Bite",
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
        steps=(
            FixedActionUse(
                action_id="bite",
            ),
            FixedActionUse(
                action_id="claw",
            ),
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


def test_find_monster_maximum_damage_turn_builds_dependencies() -> None:
    """Generate mappings and routines when evaluating a monster."""
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
        steps=(
            FixedActionUse(
                action_id="bite",
            ),
            FixedActionUse(
                action_id="claw",
            ),
        ),
    )

    monster = BaseMonster(
        name="Wolf",
        abilities=[
            bite,
            claw,
            quick_claw,
            multiattack,
        ],
    )

    routine, damage = find_monster_maximum_damage_turn(monster)

    assert routine == TurnRoutine(
        primary_action_id="multiattack",
        bonus_action_id="quick_claw",
    )

    assert damage == 19.5


def test_find_monster_maximum_damage_turn_rejects_no_primary_actions() -> None:
    """Reject damage evaluation when no turn routines exist."""
    monster = BaseMonster(
        name="Passive Wolf",
    )

    with raises(
        ValueError,
        match="No turn routines were provided",
    ):
        find_monster_maximum_damage_turn(monster)


def test_limited_use_damage_once_over_three_rounds() -> None:
    """Average one limited use and two fallback turns."""
    result = calculate_limited_use_average_damage(
        limited_damage=30.0,
        fallback_damage=12.0,
        uses=1,
    )

    assert result == 18.0


def test_limited_use_damage_twice_over_three_rounds() -> None:
    """Average of two lmiited use and one fallback turn."""
    result = calculate_limited_use_average_damage(
        limited_damage=30.0,
        fallback_damage=12.0,
        uses=2,
    )

    assert result == 24.0


def test_limited_use_damage_uses_fallback_when_stronger() -> None:
    """Use the fallback option when it does more damage."""
    result = calculate_limited_use_average_damage(
        limited_damage=8.0,
        fallback_damage=12.0,
        uses=2,
    )

    assert result == 12.0


def test_limited_use_damage_uses_fallback_when_equal() -> None:
    """Use the fallback option when the damage is equal."""
    result = calculate_limited_use_average_damage(
        limited_damage=12.0,
        fallback_damage=12.0,
        uses=2,
    )

    assert result == 12.0


def test_limited_use_damage_accepts_zero_uses() -> None:
    """Use fallback damage when no limited uses are available."""
    result = calculate_limited_use_average_damage(
        limited_damage=30.0,
        fallback_damage=12.0,
        uses=0,
    )

    assert result == 12.0


def test_limited_use_damage_supports_custom_round_count() -> None:
    """Calculate average damage over a custom evaluation window."""
    result = calculate_limited_use_average_damage(
        limited_damage=30.0,
        fallback_damage=10.0,
        uses=2,
        rounds=4,
    )

    assert result == 20.0


def test_limited_use_damage_rejects_negative_uses() -> None:
    """Reject a negative limited-use_count."""
    with raises(
        ValueError,
        match="Uses cannot be negative",
    ):
        calculate_limited_use_average_damage(
            limited_damage=30.0,
            fallback_damage=12.0,
            uses=-1,
        )


def test_limited_use_damage_rejects_zero_rounds() -> None:
    """Reject an empty evaluation window."""
    with raises(
        ValueError,
        match="Rounds must be positive",
    ):
        calculate_limited_use_average_damage(
            limited_damage=30.0,
            fallback_damage=12.0,
            uses=1,
            rounds=0,
        )
