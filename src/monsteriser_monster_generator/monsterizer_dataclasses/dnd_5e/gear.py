"""Define monster equipment models."""

from dataclasses import dataclass, field
from typing import Literal

from dataclasses_json import dataclass_json

from .actions import AttackAction, DamageRoll
from .model_types import ArmorDetails, DamageType, GearCategory, WeaponDetails


@dataclass_json
@dataclass(kw_only=True)
class Gear:
    """Represent a piece of equipment used by a monster."""

    name: str
    category: GearCategory | None = None


@dataclass_json
@dataclass(kw_only=True)
class Weapon(Gear):
    """Represent a weapon that can genearte an attack."""

    category: GearCategory | None = None
    martial: bool = field(default=False, init=False)
    damage_dice_count: int | None = field(default=None, init=False)
    damage_dice_size: int | None = field(default=None, init=False)
    damage_type: DamageType | None = field(default=None, init=False)
    weapon_range: str | None = field(default=None, init=False)
    properties: list[str] = field(default_factory=list, init=False)
    mastery: str | None = field(default=None, init=False)

    reach: int | None = field(default=None, init=False)
    normal_range: int | None = field(default=None, init=False)
    long_range: int | None = field(default=None, init=False)

    def apply_refernce_details(self, details: WeaponDetails) -> None:
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

        damage = details.get("damage")

        if damage is not None:
            self.damage_dice_count, self.damage_dice_size = self._parse_damage_dice(damage)

    def create_attack_action(
        self,
        attack_bonus: int,
        damage_modifier: int,
        action_id: str | None = None,
        action_name: str | None = None,
    ) -> AttackAction:
        """Create an attack action from this weapon.

        Args:
            attack_bonus: Modifier added to the attack roll.
            damage_modifier: Modifier added to the damage roll.
            action_id: Optional identifier for the generated action.
            action_name: Option display name for the generated action.

        Returns:
            An attack action configured for the monster using the weapon

        Raises:
            ValueError: If the weapon does not contain complete damage data

        """
        if self.damage_dice_count is None:
            raise ValueError(f"Weapon {self.name!r} has no damage dice count")
        if self.damage_dice_size is None:
            raise ValueError(f"Weapon {self.name!r} does not have a damage die size")
        if self.damage_type is None:
            raise ValueError(f"Weapon {self.name!r} does not have a damage type")

        return AttackAction(
            action_id=action_id or self._default_action_id(),
            name=action_name or self.name,
            attack_range=self._get_attack_range(),
            attack_bonus=attack_bonus,
            reach=self.reach,
            normal_range=self.normal_range,
            long_range=self.long_range,
            damage=(
                DamageRoll(
                    dice_count=self.damage_dice_count,
                    die_size=self.damage_dice_size,
                    modifier=damage_modifier,
                    damage_type=self.damage_type,
                ),
            ),
        )

    def _default_action_id(self) -> str:
        """Generate a default action id if one is not provided."""
        normalised_name = self.name.casefold().replace(" ", "_")
        return f"weapon:{normalised_name}"

    def _get_attack_range(self) -> Literal["melee", "ranged", "melee_or_ranged"]:
        """Return the normalised attack range category."""
        match self.weapon_range:
            case "melee":
                return "melee"
            case "ranged":
                return "ranged"
            case "melee_or_ranged":
                return "melee_or_ranged"
            case _:
                raise ValueError(
                    f"Weapon {self.name!r} has an invalid range: {self.weapon_range!r}"
                )

    @staticmethod
    def _parse_damage_dice(damage: str) -> tuple[int, int]:
        """Parse a damage expression, i.e. "1d8".

        Args:
            damage: Damage dice expressed as "NdN".

        Returns:
            The number of dice and the size of each die

        Raises:
            ValueError: If the expression is not valid

        """
        try:
            dice_count_text, dice_size_text = damage.lower().split("d", maxsplit=1)
            dice_count = int(dice_count_text)
            die_size = int(dice_size_text)
        except (ValueError, TypeError, AttributeError) as e:
            raise ValueError(f"Invalid damage die expression: {damage!r}") from e

        if dice_count < 1 or die_size < 1:
            raise ValueError(f"Damage dice values must be positive: {damage!r}")

        return dice_count, die_size


@dataclass_json
@dataclass(kw_only=True)
class Armor:
    """"""

    armor_class: int | None = field(default=None, init=False)
    stealth_disadvantage: bool = field(default=False, init=False)
    dexterity_modifier_cap: int | None = field(default=None, init=False)
    strength_requirement: int | None = field(default=None, init=False)

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
