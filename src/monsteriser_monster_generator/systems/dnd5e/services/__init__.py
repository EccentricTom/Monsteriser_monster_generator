"""Expose D&D 5e monster-generation services."""

from .action_selection import (
    ActionSelectionPolicy,
    natural_attack_is_available,
)

__all__ = [
    "ActionSelectionPolicy",
    "natural_attack_is_available",
]
