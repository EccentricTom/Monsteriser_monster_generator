"""Test defensive CR lookups in D&D 5E 2024 reference data."""

import polars as pl
from pytest import raises

from monsteriser_monster_generator.systems.dnd5e.reference_data import (
    ChallengeRatingReference,
)


def test_get_hit_point_cr_matches_lower_boundary(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Match a hit-point band's lower boundary."""
    result = challenge_rating_reference.get_hit_point_cr(20.0)

    assert result == 1


def test_get_hit_point_cr_matches_upper_boundary(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Match a hit-point band's upper boundary."""
    result = challenge_rating_reference.get_hit_point_cr(36.0)

    assert result == 1


def test_get_hit_point_cr_matches_next_band(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Move to the next CR after crossing an HP boundary."""
    result = challenge_rating_reference.get_hit_point_cr(37.0)

    assert result == 2


def test_get_hit_point_cr_accepts_fractional_hit_points(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Match fractional effective HP within an integer band."""
    result = challenge_rating_reference.get_hit_point_cr(35.5)

    assert result == 1


def test_get_hit_point_cr_rejects_negative_hit_points(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Reject negative hit-point values."""
    with raises(
        ValueError,
        match="Hit points cannot be negative",
    ):
        challenge_rating_reference.get_hit_point_cr(-1.0)


def test_get_hit_point_cr_rejects_hit_points_below_reference(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Reject hit points below the first available CR band."""
    with raises(
        ValueError,
        match=("Hit points fall outside the challenge-rating reference"),
    ):
        challenge_rating_reference.get_hit_point_cr(19.0)


def test_get_hit_point_cr_rejects_hit_points_above_reference(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Reject hit points above the final available CR band."""
    with raises(
        ValueError,
        match=("Hit points fall outside the challenge-rating reference"),
    ):
        challenge_rating_reference.get_hit_point_cr(55.0)


def test_get_hit_point_cr_rejects_zero_hit_points_below_reference(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Reject zero HP when the reference has no matching band."""
    with raises(
        ValueError,
        match=("Hit points fall outside the challenge-rating reference"),
    ):
        challenge_rating_reference.get_hit_point_cr(0.0)


def test_get_hit_point_cr_rejects_multiple_matches(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Reject lookup when overlapping HP bands match one value."""
    overlapping = challenge_rating_reference.reference.with_columns(
        pl.when(pl.col("challenge_rating") == 2)
        .then(pl.lit(36))
        .otherwise(pl.col("hit_points_min"))
        .alias("hit_points_min")
    )

    invalid_reference = ChallengeRatingReference(
        reference=overlapping,
    )

    with raises(
        ValueError,
        match="Hit points matched multiple CR bands",
    ):
        invalid_reference.get_hit_point_cr(36.0)
