"""Define monster equipment models."""

from dataclasses import dataclass, field

from dataclasses_json import dataclass_json

from .model_types import ArmorDetails, DamageType, GearCategory, GearType, WeaponDetails


@dataclass_json
@dataclass(kw_only=True)
class Gear:
    """Represent a piece of equipment used by a monster."""

    name: str
    gear_type: GearType
    category: GearCategory | None = None
    martial: bool = field(default=False, init=False)
    damage_die: str | None = field(default=None, init=False)
    damage_type: DamageType | None = field(default=None, init=False)
    weapon_range: str | None = field(default=None, init=False)
    properties: list[str] = field(default_factory=list, init=False)
    mastery: str | None = field(default=None, init=False)
    armor_class: int | None = field(default=None, init=False)
    stealth_disadvantage: bool = field(default=False, init=False)
    dexterity_modifier_cap: int | None = field(default=None, init=False)
    strength_requirement: int | None = field(default=None, init=False)

    def apply_weapon_details(self, details: WeaponDetails) -> None:
        """Populate this item with weapon-reference data.

        Args:
        details: Weapon data loaded from the gear reference.

        """
        self.category = details.get("category")
        self.martial = self.category == "martial"
        self.damage_die = details.get("damage")
        self.damage_type = details.get("damage_type")
        self.weapon_range = details.get("range")
        self.properties = details.get("properties", []).copy()
        self.mastery = details.get("mastery")

    def apply_armor_details(self, details: ArmorDetails) -> None:
        """Populate this item with armor-reference data.

        Args:
        details: Armor data loaded from the gear reference.

        """
        self.armor_class = details.get("armor_class")
        self.stealth_disadvantage = details.get(
            "stealth_disadvantage",
            False,
        )
        self.category = details.get("category")
        self.dexterity_modifier_cap = details.get(
            "dexterity_modifier_cap",
        )
        self.strength_requirement = details.get(
            "strength_requirement",
        )
