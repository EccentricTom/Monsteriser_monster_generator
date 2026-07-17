"""Define shared types used by monster data models."""

from dataclasses import dataclass
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

# Action types

type ActionTiming = Literal[
    "action",
    "bonus_action",
    "reaction",
    "legendary_action",
]

type ActionCategory = Literal[
    "attack",
    "multiattack",
    "special",
    "spellcasting",
    "saving_throw",
]

type ActionOrigin = Literal[
    "natural",
    "gear",
    "spell",
    "special",
    "custom",
]

type AttackRange = Literal[
    "melee",
    "ranged",
]


type AbilityName = Literal[
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
]

type AbilityModifierName = Literal[
    "strength_modifier",
    "dexterity_modifier",
    "constitution_modifier",
    "charisma_modifier",
    "wisdom_modifier",
    "intelligence_modifier",
]

type SavingThrowOutcome = Literal[
    "none",
    "half",
]

type RechargeValue = Literal[
    2,
    3,
    4,
    5,
    6,
]

# Damage and conditions


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

type ConditionName = Literal[
    "blinded",
    "charmed",
    "deafened",
    "frightened",
    "grappled",
    "incapacitated",
    "invisible",
    "paralyzed",
    "poisoned",
    "prone",
    "restrained",
    "stunned",
    "unconscious",
]

# Gear Types


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

type GearType = Literal[
    "armor",
    "shield",
    "weapon",
]
type GearCategory = Literal[
    "light",
    "medium",
    "heavy",
    "simple",
    "martial",
    "shield",
]

type CurrencyDenomination = Literal[
    "copper",
    "silver",
    "gold",
]

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


@dataclass(kw_only=True, frozen=True, slots=True)
class ConditionEffect:
    """Represent a condition imposed by an ability."""

    condition: ConditionName
    duration: str
    escape_difficulty_class: int | None = None


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
