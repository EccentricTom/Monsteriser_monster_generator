import pytest
from pytest import raises

from monsteriser_monster_generator.systems.dnd5e.calculations.challenge_rating import (
    CHALLENGE_RATING_POLICY,
    ChallengeRatingPolicy,
    calculate_monster_challenge_rating,
    combine_challenge_ratings,
)
from monsteriser_monster_generator.systems.dnd5e.models.actions import (
    AttackAction,
    DamageRoll,
)
from monsteriser_monster_generator.systems.dnd5e.models.base_monster import BaseMonster
from monsteriser_monster_generator.systems.dnd5e.reference_data import (
    load_challenge_rating_reference,
)

REFERENCE = load_challenge_rating_reference()


def test_challenge_rating_policy_defaults() -> None:
    """Use equal weighting and round down by default."""
    assert (
        ChallengeRatingPolicy(
            offensive_weight=0.5,
            defensive_weight=0.5,
            round_down=True,
        )
        == CHALLENGE_RATING_POLICY
    )


@pytest.mark.parametrize(
    (
        "offensive_cr",
        "defensive_cr",
        "expected_average",
        "expected_final_cr",
    ),
    [
        (1, 1, 1.0, 1),
        (2, 2, 2.0, 2),
        (2, 1, 1.5, 1),
        (5, 4, 4.5, 4),
        (8, 3, 5.5, 5),
        (10, 6, 8.0, 8),
    ],
)
def test_combine_challenge_ratings(
    offensive_cr: int,
    defensive_cr: int,
    expected_average: float,
    expected_final_cr: int,
) -> None:
    """Average offensive and defensive CR and round down."""
    average, final_cr = combine_challenge_ratings(
        offensive_challenge_rating=offensive_cr,
        defensive_challenge_rating=defensive_cr,
        reference=REFERENCE,
    )

    assert average == expected_average
    assert final_cr == expected_final_cr


@pytest.mark.parametrize(
    ("offensive_cr", "defensive_cr"),
    [
        (-1, 1),
        (1, -1),
    ],
)
def test_combine_challenge_ratings_rejects_negative_cr(
    offensive_cr: int,
    defensive_cr: int,
) -> None:
    """Reject negative challenge ratings."""
    with raises(ValueError):
        combine_challenge_ratings(
            offensive_challenge_rating=offensive_cr,
            defensive_challenge_rating=defensive_cr,
            reference=REFERENCE,
        )


@pytest.mark.parametrize(
    ("offensive_cr", "defensive_cr", "expected"),
    [
        (8, 2, 5),
        (2, 8, 5),
        (7, 3, 5),
        (3, 7, 5),
    ],
)
def test_combine_challenge_ratings_weights_offense_and_defense_equally(
    offensive_cr: int,
    defensive_cr: int,
    expected: int,
) -> None:
    """Treat offensive and defensive CR symmetrically."""
    _, final = combine_challenge_ratings(
        offensive_challenge_rating=offensive_cr,
        defensive_challenge_rating=defensive_cr,
        reference=REFERENCE,
    )

    assert final == expected


@pytest.mark.parametrize(
    ("offensive_cr", "defensive_cr", "expected_average", "expected_final"),
    [
        (1, 2, 1.5, 1),
        (4, 5, 4.5, 4),
        (9, 10, 9.5, 9),
    ],
)
def test_combine_challenge_ratings_rounds_half_values_down(
    offensive_cr: int,
    defensive_cr: int,
    expected_average: float,
    expected_final: int,
) -> None:
    """Round fractional challenge ratings down."""
    average, final = combine_challenge_ratings(
        offensive_challenge_rating=offensive_cr,
        defensive_challenge_rating=defensive_cr,
        reference=REFERENCE,
    )

    assert average == expected_average
    assert final == expected_final


def test_combine_challenge_ratings_can_use_standard_rounding(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Use standard rounding when round-down policy is disabled."""
    policy = ChallengeRatingPolicy(
        offensive_weight=0.5,
        defensive_weight=0.5,
        round_down=False,
    )

    monkeypatch.setattr(
        "monsteriser_monster_generator.systems.dnd5e.calculations.challenge_rating.CHALLENGE_RATING_POLICY",
        policy,
    )

    average, final = combine_challenge_ratings(
        offensive_challenge_rating=3,
        defensive_challenge_rating=2,
        reference=REFERENCE,
    )

    assert average == 2.5
    assert final == 2.0


def test_combine_challenge_ratings_uses_configured_weights(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Apply configured offensive and defensive CR weights."""
    policy = ChallengeRatingPolicy(
        offensive_weight=0.75,
        defensive_weight=0.25,
        round_down=True,
    )

    monkeypatch.setattr(
        "monsteriser_monster_generator.systems.dnd5e.calculations.challenge_rating.CHALLENGE_RATING_POLICY",
        policy,
    )

    average, final = combine_challenge_ratings(
        offensive_challenge_rating=4,
        defensive_challenge_rating=5,
        reference=REFERENCE,
    )

    assert average == 4.25
    assert final == 4.0


def test_calculate_monster_challenge_rating() -> None:
    """Calculate final CR from offensive and defensive CR."""
    bite = AttackAction(
        action_id="bite",
        name="Bite",
        origin="natural",
        attack_range="melee",
        attack_bonus=3,
        damage=(DamageRoll(dice_count=2, die_size=6, damage_type="piercing", modifier=5),),
    )

    monster = BaseMonster(
        name="Test Monster",
        hitpoints=30,
        dexterity=18,
        expected_cr=1,
        abilities=[bite],
    )

    result = calculate_monster_challenge_rating(
        monster=monster,
        reference=REFERENCE,
    )

    assert result.offensive.challenge_rating == 1
    assert result.defensive.challenge_rating == 1
    assert result.average_challenge_rating == 1.0
    assert result.challenge_rating == 1
