"""Test monster traits for D&D 5E 2024 monsters."""

from pytest import raises

from monsteriser_monster_generator.systems.dnd5e.models.actions.effects import DamageRoll
from monsteriser_monster_generator.systems.dnd5e.models.traits import (
    LegendaryResistanceTrait,
    PassiveDamageTrait,
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


def test_passive_damage_trait() -> None:
    """Test the instantation of the passive damage trait."""
    test_passive_damage_trait = PassiveDamageTrait(
        damage=(
            DamageRoll(
                dice_count=1,
                die_size=6,
                modifier=0,
                damage_type="slashing",
            ),
        ),
        expected_targets=1.0,
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


def test_passive_damage_trait_fails_negative_or_none_expected_targets() -> None:
    """Test that the passive damage model fails when expected targets are not positive."""
    with raises(ValueError, match="Expected targets must be positive"):
        PassiveDamageTrait(
            damage=(
                DamageRoll(
                    dice_count=1,
                    die_size=6,
                    modifier=0,
                    damage_type="slashing",
                ),
            ),
            expected_targets=0,
        )
