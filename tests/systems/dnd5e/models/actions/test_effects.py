"""Test action effect models."""

from pytest import raises

from monsteriser_monster_generator.systems.dnd5e.models.actions.effects import (
    DamageRoll,
    FlatDamage,
)


def test_damage_roll_average_damage() -> None:
    """Calculate the mathematical average of rolled damage."""
    damage = DamageRoll(
        dice_count=2,
        die_size=10,
        modifier=3,
        damage_type="fire",
    )

    assert damage.average_damage() == 14.0


def test_flat_damage_average_damage() -> None:
    """Return fixed damage as average damage."""
    damage = FlatDamage(
        amount=20,
        damage_type="radiant",
    )

    assert damage.average_damage() == 20.0


def test_flat_damage_rejects_negative_damage() -> None:
    """Reject negative flat damage."""
    with raises(
        ValueError,
        match="Flat damage cannot be negative",
    ):
        FlatDamage(
            amount=-1,
            damage_type="radiant",
        )
