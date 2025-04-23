from dataclasses import dataclass, field
from dataclass_exceptions import InvalidTypeError
from dataclasses_json import dataclass_json


# Base monster dataclass

@dataclass_json
@dataclass(kw_only=True)
class BaseMonster:
    """
    Base dataclass for all monsters. All monster types derive
    from this base. 
    """
    name: str
    size: str = field(default="medium")
    hitpoints: int = field(default=10)
    hit_die_size: int = field(default=8)
    hit_die_num: int = field(default=1)
    strength:int = field(default=10)
    dexterity:int = field(default=10)
    constitution:int = field(default=10)
    intelligence:int = field(default=10)
    wisdom:int = field(default=10)
    charisma:int = field(default=10)
    is_spellcaster: bool = field(default=False)
    innate_spellcasting: bool = field(default=False)

    def __post_init__(self):
        self.str_mod = self.strength//2 - 10
        self.dex_mod = self.dexterity//2 - 10
        self.con_mod = self.constitution//2 - 10
        self.int_mod = self.intelligence//2 - 10
        self.wis_mod = self.wisdom//2 - 10
        self.cha_mod = self.charisma//2 - 10
        self.armor_class = 10 + self.dex_mod

# Monster type dataclasses

@dataclass_json
@dataclass(kw_only=True)
class Aberration(BaseMonster):
    monster_type:str = "Aberration"
    gear:list | None = field(default=None, init=False)

@dataclass_json
@dataclass(kw_only=True)
class Beast(BaseMonster):
    monster_type:str = "Beast"
    armor:str = "natural armor"

@dataclass_json
@dataclass(kw_only=True)
class Celestial(BaseMonster):
    monster_type:str = "Celestial"
    gear: list | None = field(default=None, init=False)

@dataclass_json
@dataclass(kw_only=True)
class Constructs(BaseMonster):
    monster_type:str = "Celestial"
    gear: list | None = field(default=None, init=False)

# Resistances and immunities

@dataclass(kw_only=True)
class Resistance:
    type: str
    ac_modifier: float = field(default=0)

    def __post_init__(self):
        if not isinstance(self.type, str):
            raise InvalidTypeError("Not a valid type", self.type)
        if self.type in ["bludgeoning", "piercing", "slashing"]:
            self.ac_modifier += 1
        else:
            self.ac_modifier += 0.5

@dataclass(kw_only=True)
class Immunity:
    type: str
    ac_modifier: float = field(default=0)

    def __post_init__(self):
        if not isinstance(self.type, str):
            raise InvalidTypeError("Not a valid type", self.type)

@dataclass(kw_only=True)
class Vulnerability:
    type: str
    ac_modifier: float = field(default=0)