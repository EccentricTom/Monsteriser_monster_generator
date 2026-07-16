"""Define shared types used by monster data models."""

from typing import Literal, NotRequired, TypedDict

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

# Combat types

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

type AbilityName = Literal[
    "strength",
    "dexterity",
]

type AttackRange = Literal[
    "melee",
    "ranged",
]

type WeaponType = Literal[
    "melee",
    "ranged",
]

type WeaponAttackMode = Literal[
    "melee_one_handed",
    "melee_two_handed",
    "ranged",
    "thrown",
]

# Gear types

type GearType = Literal[
    "armor",
    "shield",
    "weapon",
]
type GearCategory = Literal["light", "medium", "heavy", "simple", "martial", "shield"]

type CurrencyDenomination = Literal["copper", "silver", "gold"]

type WeaponProperty = Literal[
    "ammunition",
    "finesse",
    "heavy",
    "light",
    "loading",
    "reach",
    "thrown",
    "two-handed",
    "versatile",
]

# Reference data structures (Typed Dictionaries)


class DistanceRange(TypedDict):
    """Represent the normal and long range of a weapon."""

    normal: float
    long: float


class WeaponDetails(TypedDict):
    """Describe a weapon-reference entry."""

    name: str
    category: GearCategory
    type: WeaponType
    cost: float
    cost_denom: CurrencyDenomination
    weight_lbs: float
    weight_kg: float
    damage: str
    damage_type: DamageType
    stat_mod: AbilityName
    properties: list[WeaponProperty]
    mastery: str

    versatile_damage: NotRequired[str]

    reach_ft: NotRequired[float]
    reach_m: NotRequired[float]

    range_ft: NotRequired[DistanceRange]
    range_m: NotRequired[DistanceRange]

    thrown_range_ft: NotRequired[DistanceRange]
    thrown_range_m: NotRequired[DistanceRange]


class ArmorDetails(TypedDict):
    """Describe armor data loaded from the gear reference."""

    name: str
    category: GearCategory
    armour_class: int
    stealth_disadvantage: bool

    strength_requirement: NotRequired[int]
    dexterity_modifier_cap: NotRequired[int]
