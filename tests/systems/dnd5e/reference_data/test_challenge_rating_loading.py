"""Test loading the challenge rating reference data for D&D 5E 2024."""

from pathlib import Path

import polars as pl
from pytest import raises

from monsteriser_monster_generator.systems.dnd5e.reference_data import (
    ChallengeRatingReference,
    load_challenge_rating_reference,
)

VALID_REFERENCE_CSV = """\
challenge_rating,armor_class,save_bonus,hit_points_min,hit_points_max,attack_bonus,save_dc,dpr_min,dpr_max,dpr_legend_min,dpr_legend_max
1,14,1,20,36,5,13,12,17,15,21
2,15,1,37,54,5,13,18,23,22,28
"""


def _generate_temp_csv(tmp_path: Path) -> Path:
    """Generate a valid reference CSV.

    Returns:
        Path to generated CSV.

    """
    filepath = tmp_path / "baseline_stats.csv"
    filepath.write_text(
        VALID_REFERENCE_CSV,
        encoding="utf-8",
    )
    return filepath


def test_load_challenge_rating_reference(tmp_path: Path) -> None:
    """Load valid challenge-rating reference data."""
    filepath = _generate_temp_csv(tmp_path)

    result = load_challenge_rating_reference(filepath=filepath)

    assert isinstance(result, ChallengeRatingReference)

    assert result.reference.height == 2

    assert result.reference.columns == [
        "challenge_rating",
        "armor_class",
        "save_bonus",
        "hit_points_min",
        "hit_points_max",
        "attack_bonus",
        "save_dc",
        "dpr_min",
        "dpr_max",
        "dpr_legend_min",
        "dpr_legend_max",
    ]


def test_load_challenge_rating_reference_enforces_integer_schema(
    tmp_path: Path,
) -> None:
    """Load reference columns as integer data."""
    filepath = _generate_temp_csv(tmp_path)

    result = load_challenge_rating_reference(filepath=filepath)

    assert result.reference.schema == {
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


def test_load_challenge_rating_rejects_missing_file(
    tmp_path: Path,
) -> None:
    """Raise when the reference file does not exist."""
    filepath = tmp_path / "missing.csv"

    with raises(
        FileNotFoundError,
        match="Challenge-rating reference file not found",
    ):
        load_challenge_rating_reference(filepath)


def test_load_challenge_rating_reference_rejects_non_numeric_dpr(
    tmp_path: Path,
) -> None:
    """Reject text in a numeric DPR column."""
    filepath = tmp_path / "baseline_stats.csv"
    filepath.write_text(
        """\
challenge_rating,armor_class,save_bonus,hit_points_min,hit_points_max,attack_bonus,save_dc,dpr_min,dpr_max,dpr_legend_min,dpr_legend_max
1,14,1,20,36,5,13,12,Jan.00,15,21
""",
        encoding="utf-8",
    )

    with raises(pl.exceptions.PolarsError):
        load_challenge_rating_reference(filepath)


def test_load_challenge_rating_reference_rejects_missing_column(
    tmp_path: Path,
) -> None:
    """Reject a reference missing a required column."""
    filepath = tmp_path / "baseline_stats.csv"
    filepath.write_text(
        """\
challenge_rating,armor_class,save_bonus,hit_points_min,hit_points_max,save_dc,dpr_min,dpr_max,dpr_legend_min,dpr_legend_max
1,14,1,20,36,13,12,17,15,21
""",
        encoding="utf-8",
    )

    with raises(
        ValueError,
        match=("Challenge-rating reference is missing columns: attack_bonus"),
    ):
        load_challenge_rating_reference(filepath)


def test_load_challenge_rating_reference_rejects_unexpected_column(
    tmp_path: Path,
) -> None:
    """Reject unexpected reference columns."""
    filepath = tmp_path / "baseline_stats.csv"
    filepath.write_text(
        """\
challenge_rating,armor_class,save_bonus,hit_points_min,hit_points_max,attack_bonus,save_dc,dpr_min,dpr_max,dpr_legend_min,dpr_legend_max,notes
1,14,1,20,36,5,13,12,17,15,21,first
2,15,1,37,54,5,13,18,23,22,28,second
""",
        encoding="utf-8",
    )

    with raises(
        ValueError,
        match=("Challenge-rating reference contains unexpected columns: notes"),
    ):
        load_challenge_rating_reference(filepath)
