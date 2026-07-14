"""Define monster damage resistance models."""

from dataclasses import dataclass, field
from typing import ClassVar

from dataclasses_json import dataclass_json

from .model_types import DamageType

# Damage adjustment


@dataclass_json
@dataclass(kw_only=True)
class DamageAdjustment:
    """Represent a damage interaction that modifies defensive CR."""

    PHYSICAL_DAMAGE_TYPES: ClassVar[frozenset[DamageType]] = frozenset(
        {
            "bludgeoning",
            "piercing",
            "slashing",
        }
    )
    damage_type: DamageType
    armor_class_modifier: float = field(default=0.0, init=False)
    physical_modifier: ClassVar[float] = 0.0
    other_modifier: ClassVar[float] = 0.0

    def __post_init__(self) -> None:
        """Calculate the armor-class modifier for the damage type."""
        if self.damage_type in self.PHYSICAL_DAMAGE_TYPES:
            self.armor_class_modifier = self.physical_modifier
        else:
            self.armor_class_modifier = self.other_modifier


# Resistances and immunities


@dataclass(kw_only=True)
class Resistance(DamageAdjustment):
    """Represent resistance to a particular damage type."""

    physical_modifier: ClassVar[float] = 1.0
    other_modifier: ClassVar[float] = 0.5


@dataclass(kw_only=True)
class Immunity(DamageAdjustment):
    """Represent immunity to a particular damage type."""

    physical_modifier: ClassVar[float] = 2.0
    other_modifier: ClassVar[float] = 1.0


@dataclass(kw_only=True)
class Vulnerability(DamageAdjustment):
    """Represent vulnerability to a particular damage type."""

    physical_modifier: ClassVar[float] = -1.0
    other_modifier: ClassVar[float] = -0.5
