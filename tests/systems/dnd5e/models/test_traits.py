from pytest import raises

from monsteriser_monster_generator.systems.dnd5e.models.traits import RegenerationTrait


def test_regeneration_trait() -> None:
    """Test that the regeneration trait model works."""
    test_regen = RegenerationTrait(hit_points_per_round=10)

    assert test_regen.hit_points_per_round == 10


def test_regeneration_trait_fails_negative_hit_points() -> None:
    """Test that the regeneration trait model fails when hit points are not positive."""
    with raises(ValueError, match="Regeneration hit points per round must be positive"):
        RegenerationTrait(hit_points_per_round=0)
