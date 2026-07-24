"""Expose D&D 5E combat calculations."""

from .combat_routines import TurnRoutine, generate_turn_routines
from .damage import (
    calculate_action_average_damage,
    calculate_multiattack_routine_damage,
    calculate_turn_routine_damage,
    find_maximum_damage_multiattack_routine,
    find_maximum_damage_turn,
    find_monster_maximum_damage_turn,
)

__all__ = [
    "TurnRoutine",
    "calculate_action_average_damage",
    "calculate_multiattack_routine_damage",
    "calculate_turn_routine_damage",
    "find_maximum_damage_multiattack_routine",
    "find_maximum_damage_turn",
    "find_monster_maximum_damage_turn",
    "generate_turn_routines",
]
