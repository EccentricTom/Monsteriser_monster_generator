"""Provide fixtures for D&D 5E reference-data tests."""

import polars as pl
import pytest

from monsteriser_monster_generator.systems.dnd5e.reference_data import (
    ChallengeRatingReference,
)


@pytest.fixture
def challenge_rating_reference() -> ChallengeRatingReference:
    """Create a small valid challenge-rating reference."""
    return ChallengeRatingReference(
        reference=pl.DataFrame(
            [
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
        )
    )
