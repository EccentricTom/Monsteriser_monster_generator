from monsteriser_monster_generator.systems.dnd5e.calculations.offensive.passive_damage import (
    PassiveDamageTrait,
    calculate_passive_damage,
    calculate_passive_trait_average_damage,
)
from monsteriser_monster_generator.systems.dnd5e.models.actions import (
    DamageRoll,
    FlatDamage,
)
from monsteriser_monster_generator.systems.dnd5e.models.base_monster import BaseMonster


def test_calculate_passive_trait_average_damage() -> None:
    """Calculate average damage from a passive damage trait."""
    trait = PassiveDamageTrait(
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
        damage=(
            DamageRoll(
                dice_count=2,
                die_size=6,
                damage_type="fire",
            ),
        ),
        expected_targets=2.0,
    )

    result = calculate_passive_trait_average_damage(
        trait=trait,
    )

    assert result == 14.0


def test_calculate_passive_damage_combines_traits() -> None:
    """Combine damage from multiple passive damage traits."""
    monster = BaseMonster(
        name="Test Monster",
        traits=[
            PassiveDamageTrait(
                damage=(
                    DamageRoll(
                        dice_count=2,
                        die_size=6,
                        damage_type="fire",
                    ),
                ),
            ),
            PassiveDamageTrait(
                damage=(
                    FlatDamage(
                        amount=5,
                        damage_type="necrotic",
                    ),
                ),
            ),
        ],
    )

    result = calculate_passive_damage(
        monster=monster,
    )

    assert result.average_damage_per_round == 12.0


def test_calculate_passive_damage_returns_zero_without_traits() -> None:
    """Return zero passive damage when no passive traits are present."""
    monster = BaseMonster(
        name="Test Monster",
    )

    result = calculate_passive_damage(
        monster=monster,
    )

    assert result.average_damage_per_round == 0.0
