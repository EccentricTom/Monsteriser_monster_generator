"""Define effects produced by monster actions."""

from dataclasses import dataclass

from ..model_types import (
    AbilityName,
    ConditionName,
    DamageType,
    SavingThrowOutcome,
)


@dataclass(kw_only=True, frozen=True, slots=True)
class DamageRoll:
    """One damage component of an attack."""

    dice_count: int
    die_size: int
    modifier: int = 0
    damage_type: DamageType

    def __post_init__(self) -> None:
        """Validate the damage dice."""
        if self.dice_count < 1:
            raise ValueError("Damage dice count must be positive")
        if self.die_size < 1:
            raise ValueError("Damage die size must be positive")

    def average_damage(self) -> float:
        """Average damage from one damage role."""
        average_die = (self.die_size + 1) / 2

        return self.dice_count * average_die + self.modifier


@dataclass(kw_only=True, frozen=True, slots=True)
class ConditionEffect:
    """Represent a condition imposed by an ability."""

    condition: ConditionName
    duration: str
    escape_difficulty_class: int | None = None


@dataclass(kw_only=True, frozen=True, slots=True)
class SavingThrowDamage:
    """Represent damage resolved through a saving throw instead of attack action."""

    ability: AbilityName
    difficulty_class: int
    damage: tuple[DamageRoll, ...]
    success_outcome: SavingThrowOutcome = "none"

    def average_failed_save(self) -> float:
        """Return the average damage on a failed save."""
        return sum(roll.average_damage() for roll in self.damage)

    def average_successful_save(self) -> float:
        """Return the average damage on a successful save."""
        if self.success_outcome == "half":
            return sum(roll.average_damage() for roll in self.damage) / 2
        return 0.0
