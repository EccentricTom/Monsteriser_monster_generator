from pytest import approx  # pyright: ignore[reportUnknownVariableType]

from monsteriser_monster_generator.systems.dnd5e.calculations.combat_routines import TurnRoutine
from monsteriser_monster_generator.systems.dnd5e.calculations.offensive.accuracy import (
    OffensiveAccuracy,
    OffensiveAccuracyContribution,
    calculate_offensive_accuracy_contributions,
)
from monsteriser_monster_generator.systems.dnd5e.calculations.offensive.offensive_damage import (
    OffensiveDamageResult,
)
from monsteriser_monster_generator.systems.dnd5e.models.actions import (
    AttackAction,
    DamageRoll,
    SavingThrowAction,
    SavingThrowDamage,
)
from monsteriser_monster_generator.systems.dnd5e.models.actions.usage import (
    LimitedUsage,
    RechargeUsage,
)
from monsteriser_monster_generator.systems.dnd5e.models.base_monster import (
    BaseMonster,
)


def test_calculate_offensive_accuracy_contributions_uses_fallback_only() -> None:
    """Scale fallback accuracy contributions across the full CR window."""
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

    monster = BaseMonster(
        name="Test Monster",
        abilities=[bite],
    )

    damage_result = OffensiveDamageResult(
        average_damage_per_round=8.5,
        fallback_routine=TurnRoutine(
            primary_action_id="bite",
        ),
    )

    result = calculate_offensive_accuracy_contributions(
        monster=monster,
        damage_result=damage_result,
        rounds=3,
    )

    assert result == (
        OffensiveAccuracyContribution(
            accuracy=OffensiveAccuracy(
                accuracy_type="attack_bonus",
                value=7,
            ),
            damage=25.5,
        ),
    )


def test_calculate_offensive_accuracy_contributions_uses_limited_action() -> None:
    """Weight limited-use and fallback accuracy across the CR window."""
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

    fire_breath = SavingThrowAction(
        action_id="fire_breath",
        name="Fire Breath",
        origin="natural",
        ability="dexterity",
        difficulty_class=15,
        saving_throw=SavingThrowDamage(
            damage=(
                DamageRoll(
                    dice_count=6,
                    die_size=6,
                    damage_type="fire",
                ),
            ),
            success_outcome="half",
        ),
        usage=LimitedUsage(uses=1, period="day"),
    )

    monster = BaseMonster(
        name="Test Monster",
        abilities=[
            bite,
            fire_breath,
        ],
    )

    damage_result = OffensiveDamageResult(
        average_damage_per_round=(21.0 + 8.5 + 8.5) / 3,
        fallback_routine=TurnRoutine(
            primary_action_id="bite",
        ),
        special_action_id="fire_breath",
    )

    result = calculate_offensive_accuracy_contributions(
        monster=monster,
        damage_result=damage_result,
        rounds=3,
    )

    assert result == (
        OffensiveAccuracyContribution(
            accuracy=OffensiveAccuracy(
                accuracy_type="save_dc",
                value=15,
            ),
            damage=21.0,
        ),
        OffensiveAccuracyContribution(
            accuracy=OffensiveAccuracy(
                accuracy_type="attack_bonus",
                value=7,
            ),
            damage=17.0,
        ),
    )


def test_calculate_offensive_accuracy_contributions_uses_recharge_action() -> None:
    """Weight recharge and fallback accuracy by expected usage."""
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

    fire_breath = SavingThrowAction(
        action_id="fire_breath",
        name="Fire Breath",
        origin="natural",
        ability="dexterity",
        difficulty_class=15,
        saving_throw=SavingThrowDamage(
            damage=(
                DamageRoll(
                    dice_count=6,
                    die_size=6,
                    damage_type="fire",
                ),
            ),
            success_outcome="half",
        ),
        usage=RechargeUsage(recharge_minimum=3),
    )

    monster = BaseMonster(
        name="Test Monster",
        abilities=[
            bite,
            fire_breath,
        ],
    )

    damage_result = OffensiveDamageResult(
        average_damage_per_round=0.0,
        fallback_routine=TurnRoutine(
            primary_action_id="bite",
        ),
        special_action_id="fire_breath",
    )

    result = calculate_offensive_accuracy_contributions(
        monster=monster,
        damage_result=damage_result,
        rounds=3,
    )

    assert result[0].accuracy == OffensiveAccuracy(
        accuracy_type="save_dc",
        value=15,
    )
    assert result[0].damage == approx(49.0)

    assert result[1].accuracy == OffensiveAccuracy(
        accuracy_type="attack_bonus",
        value=7,
    )
    assert result[1].damage == approx(17 / 3)
