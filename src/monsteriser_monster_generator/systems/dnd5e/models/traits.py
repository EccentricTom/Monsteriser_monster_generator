"""Define structured monster traits for D&D 5E 2024."""

from dataclasses import dataclass

from dataclasses_json import dataclass_json

from ..models.actions.effects import DamageRoll


@dataclass_json
@dataclass(kw_only=True, frozen=True, slots=True)
class MonsterTrait:
    """Base class for structured monster traits."""


@dataclass_json
@dataclass(kw_only=True, frozen=True, slots=True)
class RegenerationTrait(MonsterTrait):
    """Represent hit points regained automatically each round."""

    hit_points_per_round: int

    def __post_init__(self) -> None:
        """Validate regeneration values."""
        if self.hit_points_per_round <= 0:
            raise ValueError("Regeneration hit points per round must be positive")


@dataclass_json
@dataclass(kw_only=True, frozen=True, slots=True)
class LegendaryResistanceTrait(MonsterTrait):
    """Represent a monster's use of legendary resistances."""

    uses: int = 3

    def __post_init__(self) -> None:
        """Validate regeneration values."""
        if self.uses <= 0:
            raise ValueError("Legendary resistance uses must be positive")


@dataclass_json
@dataclass(kw_only=True, frozen=True, slots=True)
class PassiveDamageTrait(MonsterTrait):
    """Represent automatic damage dealt each round."""

    damage: tuple[DamageRoll, ...]
    expected_targets: float = 1.0

    def __post_init__(self) -> None:
        """Validate positive number of expected targets."""
        if self.expected_targets <= 0:
            raise ValueError("Expected targets must be positive")
