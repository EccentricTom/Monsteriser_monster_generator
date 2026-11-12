from pytest import mark

from monsteriser_monster_generator.systems.dnd5e.calculations.offensive.passive_damage import (
    calculate_passive_damage,
    calculate_passive_trait_average_damage,
    get_passive_damage_expected_targets,
)
from monsteriser_monster_generator.systems.dnd5e.models.actions import (
    DamageRoll,
    FlatDamage,
)
from monsteriser_monster_generator.systems.dnd5e.models.base_monster import BaseMonster
from monsteriser_monster_generator.systems.dnd5e.models.traits import (
    PassiveDamageTrait,
    PassiveDamageTrigger,
    RegenerationTrait,
)


@mark.parametrize(
    ("trigger", "expected_targets", "expected_result"),
    [
        ("aura", None, 2.0),
        ("retaliation", None, 1.0),
        ("conditional", None, 1.0),
        ("aura", 1.5, 1.5),
        ("retaliation", 3.0, 3.0),
        ("conditional", 2.5, 2.5),
        ("aura", 0.0, 0.0),
    ],
)
def test_get_passive_damage_expected_targets(
    trigger: PassiveDamageTrigger,
    expected_targets: float | None,
    expected_result: float,
) -> None:
    """Use explicit target counts or fall back to the trigger's target count."""
    trait = PassiveDamageTrait(
        damage=(FlatDamage(amount=5, damage_type="fire"),),
        trigger=trigger,
        expected_targets=expected_targets,
    )

    result = get_passive_damage_expected_targets(trait=trait)

    assert result == expected_result


def test_calculate_passive_aura_damage_uses_model_default_targets() -> None:
    """Use the model's default target count when no override is supplied."""
    trait = PassiveDamageTrait(
        damage=(FlatDamage(amount=5, damage_type="fire"),),
        trigger="aura",
    )

    result = calculate_passive_trait_average_damage(trait=trait)

    assert result == 5.0


def test_calculate_passive_trait_average_damage_combines_components() -> None:
    """Scale the sum of rolled and flat damage using the aura target count."""
    trait = PassiveDamageTrait(
        damage=(
            DamageRoll(dice_count=2, die_size=6, damage_type="fire"),
            FlatDamage(amount=5, damage_type="radiant"),
        ),
        trigger="aura",
        expected_targets=None,
    )

    result = calculate_passive_trait_average_damage(trait=trait)

    assert result == 24.0


def test_calculate_passive_trait_average_damage() -> None:
    """Calculate average damage from a passive damage trait."""
    trait = PassiveDamageTrait(
        trigger="retaliation",
        damage=(
            DamageRoll(
                dice_count=2,
                die_size=6,
                damage_type="fire",
            ),
        ),
    )

    result = calculate_passive_trait_average_damage(
        trait=trait,
    )

    assert result == 7.0


def test_calculate_passive_trait_average_flat_damage() -> None:
    """Calculate passive damage from fixed damage."""
    trait = PassiveDamageTrait(
        trigger="conditional",
        damage=(
            FlatDamage(
                amount=5,
                damage_type="necrotic",
            ),
        ),
    )

    result = calculate_passive_trait_average_damage(
        trait=trait,
    )

    assert result == 5.0


def test_calculate_passive_trait_average_damage_uses_expected_targets() -> None:
    """Scale passive damage by the expected number of targets."""
    trait = PassiveDamageTrait(
        trigger="aura",
        damage=(
            DamageRoll(
                dice_count=2,
                die_size=6,
                damage_type="fire",
            ),
        ),
        expected_targets=1.5,
    )

    result = calculate_passive_trait_average_damage(
        trait=trait,
    )

    assert result == 10.5


def test_calculate_passive_damage_combines_traits() -> None:
    """Combine damage from multiple passive damage traits."""
    monster = BaseMonster(
        name="Test Monster",
        traits=[
            PassiveDamageTrait(
                trigger="aura",
                expected_targets=None,
                damage=(
                    DamageRoll(
                        dice_count=2,
                        die_size=6,
                        damage_type="fire",
                    ),
                ),
            ),
            PassiveDamageTrait(
                trigger="retaliation",
                expected_targets=None,
                damage=(
                    FlatDamage(
                        amount=5,
                        damage_type="necrotic",
                    ),
                ),
            ),
            RegenerationTrait(hit_points_per_round=10),
        ],
    )

    result = calculate_passive_damage(
        monster=monster,
    )

    assert result.average_damage_per_round == 19.0


def test_calculate_passive_damage_returns_zero_without_traits() -> None:
    """Return zero passive damage when no passive traits are present."""
    monster = BaseMonster(
        name="Test Monster",
    )

    result = calculate_passive_damage(
        monster=monster,
    )

    assert result.average_damage_per_round == 0.0
