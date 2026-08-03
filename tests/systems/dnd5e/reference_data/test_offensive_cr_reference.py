"""Test D&D 5E 2024 challenge-rating reference behaviour."""

import polars as pl
from pytest import raises

from monsteriser_monster_generator.systems.dnd5e.reference_data import (
    ChallengeRatingReference,
)


def test_get_reference_base_excludes_legendary_columns(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Remove legendary DPR columns from the base reference."""
    result = challenge_rating_reference.get_reference_base()

    assert "dpr_legend_min" not in result.columns
    assert "dpr_legend_max" not in result.columns
    assert "dpr_min" in result.columns
    assert "dpr_max" in result.columns
    assert result.height == 2


def test_get_legendary_reference_excludes_standard_dpr_columns(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Remove standard DPR columns from the legendary reference."""
    result = challenge_rating_reference.get_legendary_reference()

    assert "dpr_min" not in result.columns
    assert "dpr_max" not in result.columns
    assert "dpr_legend_min" in result.columns
    assert "dpr_legend_max" in result.columns
    assert result.height == 2


def test_get_offensive_cr_matches_standard_lower_boundary(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Match a standard DPR band's lower boundary."""
    result = challenge_rating_reference.get_offensive_cr(12.0)

    assert result == 1


def test_get_offensive_cr_matches_standard_upper_boundary(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Match a standard DPR band's upper boundary."""
    result = challenge_rating_reference.get_offensive_cr(17.0)

    assert result == 1


def test_get_offensive_cr_matches_next_standard_band(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Move to the next CR after crossing a DPR boundary."""
    result = challenge_rating_reference.get_offensive_cr(18.0)

    assert result == 2


def test_get_offensive_cr_accepts_fractional_damage(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Match fractional average damage within an integer band."""
    result = challenge_rating_reference.get_offensive_cr(16.5)

    assert result == 1


def test_get_offensive_cr_uses_legendary_ranges(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Use legendary DPR ranges when requested."""
    result = challenge_rating_reference.get_offensive_cr(
        22.0,
        legendary=True,
    )

    assert result == 2


def test_get_offensive_cr_uses_different_standard_and_legendary_bands(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Return different CRs when standard and legendary bands differ."""
    standard_result = challenge_rating_reference.get_offensive_cr(
        18.0,
    )
    legendary_result = challenge_rating_reference.get_offensive_cr(
        18.0,
        legendary=True,
    )

    assert standard_result == 2
    assert legendary_result == 1


def test_get_offensive_cr_rejects_negative_damage(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Reject negative damage values."""
    with raises(
        ValueError,
        match="Damage per round cannot be negative",
    ):
        challenge_rating_reference.get_offensive_cr(-1.0)


def test_get_offensive_cr_rejects_damage_below_reference(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Reject damage below the first available CR band."""
    with raises(
        ValueError,
        match=("Damage per round falls outside the challenge-rating reference"),
    ):
        challenge_rating_reference.get_offensive_cr(11.0)


def test_get_offensive_cr_rejects_damage_above_reference(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Reject damage above the final available CR band."""
    with raises(
        ValueError,
        match=("Damage per round falls outside the challenge-rating reference"),
    ):
        challenge_rating_reference.get_offensive_cr(24.0)


def test_get_offensive_cr_rejects_multiple_matches(
    challenge_rating_reference: ChallengeRatingReference,
) -> None:
    """Reject lookup when overlapping bands match the same DPR."""
    overlapping = challenge_rating_reference.reference.with_columns(
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
