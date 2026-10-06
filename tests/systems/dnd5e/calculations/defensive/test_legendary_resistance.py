from pytest import raises

from monsteriser_monster_generator.systems.dnd5e.calculations.defensive.legendary_resistance import (
    LegendaryResistanceAdjustmentResult,
    calculate_legendary_resistance_effective_hit_points,
    get_legendary_resistance_hit_points_per_use,
)
from monsteriser_monster_generator.systems.dnd5e.models.base_monster import (
    BaseMonster,
)
from monsteriser_monster_generator.systems.dnd5e.models.traits import (
    LegendaryResistanceTrait,
)


def test_get_legendary_resistance_hit_points_per_use() -> None:
    """Return the correct effective HP contribution for each CR band."""
    assert (
        get_legendary_resistance_hit_points_per_use(
            expected_challenge_rating=1.0,
        )
        == 10
    )
    assert (
        get_legendary_resistance_hit_points_per_use(
            expected_challenge_rating=4.0,
        )
        == 10
    )

    assert (
        get_legendary_resistance_hit_points_per_use(
            expected_challenge_rating=5.0,
        )
        == 20
    )
    assert (
        get_legendary_resistance_hit_points_per_use(
            expected_challenge_rating=10.0,
        )
        == 20
    )

    assert (
        get_legendary_resistance_hit_points_per_use(
            expected_challenge_rating=11.0,
        )
        == 30
    )
    assert (
        get_legendary_resistance_hit_points_per_use(
            expected_challenge_rating=20.0,
        )
        == 30
    )


def test_calculate_legendary_resistance_effective_hit_points() -> None:
    """Calculate effective HP from Legendary Resistance uses."""
    monster = BaseMonster(
        name="Ancient Monster",
        expected_cr=8.0,
        traits=[
            LegendaryResistanceTrait(
                uses=3,
            )
        ],
    )

    result = calculate_legendary_resistance_effective_hit_points(
        monster=monster,
    )

    assert result == LegendaryResistanceAdjustmentResult(
        uses=3,
        hit_points_per_use=20,
        effective_hit_points=60.0,
    )


def test_calculate_legendary_resistance_effective_hit_points_returns_none_without_trait() -> None:
    """Return no adjustment when Legendary Resistance is absent."""
    monster = BaseMonster(
        name="Wolf",
        expected_cr=2.0,
    )

    result = calculate_legendary_resistance_effective_hit_points(
        monster=monster,
    )

    assert result is None


def test_calculate_legendary_resistance_effective_hit_points_rejects_multiple_traits() -> None:
    """Reject monsters with multiple Legendary Resistance traits."""
    monster = BaseMonster(
        name="Invalid Monster",
        expected_cr=8.0,
        traits=[
            LegendaryResistanceTrait(
                uses=3,
            ),
            LegendaryResistanceTrait(
                uses=1,
            ),
        ],
    )

    with raises(
        ValueError,
        match="Monster cannot have multiple Legendary Resistance traits",
    ):
        calculate_legendary_resistance_effective_hit_points(
            monster=monster,
        )


def test_get_legendary_resistance_hit_points_per_use_rejects_cr_below_one() -> None:
    """Reject Legendary Resistance below the supported CR range."""
    with raises(
        ValueError,
        match=("Legendary Resistance requires an expected challenge rating of at least 1"),
    ):
        get_legendary_resistance_hit_points_per_use(
            expected_challenge_rating=0.5,
        )
