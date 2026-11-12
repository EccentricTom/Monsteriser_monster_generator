"""Test monster traits for D&D 5E 2024 monsters."""

from pytest import mark, raises

from monsteriser_monster_generator.systems.dnd5e.models.actions.effects import (
    DamageRoll,
    FlatDamage,
)
from monsteriser_monster_generator.systems.dnd5e.models.traits import (
    LegendaryResistanceTrait,
    PassiveDamageTrait,
    PassiveDamageTrigger,
    RegenerationTrait,
)


def test_regeneration_trait() -> None:
    """Test that the regeneration trait model works."""
    test_regen = RegenerationTrait(hit_points_per_round=10)

    assert test_regen.hit_points_per_round == 10


def test_regeneration_trait_fails_negative_hit_points() -> None:
    """Test that the regeneration trait model fails when hit points are not positive."""
    with raises(ValueError, match="Regeneration hit points per round must be positive"):
        RegenerationTrait(hit_points_per_round=0)


def test_legendary_resistance_trait() -> None:
    """Test the instantion of legendary resistances."""
    test_legendary_resistance = LegendaryResistanceTrait()
    test_legendary_resistance_custom = LegendaryResistanceTrait(uses=5)

    assert test_legendary_resistance.uses == 3
    assert test_legendary_resistance_custom.uses == 5


def test_legendary_resistance_trait_fails_negative_uses() -> None:
    """Test that the legendary resistance model fails when uses are not positive."""
    with raises(ValueError, match="Legendary resistance uses must be positive"):
        LegendaryResistanceTrait(uses=0)


@mark.parametrize("trigger", ["aura", "retaliation", "conditional"])
def test_passive_damage_trait(trigger: PassiveDamageTrigger) -> None:
    """Store passive damage and its trigger with the default target count."""
    test_passive_damage_trait = PassiveDamageTrait(
        trigger=trigger,
        damage=(
            DamageRoll(
                dice_count=1,
                die_size=6,
                modifier=0,
                damage_type="slashing",
            ),
        ),
    )
    assert test_passive_damage_trait.damage == (
        DamageRoll(
            dice_count=1,
            die_size=6,
            modifier=0,
            damage_type="slashing",
        ),
    )
    assert test_passive_damage_trait.expected_targets == 1.0
    assert test_passive_damage_trait.trigger == trigger


@mark.parametrize("expected_targets", [None, 0.0, 1.5])
def test_passive_damage_trait_custom_expected_targets(expected_targets: float | None) -> None:
    """Store an optional target count without applying calculation defaults."""
    trait = PassiveDamageTrait(
        damage=(FlatDamage(amount=5, damage_type="fire"),),
        trigger="aura",
        expected_targets=expected_targets,
    )

    assert trait.expected_targets == expected_targets


def test_passive_damage_trait_mixed_damage() -> None:
    """Store rolled and flat damage components in the same trait."""
    damage = (
        DamageRoll(dice_count=1, die_size=6, damage_type="fire"),
        FlatDamage(amount=5, damage_type="radiant"),
    )
    trait = PassiveDamageTrait(
        damage=damage,
        trigger="retaliation",
    )

    assert trait.damage == damage


def test_passive_damage_trait_requires_trigger() -> None:
    """Require callers to specify how passive damage is triggered."""
    with raises(TypeError, match="trigger"):
        PassiveDamageTrait(
            damage=(FlatDamage(amount=5, damage_type="fire"),),
        )  # type: ignore (testing missing type)
