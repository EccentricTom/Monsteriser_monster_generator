"""Test the base D&D 5E 2024 monster model."""

from pytest import raises

from monsteriser_monster_generator.systems.dnd5e.models.actions import MonsterAction
from monsteriser_monster_generator.systems.dnd5e.models.base_monster import BaseMonster


def test_get_abilities_by_id_indexes_abilities() -> None:
    """Test that the model correctly indexes abilities added to it."""
    bite = MonsterAction(action_id="bite", name="Bite", category="attack", origin="natural")

    roar = MonsterAction(action_id="roar", name="Roar", category="special", origin="natural")

    monster = BaseMonster(
        name="Creature",
        abilities=[
            bite,
            roar,
        ],
    )

    result = monster.get_abilities_by_id()

    assert result == {
        "bite": bite,
        "roar": roar,
    }


def test_get_abilities_by_id_rejects_duplicate_identifiers() -> None:
    """Reject multiple abilities with the same identifier."""
    first_bite = MonsterAction(action_id="bite", name="Bite", category="attack", origin="natural")

    second_bite = MonsterAction(action_id="bite", name="Bite", category="attack", origin="natural")

    monster = BaseMonster(
        name="Creature",
        abilities=[
            first_bite,
            second_bite,
        ],
    )

    with raises(
        ValueError,
        match="Duplicate action identifier: 'bite'",
    ):
        monster.get_abilities_by_id()
