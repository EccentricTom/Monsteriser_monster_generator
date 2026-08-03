"""Load and expose reference data."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict, cast

import polars as pl

SYSTEM_DIRECTORY = Path(__file__).resolve().parent
DATA_DIRECTORY = SYSTEM_DIRECTORY / "data" / "fifth_edition"

CHALLENGE_RATING_FILE = DATA_DIRECTORY / "baseline_stats.csv"
GEAR_FILE = DATA_DIRECTORY / "gear.json"

CHALLENGE_RATING_SCHEMA = {
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

type ReferenceEntry = dict[str, object]
type ReferenceGroup = dict[str, ReferenceEntry]


class WeaponReferences(TypedDict):
    """Contain melee and ranged weapon-reference data."""

    melee: ReferenceGroup
    ranged: ReferenceGroup


class GearReferenceData(TypedDict):
    """Describe the expected structure of the gear-reference file."""

    weapons: WeaponReferences
    armor: ReferenceGroup


@dataclass(frozen=True, slots=True)
class ChallengeRatingReference:
    """Provide access to challenge-rating reference statistics."""

    reference: pl.DataFrame

    def validate(self) -> None:
        """Validate the challenge-rating reference data.

        Raises:
            ValueError: If columns, ranges, or CR ordering are invalid.

        """
        self._validate_columns()
        self._validate_challenge_ratings()
        self._validate_ranges()
        self._validate_dpr_continuity()

    def get_reference_base(self) -> pl.DataFrame:
        """Return the reference without legendary damage columns."""
        return self.reference.drop(
            "dpr_legend_min",
            "dpr_legend_max",
        )

    def get_legendary_reference(self) -> pl.DataFrame:
        """Return the reference without standard damage columns."""
        return self.reference.drop(
            "dpr_min",
            "dpr_max",
        )

    def _validate_columns(self) -> None:
        """Validate that all required columns are present."""
        expected_columns = set(CHALLENGE_RATING_SCHEMA)
        actual_columns = set(self.reference.columns)

        missing_columns = expected_columns - actual_columns
        unexpected_columns = actual_columns - expected_columns

        if missing_columns:
            missing_text = ", ".join(sorted(missing_columns))
            raise ValueError(f"Challenge-rating reference is missing columns: {missing_text}")

        if unexpected_columns:
            unexpected_text = ", ".join(sorted(unexpected_columns))
            raise ValueError(
                f"Challenge-rating reference contains unexpected columns: {unexpected_text}"
            )

    def _validate_challenge_ratings(self) -> None:
        """Validate that CR values are unique and ordered."""
        challenge_ratings = self.reference["challenge_rating"].to_list()

        if not challenge_ratings:
            raise ValueError("Challenge-rating reference cannot be empty")

        if len(challenge_ratings) != len(set(challenge_ratings)):
            raise ValueError("Challenge-rating values must be unique")

        if challenge_ratings != sorted(challenge_ratings):
            raise ValueError("Challenge-rating values must be ordered")

    def _validate_ranges(self) -> None:
        """Validate that all minimum values are within their ranges."""
        invalid_rows = self.reference.filter(
            (pl.col("hit_points_min") > pl.col("hit_points_max"))
            | (pl.col("dpr_min") > pl.col("dpr_max"))
            | (pl.col("dpr_legend_min") > pl.col("dpr_legend_max"))
        )

        if not invalid_rows.is_empty():
            raise ValueError("Challenge-rating reference contains invalid ranges")

    def _validate_dpr_continuity(self) -> None:
        """Validate that DPR ranges have no gaps or overlaps."""
        ordered_reference = self.reference.sort("challenge_rating")

        standard_gaps = ordered_reference.select(
            (pl.col("dpr_min") - pl.col("dpr_max").shift(1)).alias("difference")
        ).drop_nulls()

        if standard_gaps.filter(pl.col("difference") != 1).height:
            raise ValueError("Standard DPR ranges must be contiguous")

        legendary_gaps = ordered_reference.select(
            (pl.col("dpr_legend_min") - pl.col("dpr_legend_max").shift(1)).alias("difference")
        ).drop_nulls()

        if legendary_gaps.filter(pl.col("difference") != 1).height:
            raise ValueError("Legendary DPR ranges must be contiguous")

    def get_dpr_band(
        self,
        damage_per_round: float,
        *,
        legendary: bool = False,
    ) -> pl.DataFrame:
        """Return the CR row containing the supplied DPR.

        Args:
            damage_per_round: Average damage per round.
            legendary: Whether to use legendary DPR ranges.

        Returns:
            A single-row DataFrame containing the matching CR band.

        Raises:
            ValueError: If damage is negative or outside the table.

        """
        if damage_per_round < 0:
            raise ValueError("Damage per round cannot be negative")

        minimum_column = "dpr_legend_min" if legendary else "dpr_min"
        maximum_column = "dpr_legend_max" if legendary else "dpr_max"

        matching_rows = self.reference.filter(
            pl.col(minimum_column) <= damage_per_round,
            pl.col(maximum_column) >= damage_per_round,
        )

        if matching_rows.is_empty():
            raise ValueError(
                f"Damage per round falls outside the challenge-rating reference: {damage_per_round}"
            )

        if matching_rows.height > 1:
            raise ValueError(f"Damage per round matched multiple CR bands: {damage_per_round}")

        return matching_rows

    def get_offensive_cr(
        self,
        damage_per_round: float,
        *,
        legendary: bool = False,
    ) -> int:
        """Return the challenge rating associated with a DPR value."""
        matching_band = self.get_dpr_band(
            damage_per_round,
            legendary=legendary,
        )

        challenge_rating = matching_band.item(
            0,
            "challenge_rating",
        )

        if not isinstance(challenge_rating, int):
            raise TypeError("Challenge-rating value must be an integer")

        return challenge_rating

    def get_hit_point_band(self, hit_points: float) -> pl.DataFrame:
        """Return the CR row containing the supplied hit points.

        Args:
            hit_points: Hitpoints of the monster to reference.

        Returns:
            A single-row DataFrame containing the matching CR band.

        Raises:
            ValueError: If hit_points are negative or outside the table.

        """
        if hit_points < 0:
            raise ValueError("Hitpoints cannot be negative")

        matching_rows = self.reference.filter(
            pl.col("hit_points_min") <= hit_points,
            pl.col("hit_points_max") >= hit_points,
        )

        if matching_rows.is_empty():
            raise ValueError(f"Hitpoints fall outside the challenge-rating reference: {hit_points}")

        if matching_rows.height > 1:
            raise ValueError(f"Hitpoints matched multiple CR bands: {hit_points}")

        return matching_rows


def load_challenge_rating_reference(
    filepath: Path = CHALLENGE_RATING_FILE,
) -> ChallengeRatingReference:
    """Load challenge-rating reference data from a CSV file.

    Args:
        filepath: Path to the challenge-rating reference CSV file.

    Returns: An immutable challenge-rating reference object.

    Raises: FileNotFoundError: If the reference file does not exist. pl.exceptions.PolarsError: If Polars cannot parse the CSV file.

    """
    if not filepath.is_file():
        raise FileNotFoundError(f"Challenge-rating reference file not found: {filepath}")

    reference = pl.read_csv(
        filepath,
        schema_overrides=CHALLENGE_RATING_SCHEMA,
    )

    challenge_rating_reference = ChallengeRatingReference(
        reference=reference,
    )
    challenge_rating_reference.validate()

    return challenge_rating_reference


@dataclass(frozen=True, slots=True)
class GearReference:
    """Provide access to weapon and armor reference data."""

    full_reference: GearReferenceData

    def get_melee_gear_reference(self) -> ReferenceGroup:
        """Return all melee weapon-reference entries."""
        return self.full_reference["weapons"]["melee"]

    def get_ranged_gear_reference(self) -> ReferenceGroup:
        """Return all ranged weapon-reference entries."""
        return self.full_reference["weapons"]["ranged"]

    def get_armor_gear_reference(self) -> ReferenceGroup:
        """Return all armor-reference entries."""
        return self.full_reference["armor"]


def load_gear_reference(
    filepath: Path = GEAR_FILE,
) -> GearReference:
    """Load gear-reference data from a JSON file.

    Args:
        filepath: Path to the gear-reference JSON file.

        Returns: An immutable gear-reference object.

    Raises:
            FileNotFoundError: If the reference file does not exist.
            json.JSONDecodeError: If the file does not contain valid JSON.
            TypeError: If the top-level JSON value is not an object.

    """
    if not filepath.is_file():
        raise FileNotFoundError(f"Gear reference file not found: {filepath}")
    raw_reference: object = json.loads(filepath.read_text(encoding="utf-8"))
    if not isinstance(raw_reference, dict):
        raise TypeError("The gear reference must contain a JSON object")

    reference = cast(GearReferenceData, raw_reference)

    return GearReference(full_reference=reference)
