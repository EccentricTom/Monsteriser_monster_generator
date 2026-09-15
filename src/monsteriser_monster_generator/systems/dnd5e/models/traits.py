"""Define structured monster traits for D&D 5E 2024."""

from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass(kw_only=True, frozen=True, slots=True)
class MonsterTrait:
    """Base class for structured monster traits."""

    name: str


@dataclass_json
@dataclass(kw_only=True, frozen=True, slots=True)
class RegenerationTrait(MonsterTrait):
    """Represent hit points regained automatically each round."""

    hit_points_per_round: int
