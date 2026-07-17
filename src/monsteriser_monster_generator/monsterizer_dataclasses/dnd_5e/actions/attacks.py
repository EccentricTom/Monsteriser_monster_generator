"""Define attack-roll and saving-throw actions."""

from dataclasses import dataclass, field
from typing import Literal

from ..model_types import AttackRange
from .base import MonsterAction
from .effects import ConditionEffect, DamageRoll, SavingThrowDamage


@dataclass(kw_only=True, frozen=True, slots=True)
class AttackAction(MonsterAction):
    """A monster action that deals damage.

    This allows for a single attact that can have different die rolls for different damage types.
    """

    category: Literal["attack"] = field(
        default="attack",
        init=False,
    )

    attack_range: AttackRange
    attack_bonus: int
    damage: tuple[DamageRoll, ...]

    conditions: tuple[ConditionEffect, ...] = ()

    reach_ft: float | None = None
    reach_m: float | None = None
    normal_range_ft: float | None = None
    long_range_ft: float | None = None
    normal_range_m: float | None = None
    long_range_m: float | None = None

    def average_damage(self) -> float:
        """Average damage of the attack."""
        return sum(damage_roll.average_damage() for damage_roll in self.damage)


@dataclass(kw_only=True, frozen=True, slots=True)
class SavingThrowAction(MonsterAction):
    """Represent an action resolved with a saving throw."""

    category: Literal["saving_throw"] = field(
        default="saving_throw",
        init=False,
    )

    saving_throw: SavingThrowDamage
    conditions: tuple[ConditionEffect, ...] = ()

    area_description: str | None = None
    expected_targets: float = 1.0

    def __post_init__(self) -> None:
        """Validate the expected target count."""
        if self.expected_targets < 1:
            raise ValueError("Must have at least one expected target.")
