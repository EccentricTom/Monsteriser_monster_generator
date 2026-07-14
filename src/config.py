"""Load and expose reference data."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict, cast

import polars as pl

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIRECTORY = PROJECT_ROOT / "data" / "fifth_edition"

CHALLENGE_RATING_FILE = DATA_DIRECTORY / "baseline_stats.csv"
GEAR_FILE = DATA_DIRECTORY / "gear.json"

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

    def get_reference_base(self) -> pl.DataFrame:
        """Return the reference without legendary damage columns."""
        return self.reference.drop(
            "dpr_legend_min",
            "dpr_legend_max",
        )

    def get_legendary_reference(self) -> pl.DataFrame:
        """Return challenge-rating and legendary damage columns."""
        return self.reference.select(
            "challenge_rating",
            "dpr_legend_min",
            "dpr_legend_max",
        )


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
    reference = pl.read_csv(filepath)
    return ChallengeRatingReference(reference=reference)


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
