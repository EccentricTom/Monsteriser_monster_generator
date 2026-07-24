"""Calculate the raw average damage for D&D 5E 2024 monster actions for single attacks."""

from monsteriser_monster_generator.systems.dnd5e.calculations import (
    calculate_action_average_damage,
)
from monsteriser_monster_generator.systems.dnd5e.models.actions import (
    AttackAction,
    DamageRoll,
    MonsterAction,
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
