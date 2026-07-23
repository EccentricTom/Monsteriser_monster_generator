"""Expose D&D 5e monster-generation services."""

from .action_selection import (
    ActionSelectionPolicy,
    natural_attack_is_available,
)
from .multiattack_validation import (
    validate_monster_multiattacks,
)

__all__ = [
    "ActionSelectionPolicy",
    "natural_attack_is_available",
    "validate_monster_multiattacks",
]
