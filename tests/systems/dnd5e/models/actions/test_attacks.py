"""Test attack action models."""

from pytest import raises

from monsteriser_monster_generator.systems.dnd5e.models.actions import (
    AttackAction,
    DamageRoll,
    FlatDamage,
)


def test_attack_action_average_damage() -> None:
    """Calculate average damage across multiple damage components."""
    attack = AttackAction(
        action_id="flame_sword",
        name="Flame Sword",
        origin="natural",
        attack_range="melee",
        attack_bonus=6,
        reach_ft=5,
        damage=(
            DamageRoll(
                dice_count=2,
                die_size=6,
                modifier=3,
                damage_type="slashing",
            ),
            FlatDamage(
                amount=5,
                damage_type="fire",
            ),
        ),
    )

    assert attack.average_damage() == 15.0


def test_attack_action_generates_melee_description() -> None:
    """Generate a melee attack description."""
    attack = AttackAction(
        action_id="bite",
        name="Bite",
        origin="natural",
        attack_range="melee",
        attack_bonus=5,
        reach_ft=5,
        damage=(
            DamageRoll(
                dice_count=2,
                die_size=6,
                modifier=3,
                damage_type="piercing",
            ),
        ),
    )

    assert attack.generate_description() == (
        "Melee attack roll: 5, reach 5 ft. Hit: 10 (2d6 + 3) Piercing damage"
    )


def test_attack_action_generates_ranged_description() -> None:
    """Generate a ranged attack description."""
    attack = AttackAction(
        action_id="longbow",
        name="Longbow",
        origin="gear",
        attack_range="ranged",
        attack_bonus=6,
        normal_range_ft=150,
        long_range_ft=600,
        damage=(
            DamageRoll(
                dice_count=1,
                die_size=8,
                modifier=3,
                damage_type="piercing",
            ),
        ),
    )

    description = attack.generate_description()

    assert "Ranged attack roll: 6" in description
    assert "range 150/600 ft" in description


def test_attack_action_generates_melee_or_ranged_description() -> None:
    """Generate a combined melee-or-ranged attack description."""
    attack = AttackAction(
        action_id="spear",
        name="Spear",
        origin="gear",
        attack_range="melee_or_ranged",
        attack_bonus=5,
        reach_ft=5,
        normal_range_ft=20,
        long_range_ft=60,
        damage=(
            DamageRoll(
                dice_count=1,
                die_size=6,
                modifier=3,
                damage_type="piercing",
            ),
        ),
    )

    description = attack.generate_description()

    assert "reach 5 ft" in description
    assert "range 20/60 ft" in description


def test_attack_action_uses_description_override() -> None:
    """Return an explicit description override unchanged."""
    description_override = "The creature snaps at a target within reach."
    attack = AttackAction(
        action_id="bite",
        name="Bite",
        origin="natural",
        attack_range="melee",
        attack_bonus=5,
        damage=(),
        description_override=description_override,
    )

    assert attack.generate_description() == description_override


def test_attack_action_supports_flat_damage_description() -> None:
    """Generate attack text containing fixed damage."""
    attack = AttackAction(
        action_id="bite",
        name="Bite",
        origin="natural",
        attack_range="melee",
        attack_bonus=5,
        reach_ft=5,
        damage=(
            FlatDamage(
                amount=5,
                damage_type="piercing",
            ),
        ),
    )

    assert attack.generate_description() == (
        "Melee attack roll: 5, reach 5 ft. Hit: 5 Piercing damage"
    )


def test_attack_action_rejects_missing_melee_reach() -> None:
    """Reject description generation without melee reach."""
    attack = AttackAction(
        action_id="bite",
        name="Bite",
        origin="natural",
        attack_range="melee",
        attack_bonus=5,
        damage=(
            FlatDamage(
                amount=5,
                damage_type="piercing",
            ),
        ),
    )

    with raises(
        ValueError,
        match="Melee attack 'bite' has no reach",
    ):
        attack.generate_description()
