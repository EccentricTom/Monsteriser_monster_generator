"""Test D&D 5E 2024 challenge-rating reference behaviour."""

import polars as pl
import pytest
from pytest import raises

from monsteriser_monster_generator.systems.dnd5e.reference_data import (
    ChallengeRatingReference,
)


def create_reference(
    rows: list[dict[str, int]] | None = None,
) -> ChallengeRatingReference:
    """Create a small challenge-rating reference for tests."""
    reference_rows = rows or [
        {
            "challenge_rating": 1,
            "armor_class": 14,
            "save_bonus": 1,
            "hit_points_min": 20,
            "hit_points_max": 36,
            "attack_bonus": 5,
            "save_dc": 13,
            "dpr_min": 12,
            "dpr_max": 17,
            "dpr_legend_min": 15,
            "dpr_legend_max": 21,
        },
        {
            "challenge_rating": 2,
            "armor_class": 15,
            "save_bonus": 1,
            "hit_points_min": 37,
            "hit_points_max": 54,
            "attack_bonus": 5,
            "save_dc": 13,
            "dpr_min": 18,
            "dpr_max": 23,
            "dpr_legend_min": 22,
            "dpr_legend_max": 28,
        },
    ]

    return ChallengeRatingReference(
        reference=pl.DataFrame(reference_rows),
    )


def test_validate_accepts_valid_refence() -> None:
    """Accept valid ordered and contiguous reference data."""
    reference = create_reference()

    reference.validate()


def test_validate_reject_empty_reference() -> None:
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


def test_validate_rejects_duplicate_challenge_rating() -> None:
    """Reject duplicate challenge-rating rows."""
    reference = create_reference(
        rows=[
            {
                **create_reference().reference.row(
                    0,
                    named=True,
                ),
            },
            {
                **create_reference().reference.row(
                    0,
                    named=True,
                ),
            },
        ]
    )

    with raises(
        ValueError,
        match="Challenge-rating values must be unique",
    ):
        reference.validate()


def test_validate_rejects_unordered_challenge_ratings() -> None:
    """Reject challenge ratings that are not ascending."""
    valid_reference = create_reference()

    reference = ChallengeRatingReference(
        reference=valid_reference.reference.reverse(),
    )

    with raises(
        ValueError,
        match="Challenge-rating values must be ordered",
    ):
        reference.validate()


@pytest.mark.parametrize(
    ("minimum_column", "maximum_column"),
    [
        ("hit_points_min", "hit_points_max"),
        ("dpr_min", "dpr_max"),
        ("dpr_legend_min", "dpr_legend_max"),
    ],
)
def test_validate_rejects_inverted_range(
    minimum_column: str,
    maximum_column: str,
) -> None:
    """Reject a minimum greater than its corresponding maximum."""
    reference = create_reference()

    invalid_dataframe = reference.reference.with_columns(
        pl.when(pl.col("challenge_rating") == 1)
        .then(pl.col(maximum_column) + 1)
        .otherwise(pl.col(minimum_column))
        .alias(minimum_column)
    )

    with raises(
        ValueError,
        match=("Challenge-rating reference contains invalid ranges"),
    ):
        ChallengeRatingReference(
            reference=invalid_dataframe,
        ).validate()


def test_validate_rejects_standard_dpr_gap() -> None:
    """Reject gaps between consecutive standard DPR ranges."""
    reference = create_reference()

    invalid_dataframe = reference.reference.with_columns(
        pl.when(pl.col("challenge_rating") == 2)
        .then(pl.lit(19))
        .otherwise(pl.col("dpr_min"))
        .alias("dpr_min")
    )

    with raises(
        ValueError,
        match="Standard DPR ranges must be contiguous",
    ):
        ChallengeRatingReference(
            reference=invalid_dataframe,
        ).validate()


def test_validate_rejects_legendary_dpr_gap() -> None:
    """Reject gaps between consecutive legendary DPR ranges."""
    reference = create_reference()

    invalid_dataframe = reference.reference.with_columns(
        pl.when(pl.col("challenge_rating") == 2)
        .then(pl.lit(19))
        .otherwise(pl.col("dpr_legend_min"))
        .alias("dpr_legend_min")
    )

    with raises(
        ValueError,
        match="Legendary DPR ranges must be contiguous",
    ):
        ChallengeRatingReference(
            reference=invalid_dataframe,
        ).validate()


def test_validate_rejects_standard_dpr_overlap() -> None:
    """Reject overlapping standard DPR ranges."""
    reference = create_reference()

    invalid_dataframe = reference.reference.with_columns(
        pl.when(pl.col("challenge_rating") == 2)
        .then(pl.lit(17))
        .otherwise(pl.col("dpr_min"))
        .alias("dpr_min")
    )

    with raises(
        ValueError,
        match="Standard DPR ranges must be contiguous",
    ):
        ChallengeRatingReference(
            reference=invalid_dataframe,
        ).validate()


def test_validate_rejects_legendary_dpr_overlap() -> None:
    """Reject overlapping legendary DPR ranges."""
    reference = create_reference()

    invalid_dataframe = reference.reference.with_columns(
        pl.when(pl.col("challenge_rating") == 2)
        .then(pl.lit(17))
        .otherwise(pl.col("dpr_legend_min"))
        .alias("dpr_legend_min")
    )

    with raises(
        ValueError,
        match="Legendary DPR ranges must be contiguous",
    ):
        ChallengeRatingReference(
            reference=invalid_dataframe,
        ).validate()


def test_get_reference_base_excludes_legendary_columns() -> None:
    """Remove legendary DPR columns from the base reference."""
    reference = create_reference()

    result = reference.get_reference_base()

    assert "dpr_legend_min" not in result.columns
    assert "dpr_legend_max" not in result.columns
    assert result.height == 2


def test_get_legendary_reference_selects_expected_columns() -> None:
    """Return CR and legendary DPR columns."""
    reference = create_reference()

    result = reference.get_legendary_reference()

    assert "dpr_min" not in result.columns
    assert "dpr_max" not in result.columns
    assert result.height == 2


def test_get_offensive_cr_matches_standard_lower_boundary() -> None:
    """Match a standard DPR band's lower boundary."""
    reference = create_reference()

    result = reference.get_offensive_cr(12.0)

    assert result == 1


def test_get_offensive_cr_matches_standard_upper_boundary() -> None:
    """Match a standard DPR band's upper boundary."""
    reference = create_reference()

    result = reference.get_offensive_cr(17.0)

    assert result == 1


def test_get_offensive_cr_matches_next_standard_band() -> None:
    """Move to the next CR after crossing a DPR boundary."""
    reference = create_reference()

    result = reference.get_offensive_cr(18.0)

    assert result == 2


def test_get_offensive_cr_accepts_fractional_damage() -> None:
    """Match fractional average damage within an integer band."""
    reference = create_reference()

    result = reference.get_offensive_cr(16.5)

    assert result == 1


def test_get_offensive_cr_uses_legendary_ranges() -> None:
    """Use legendary DPR ranges when requested."""
    reference = create_reference()

    result = reference.get_offensive_cr(
        22.0,
        legendary=True,
    )

    assert result == 2


def test_get_offensive_cr_rejects_negative_damage() -> None:
    """Reject negative damage values."""
    reference = create_reference()

    with raises(
        ValueError,
        match="Damage per round cannot be negative",
    ):
        reference.get_offensive_cr(-1.0)


def test_get_offensive_cr_rejects_damage_below_reference() -> None:
    """Reject damage below the first available CR band."""
    reference = create_reference()

    with raises(
        ValueError,
        match=("Damage per round falls outside the challenge-rating reference"),
    ):
        reference.get_offensive_cr(11.0)


def test_get_offensive_cr_rejects_damage_above_reference() -> None:
    """Reject damage above the final available CR band."""
    reference = create_reference()

    with raises(
        ValueError,
        match=("Damage per round falls outside the challenge-rating reference"),
    ):
        reference.get_offensive_cr(24.0)


def test_get_offensive_cr_rejects_multiple_matches() -> None:
    """Reject lookup when overlapping bands match the same DPR."""
    reference = create_reference()
    overlapping = reference.reference.with_columns(
        pl.when(pl.col("challenge_rating") == 2)
        .then(pl.lit(17))
        .otherwise(pl.col("dpr_min"))
        .alias("dpr_min")
    )

    invalid_reference = ChallengeRatingReference(
        reference=overlapping,
    )

    with raises(
        ValueError,
        match="Damage per round matched multiple CR bands",
    ):
        invalid_reference.get_offensive_cr(17.0)
