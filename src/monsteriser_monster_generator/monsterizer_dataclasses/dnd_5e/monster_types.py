"""Define concrete D&D monster-type models."""

from dataclasses import dataclass, field
from typing import Literal

from dataclasses_json import dataclass_json

from .base_monster import BaseMonster


@dataclass_json
@dataclass(kw_only=True)
class Aberration(BaseMonster):
    """Represent an aberration."""

    monster_type: Literal["Aberration"] = field(
        default="Aberration",
        init=False,
    )


@dataclass_json
@dataclass(kw_only=True)
class Beast(BaseMonster):
    """Represent a beast."""

    monster_type: Literal["Beast"] = field(
        default="Beast",
        init=False,
    )
    armor_description: str = "natural armor"


@dataclass_json
@dataclass(kw_only=True)
class Celestial(BaseMonster):
    """Represent a celestial."""

    monster_type: Literal["Celestial"] = field(
        default="Celestial",
        init=False,
    )


@dataclass_json
@dataclass(kw_only=True)
class Construct(BaseMonster):
    """Represent a construct."""

    monster_type: Literal["Construct"] = field(
        default="Construct",
        init=False,
    )


@dataclass_json
@dataclass(kw_only=True)
class Dragon(BaseMonster):
    """Represent a dragon."""

    monster_type: Literal["Dragon"] = field(
        default="Dragon",
        init=False,
    )


@dataclass_json
@dataclass(kw_only=True)
class Elemental(BaseMonster):
    """Represent an elemental."""

    monster_type: Literal["Elemental"] = field(
        default="Elemental",
        init=False,
    )


@dataclass_json
@dataclass(kw_only=True)
class Fey(BaseMonster):
    """Represent a fey creature."""

    monster_type: Literal["Fey"] = field(
        default="Fey",
        init=False,
    )


@dataclass_json
@dataclass(kw_only=True)
class Fiend(BaseMonster):
    """Represent a fiend."""

    monster_type: Literal["Fiend"] = field(
        default="Fiend",
        init=False,
    )


@dataclass_json
@dataclass(kw_only=True)
class Giant(BaseMonster):
    """Represent a giant."""

    monster_type: Literal["Giant"] = field(
        default="Giant",
        init=False,
    )


@dataclass_json
@dataclass(kw_only=True)
class Humanoid(BaseMonster):
    """Represent a humanoid."""

    monster_type: Literal["Humanoid"] = field(
        default="Humanoid",
        init=False,
    )


@dataclass_json
@dataclass(kw_only=True)
class Monstrosity(BaseMonster):
    """Represent a monstrosity."""

    monster_type: Literal["Monstrosity"] = field(
        default="Monstrosity",
        init=False,
    )


@dataclass_json
@dataclass(kw_only=True)
class Ooze(BaseMonster):
    """Represent an ooze."""

    monster_type: Literal["Ooze"] = field(
        default="Ooze",
        init=False,
    )


@dataclass_json
@dataclass(kw_only=True)
class Plant(BaseMonster):
    """Represent a plant creature."""

    monster_type: Literal["Plant"] = field(
        default="Plant",
        init=False,
    )


@dataclass_json
@dataclass(kw_only=True)
class Undead(BaseMonster):
    """Represent an undead creature."""

    monster_type: Literal["Undead"] = field(
        default="Undead",
        init=False,
    )
