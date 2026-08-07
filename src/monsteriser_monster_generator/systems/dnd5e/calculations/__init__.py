"""Expose D&D 5E combat calculations."""

from .combat_routines import (
    TurnRoutine,
    generate_repeatable_turn_routines,
    generate_turn_routines,
)
from .defensive import (
    DefensiveChallengeRatingResult,
    DefensiveHealthResult,
    calculate_effective_hit_points,
    calculate_monster_defensive_cr,
)
from .offensive import (
    OffensiveChallengeRatingResult,
    OffensiveDamageResult,
    calculate_monster_offensive_cr,
    calculate_monster_offensive_damage,
)

__all__ = [
    "DefensiveChallengeRatingResult",
    "DefensiveHealthResult",
    "OffensiveChallengeRatingResult",
    "OffensiveDamageResult",
    "TurnRoutine",
    "calculate_effective_hit_points",
    "calculate_monster_defensive_cr",
    "calculate_monster_offensive_cr",
    "calculate_monster_offensive_damage",
    "generate_repeatable_turn_routines",
    "generate_turn_routines",
]
