"""Define actions available to monsters."""

from dataclasses import dataclass, field
from typing import Literal

from .model_types import DamageType

type ActionCategory = Literal["attack", "multiattack", "special", "spellcasting"]

type AttackRange = Literal["melee", "ranged", "melee_or_range"]


@dataclass(kw_only=True, frozen=True, slots=True)
class DamageRoll:
    """One damage component of an attack"""

    dice_count: int
    die_size: int
    modifier: int = 0
    damage_type: DamageType

    def average_damage(self) -> float:
        """The average damage from one damage role."""
        average_die = (self.die_size + 1) / 2

        return self.dice_count * average_die + self.modifier


@dataclass(kw_only=True, frozen=True, slots=True)
class MonsterAction:
    """An action availabel to a monster."""

    action_id: str
    name: str
    category: ActionCategory
    description: str = ""


@dataclass(kw_only=True, frozen=True, slots=True)
class AttackAction(MonsterAction):
    """A monster action that deals damage.

    This allows for a single attact that can have different die rolls for different damage types.
    """

    category: Literal["attack"] = field(default="attack", init=False)
    attack_range: AttackRange
    attack_bonus: int
    damage: tuple[DamageRoll, ...]
    reach: int | None = None
    normal_range: int | None = None
    long_range: int | None = None

    def average_damage(self) -> float:
        """The average damage of the attack."""
        return sum(damage_roll.average_damage() for damage_roll in self.damage)
