"""Test action effect models."""

from pytest import raises

from monsteriser_monster_generator.systems.dnd5e.models.actions.effects import (
    DamageRoll,
    FlatDamage,
    SavingThrowDamage,
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


def test_flat_damage_stat_block_text() -> None:
    """Generate stat-block text for fixed damage."""
    damage = FlatDamage(
        amount=5,
        damage_type="necrotic",
    )

    assert damage.stat_block_text() == "5 necrotic damage"


def test_saving_throw_flat_damage() -> None:
    """Calculate failed-save damage and half damage for a successful save."""
    saving_throw = SavingThrowDamage(
        damage=(FlatDamage(amount=5, damage_type="fire"),),
        success_outcome="half",
    )

    assert saving_throw.average_failed_save() == 5.0
    assert saving_throw.average_successful_save() == 2.5


def test_saving_throw_mixed_damage() -> None:
    """Combine rolled and flat damage before applying a successful save."""
    saving_throw = SavingThrowDamage(
        damage=(
            DamageRoll(
                dice_count=2,
                die_size=10,
                modifier=3,
                damage_type="fire",
            ),
            FlatDamage(amount=5, damage_type="radiant"),
        ),
        success_outcome="half",
    )

    assert saving_throw.average_failed_save() == 19.0
    assert saving_throw.average_successful_save() == 9.5


def test_saving_throw_mixed_damage_negated_on_success() -> None:
    """Negate both rolled and flat damage when a successful save prevents damage."""
    saving_throw = SavingThrowDamage(
        damage=(
            DamageRoll(
                dice_count=2,
                die_size=10,
                modifier=3,
                damage_type="fire",
            ),
            FlatDamage(amount=5, damage_type="radiant"),
        ),
        success_outcome="none",
    )

    assert saving_throw.average_failed_save() == 19.0
    assert saving_throw.average_successful_save() == 0.0


def test_damage_roll_stat_block_text() -> None:
    """Generate stat-block text for rolled damage."""
    damage = DamageRoll(
        dice_count=2,
        die_size=10,
        modifier=3,
        damage_type="fire",
    )

    assert damage.stat_block_text() == "14 (2d10 + 3) Fire damage"
