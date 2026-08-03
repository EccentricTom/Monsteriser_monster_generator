"""Test armor-class lookups in D&D 5E 2024 reference data."""

import polars as pl
from pytest import raises

from monsteriser_monster_generator.systems.dnd5e.reference_data import (
    ChallengeRatingReference,
)


def test_get_expected_armor_class_returns_matching_value(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Return the expected armor class for a known CR."""
    result = challenge_rating_reference.get_expected_armor_class(
        challenge_rating=1,
    )

    assert result == 14


def test_get_expected_armor_class_returns_value_for_next_cr(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Return the expected armor class for another known CR."""
    result = challenge_rating_reference.get_expected_armor_class(
        challenge_rating=2,
    )

    assert result == 15


def test_get_expected_armor_class_allows_repeated_ac_values(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Allow different CR rows to share the same expected AC."""
    repeated_ac_reference = ChallengeRatingReference(
        reference=challenge_rating_reference.reference.with_columns(
            pl.when(pl.col("challenge_rating") == 2)
            .then(pl.lit(14))
            .otherwise(pl.col("armor_class"))
            .alias("armor_class")
        )
    )

    first_result = repeated_ac_reference.get_expected_armor_class(
        challenge_rating=1,
    )
    second_result = repeated_ac_reference.get_expected_armor_class(
        challenge_rating=2,
    )

    assert first_result == 14
    assert second_result == 14


def test_get_expected_armor_class_rejects_cr_below_reference(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Reject a CR below the available reference rows."""
    with raises(
        ValueError,
        match=("Challenge rating falls outside the challenge-rating reference: 0"),
    ):
        challenge_rating_reference.get_expected_armor_class(
            challenge_rating=0,
        )


def test_get_expected_armor_class_rejects_cr_above_reference(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Reject a CR above the available reference rows."""
    with raises(
        ValueError,
        match=("Challenge rating falls outside the challenge-rating reference: 3"),
    ):
        challenge_rating_reference.get_expected_armor_class(
            challenge_rating=3,
        )


def test_get_expected_armor_class_rejects_negative_cr(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Reject a negative challenge rating."""
    with raises(
        ValueError,
        match=("Challenge rating falls outside the challenge-rating reference: -1"),
    ):
        challenge_rating_reference.get_expected_armor_class(
            challenge_rating=-1,
        )


def test_get_expected_armor_class_rejects_duplicate_cr(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Reject duplicate rows for the requested challenge rating."""
    duplicated_row = challenge_rating_reference.reference.slice(
        offset=0,
        length=1,
    )

    duplicated_reference = ChallengeRatingReference(
        reference=pl.concat(
            [
                challenge_rating_reference.reference,
                duplicated_row,
            ],
            how="vertical",
        )
    )

    with raises(
        ValueError,
        match="Challenge rating is duplicated: 1",
    ):
        duplicated_reference.get_expected_armor_class(
            challenge_rating=1,
        )


def test_get_expected_armor_class_rejects_non_integer_value(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Reject a non-integer armor-class reference value."""
    invalid_reference = ChallengeRatingReference(
        reference=challenge_rating_reference.reference.with_columns(
            pl.when(pl.col("challenge_rating") == 1)
            .then(pl.lit("fourteen"))
            .otherwise(pl.col("armor_class").cast(pl.String))
            .alias("armor_class")
        )
    )

    with raises(
        TypeError,
        match="Armor-class reference value must be an integer",
    ):
        invalid_reference.get_expected_armor_class(
            challenge_rating=1,
        )
