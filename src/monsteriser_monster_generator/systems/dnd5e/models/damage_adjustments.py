"""Define monster damage adjustment models."""

from dataclasses import dataclass

from dataclasses_json import dataclass_json

from .model_types import DamageType


@dataclass_json
@dataclass(kw_only=True)
class DamageAdjustment:
    """Represent a monster's interaction with a damage type."""

    damage_type: DamageType


@dataclass_json
@dataclass(kw_only=True)
class Resistance(DamageAdjustment):
    """Represent resistance to a damage type."""


@dataclass_json
@dataclass(kw_only=True)
class Immunity(DamageAdjustment):
    """Represent immunity to a damage type."""


@dataclass_json
@dataclass(kw_only=True)
class Vulnerability(DamageAdjustment):
    """Represent vulnerability to a damage type."""
