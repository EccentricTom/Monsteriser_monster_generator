"""Dataclasses for creating monsters using DnD 5th Edition."""

from dataclasses import dataclass, field, make_dataclass

from dataclass_exceptions import InvalidTypeError
from dataclasses_json import dataclass_json

# Base monster dataclass

@dataclass_json
@dataclass(kw_only=True)
class BaseMonster:
    """
    Base dataclass for all monsters.
    
    All monster types derive from this base. 
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
    traits: list = field(default=[])
    actions: list = field(default=[])
    bonus_actions: list = field(default=[])

    def __post_init__(self):
        """Set up ability modifiers and base armor class."""
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
    """
    Aberration.

    Inherits from BaseMonster.

    Could use gear.
    """

    monster_type:str = "Aberration"
    gear:list | None = field(default=None, init=False)

@dataclass_json
@dataclass(kw_only=True)
class Beast(BaseMonster):
    """
    Beast.

    Inherits from BaseMonster.
    
    Does not use gear except for edge cases.

    Uses natural armor unless specified.
    """

    monster_type:str = "Beast"
    armor:str = "natural armor"

@dataclass_json
@dataclass(kw_only=True)
class Celestial(BaseMonster):
    """
    Celestial.

    Inherits from BaseMonster.

    Could use gear.
    """

    monster_type:str = "Celestial"
    gear: list | None = field(default=None, init=False)

@dataclass_json
@dataclass(kw_only=True)
class Constructs(BaseMonster):
    """
    Construct.

    Inherits from BaseMonster.
    """

    monster_type:str = "Celestial"
    gear: list | None = field(default=None, init=False)

# Resistances and immunities

@dataclass(kw_only=True)
class Resistance:
    """
    Dataclass used to track any monster resistances.

    Will be part of a list, even if there is just one resistance.
    """

    type: str
    ac_modifier: float = field(default=0)

    def __post_init__(self):
        """Validate that type is the correct format."""
        if not isinstance(self.type, str):
            raise InvalidTypeError("Not a valid type", self.type)
        if self.type in ["bludgeoning", "piercing", "slashing"]:
            self.ac_modifier += 1
        else:
            self.ac_modifier += 0.5

@dataclass(kw_only=True)
class Immunity:
    """
    Dataclass used to track any monster immunities.

    Will be part of a list, even if there is just one resistance.
    """
    
    type: str
    ac_modifier: float = field(default=0)

    def __post_init__(self):
        """Validate that type is the correct format."""
        if not isinstance(self.type, str):
            raise InvalidTypeError("Not a valid type", self.type)
        if self.type in ["bludgeoning", "piercing", "slashing"]:
            self.ac_modifier += 2
        else:            
            self.ac_modifier += 1

@dataclass(kw_only=True)
class Vulnerability:
    """
    Dataclass used to track any monster vulnerabilities.

    Will be part of a list, even if there is just one resistance.
    """
    
    type: str
    ac_modifier: float = field(default=0)

    def __post_init__(self):
        """Validate that type is the correct format."""
        if not isinstance(self.type, str):
            raise InvalidTypeError("Not a valid type", self.type)
        if self.type in ["bludgeoning", "piercing", "slashing"]:
            self.ac_modifier -= 1
        else:
            self.ac_modifier -= 0.5

@dataclass(kw_only=True)
class Gear:
    """
    Dataclass used to track any monster gear.

    Will be part of a list, even if there is just one piece of gear.
    """

    name: str
    type: str
    category: str | None = field(default=None)

    def __post_init__(self):
        """Validate that type is the correct format."""
        if not isinstance(self.name, str):
            raise InvalidTypeError("Not a valid name", self.name)
        if not isinstance(self.type, str):
            raise InvalidTypeError("Not a valid type", self.type)
        if not isinstance(self.category, str):
            raise InvalidTypeError("Not a valid category", self.category)
        
    def weapon_details(self, details:dict) -> None:
        """Fill in the details of the weapon based on the reference.
        
        Args:
            details (dict): Details of the weapon from the gear reference

        """
        self.martial = True if details.get("catetory") == "martial" else False
        self.damage_die = details.get("damage")
        self.damage_type = details.get("damage_type")
        if "range" in details:
            self.range = details.get("range")
        self.properties = details.get("properties", [])
        self.mastery = details.get("mastery", None)

    def armor_details(self, details:dict) -> None:
        """Fill in the details of the armor based on the reference.
        
        Args:
            details (dict): Details of the armor from the gear reference

        """
        self.armor_class = details.get("armor_class")
        self.stealth_disadvantage = details.get("stealth_dis", False)
        self.category = details.get("category", None)
        self.dex_mod_cap = details.get("dex_mod_cap", None)
        if details.get("stat_req"):
            self.stat_req = details.get("stat_req", None)
            self.stat_req_num = details.get("stat_req_num", None)


