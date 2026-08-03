"""Test D&D 5E 2024 challenge-rating reference behaviour."""

import polars as pl
import pytest
from pytest import raises

from monsteriser_monster_generator.systems.dnd5e.reference_data import (
    ChallengeRatingReference,
)


def test_validate_accepts_valid_reference(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Accept valid ordered and contiguous reference data."""
    challenge_rating_reference.validate()


def test_validate_rejects_empty_reference() -> None:
    """Reject an empty challenge-rating reference."""
    reference = ChallengeRatingReference(
        reference=pl.DataFrame(
            schema={
                "challenge_rating": pl.Int64,
                "armor_class": pl.Int64,
                "save_bonus": pl.Int64,
                "hit_points_min": pl.Int64,
                "hit_points_max": pl.Int64,
                "attack_bonus": pl.Int64,
                "save_dc": pl.Int64,
                "dpr_min": pl.Int64,
                "dpr_max": pl.Int64,
                "dpr_legend_min": pl.Int64,
                "dpr_legend_max": pl.Int64,
            }
        ),
    )

    with raises(ValueError, match="Challenge-rating reference cannot be empty"):
        reference.validate()


def test_validate_rejects_duplicate_challenge_rating(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Reject duplicate challenge-rating rows."""
    first_row = challenge_rating_reference.reference.slice(
        offset=0,
        length=1,
    )

    duplicate_reference = ChallengeRatingReference(
        reference=pl.concat(
            [
                first_row,
                first_row,
            ],
            how="vertical",
        ),
    )

    with raises(
        ValueError,
        match="Challenge-rating values must be unique",
    ):
        duplicate_reference.validate()


def test_validate_rejects_unordered_challenge_ratings(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Reject challenge ratings that are not ascending."""
    unordered_reference = ChallengeRatingReference(
        reference=challenge_rating_reference.reference.reverse(),
    )

    with raises(
        ValueError,
        match="Challenge-rating values must be ordered",
    ):
        unordered_reference.validate()


@pytest.mark.parametrize(
    ("minimum_column", "maximum_column"),
    [
        ("hit_points_min", "hit_points_max"),
        ("dpr_min", "dpr_max"),
        ("dpr_legend_min", "dpr_legend_max"),
    ],
)
def test_validate_rejects_inverted_range(
    challenge_rating_reference: ChallengeRatingReference,
    minimum_column: str,
    maximum_column: str,
) -> None:
    """Reject a minimum greater than its corresponding maximum."""
    invalid_dataframe = challenge_rating_reference.reference.with_columns(
        pl.when(pl.col("challenge_rating") == 1)
        .then(pl.col(maximum_column) + 1)
        .otherwise(pl.col(minimum_column))
        .alias(minimum_column)
    )

    invalid_reference = ChallengeRatingReference(
        reference=invalid_dataframe,
    )

    with raises(
        ValueError,
        match="Challenge-rating reference contains invalid ranges",
    ):
        invalid_reference.validate()


def test_validate_rejects_standard_dpr_gap(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Reject gaps between consecutive standard DPR ranges."""
    invalid_dataframe = challenge_rating_reference.reference.with_columns(
        pl.when(pl.col("challenge_rating") == 2)
        .then(pl.lit(19))
        .otherwise(pl.col("dpr_min"))
        .alias("dpr_min")
    )

    invalid_reference = ChallengeRatingReference(
        reference=invalid_dataframe,
    )

    with raises(
        ValueError,
        match="Standard DPR ranges must be contiguous",
    ):
        invalid_reference.validate()


def test_validate_rejects_legendary_dpr_gap(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Reject gaps between consecutive legendary DPR ranges."""
    invalid_dataframe = challenge_rating_reference.reference.with_columns(
        pl.when(pl.col("challenge_rating") == 2)
        .then(pl.lit(23))
        .otherwise(pl.col("dpr_legend_min"))
        .alias("dpr_legend_min")
    )

    invalid_reference = ChallengeRatingReference(
        reference=invalid_dataframe,
    )

    with raises(
        ValueError,
        match="Legendary DPR ranges must be contiguous",
    ):
        invalid_reference.validate()


def test_validate_rejects_standard_dpr_overlap(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Reject overlapping standard DPR ranges."""
    invalid_dataframe = challenge_rating_reference.reference.with_columns(
        pl.when(pl.col("challenge_rating") == 2)
        .then(pl.lit(17))
        .otherwise(pl.col("dpr_min"))
        .alias("dpr_min")
    )

    invalid_reference = ChallengeRatingReference(
        reference=invalid_dataframe,
    )

    with raises(
        ValueError,
        match="Standard DPR ranges must be contiguous",
    ):
        invalid_reference.validate()


def test_validate_rejects_legendary_dpr_overlap(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Reject overlapping legendary DPR ranges."""
    invalid_dataframe = challenge_rating_reference.reference.with_columns(
        pl.when(pl.col("challenge_rating") == 2)
        .then(pl.lit(21))
        .otherwise(pl.col("dpr_legend_min"))
        .alias("dpr_legend_min")
    )

    invalid_reference = ChallengeRatingReference(
        reference=invalid_dataframe,
    )

    with raises(
        ValueError,
        match="Legendary DPR ranges must be contiguous",
    ):
        invalid_reference.validate()


def test_validate_rejects_hit_point_gap(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Reject gaps between consecutive hit-point ranges."""
    invalid_dataframe = challenge_rating_reference.reference.with_columns(
        pl.when(pl.col("challenge_rating") == 2)
        .then(pl.lit(38))
        .otherwise(pl.col("hit_points_min"))
        .alias("hit_points_min")
    )

    invalid_reference = ChallengeRatingReference(
        reference=invalid_dataframe,
    )

    with raises(
        ValueError,
        match="Hit-point ranges must be contiguous",
    ):
        invalid_reference.validate()


def test_validate_rejects_hit_point_overlap(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Reject overlapping hit-point ranges."""
    invalid_dataframe = challenge_rating_reference.reference.with_columns(
        pl.when(pl.col("challenge_rating") == 2)
        .then(pl.lit(36))
        .otherwise(pl.col("hit_points_min"))
        .alias("hit_points_min")
    )

    invalid_reference = ChallengeRatingReference(
        reference=invalid_dataframe,
    )

    with raises(
        ValueError,
        match="Hit-point ranges must be contiguous",
    ):
        invalid_reference.validate()
