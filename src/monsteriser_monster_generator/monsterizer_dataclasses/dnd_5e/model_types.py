"""Define shared types used by monster data models."""

from typing import Literal, TypedDict

# Monster sizes

type MonsterSize = Literal[
    "tiny",
    "small",
    "medium",
    "large",
    "huge",
    "gargantuan",
]

# Monster types

type MonsterType = Literal[
    "Aberration",
    "Beast",
    "Celestial",
    "Construct",
    "Dragon",
    "Elemental",
    "Fey",
    "Fiend",
    "Giant",
    "Humanoid",
    "Monstrosity",
    "Ooze",
    "Plant",
    "Undead",
]

# Damage types

type DamageType = Literal[
    "acid",
    "bludgeoning",
    "cold",
    "fire",
    "force",
    "lightning",
    "necrotic",
    "piercing",
    "poison",
    "psychic",
    "radiant",
    "slashing",
    "thunder",
]

# Gear types

type GearType = Literal[
    "armor",
    "shield",
    "weapon",
]

# Gear categories

type GearCategory = Literal[
    "light",
    "medium",
    "heavy",
    "simple",
    "martial",
]

# Gear details


class WeaponDetails(TypedDict, total=False):
    """Describe weapon-reference data."""

    category: GearCategory
    damage: str
    damage_type: DamageType
    range: str
    properties: list[str]
    mastery: str


class ArmorDetails(TypedDict, total=False):
    """Describe armor data loaded from the gear reference."""

    armor_class: int
    stealth_disadvantage: bool
    category: GearCategory
    dexterity_modifier_cap: int | None
    strength_requirement: int | None
