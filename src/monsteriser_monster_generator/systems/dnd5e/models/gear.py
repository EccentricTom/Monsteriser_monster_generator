"""Define monster equipment models."""

from dataclasses import dataclass, field
from typing import Literal

from dataclasses_json import dataclass_json

from .actions import AttackAction, DamageRoll
from .model_types import (
    AbilityName,
    ArmorDetails,
    AttackRange,
    CurrencyDenomination,
    DamageType,
    GearCategory,
    WeaponAttackMode,
    WeaponDetails,
    WeaponProperty,
    WeaponType,
)


@dataclass_json
@dataclass(kw_only=True)
class Gear:
    """Represent a piece of equipment used by a monster."""

    name: str | None = None
    category: GearCategory | None = None


@dataclass_json
@dataclass(kw_only=True)
class Weapon(Gear):
    """Represent a weapon that can genearte an attack."""

    gear_type: Literal["weapon"] = field(
        default="weapon",
        init=False,
    )

    weapon_type: WeaponType | None = field(default=None, init=False)
    ability_modifier: AbilityName | None = field(
        default=None,
        init=False,
    )

    cost: float | None = field(default=None, init=False)
    cost_denomination: CurrencyDenomination | None = field(
        default=None,
        init=False,
    )
    weight_lbs: float | None = field(default=None, init=False)
    weight_kg: float | None = field(default=None, init=False)

    properties: list[WeaponProperty] = field(
        default_factory=list[WeaponProperty],
        init=False,
    )
    mastery: str | None = field(default=None, init=False)

    damage_dice_count: int | None = field(default=None, init=False)
    damage_die_size: int | None = field(default=None, init=False)

    versatile_dice_count: int | None = field(default=None, init=False)
    versatile_die_size: int | None = field(default=None, init=False)

    damage_type: DamageType | None = field(default=None, init=False)

    reach_ft: float | None = field(default=None, init=False)
    reach_m: float | None = field(default=None, init=False)

    normal_range_ft: float | None = field(default=None, init=False)
    long_range_ft: float | None = field(default=None, init=False)
    normal_range_m: float | None = field(default=None, init=False)
    long_range_m: float | None = field(default=None, init=False)

    thrown_normal_range_ft: float | None = field(
        default=None,
        init=False,
    )
    thrown_long_range_ft: float | None = field(
        default=None,
        init=False,
    )
    thrown_normal_range_m: float | None = field(
        default=None,
        init=False,
    )
    thrown_long_range_m: float | None = field(
        default=None,
        init=False,
    )

    def apply_reference_details(self, details: WeaponDetails) -> None:
        """Populate this item with weapon-reference data.

        Args:
        details: Weapon data loaded from the gear reference.

        """
        self.name = details["name"]
        self.category = details["category"]
        self.weapon_type = details["type"]
        self.ability_modifier = details["stat_mod"]

        self.cost = details["cost"]
        self.cost_denomination = details["cost_denom"]
        self.weight_lbs = details["weight_lbs"]
        self.weight_kg = details["weight_kg"]

        self.properties = details.get("properties").copy()
        self.mastery = details["mastery"]
        self.damage_type = details["damage_type"]

        self.damage_dice_count, self.damage_die_size = self._parse_damage_dice(details["damage"])

        versatile_damage = details.get("versatile_damage")

        if versatile_damage is not None:
            self.versatile_dice_count, self.versatile_die_size = self._parse_damage_dice(
                versatile_damage
            )

        self.reach_ft = details.get("reach_ft")
        self.reach_m = details.get("reach_m")

        ranged_ft = details.get("range_ft")
        ranged_m = details.get("range_m")
        thrown_ft = details.get("thrown_range_ft")
        thrown_m = details.get("thrown_range_m")

        if ranged_ft is not None:
            self.normal_range_ft = ranged_ft["normal"]
            self.long_range_ft = ranged_ft["long"]

        if ranged_m is not None:
            self.normal_range_m = ranged_m["normal"]
            self.long_range_m = ranged_m["long"]

        if thrown_ft is not None:
            self.thrown_normal_range_ft = thrown_ft["normal"]
            self.thrown_long_range_ft = thrown_ft["long"]

        if thrown_m is not None:
            self.thrown_normal_range_m = thrown_m["normal"]
            self.thrown_long_range_m = thrown_m["long"]

    def create_attack_action(
        self,
        *,
        mode: WeaponAttackMode,
        attack_bonus: int,
        damage_modifier: int,
        action_id: str | None = None,
        action_name: str | None = None,
        additional_damage: tuple[DamageRoll, ...] = (),
    ) -> AttackAction:
        """Create an attack action from this weapon.

        Args:
            mode: Whether the attack is ranged or not, and if versatile or not.
            attack_bonus: Modifier added to the attack roll.
            damage_modifier: Modifier added to the damage roll.
            action_id: Optional identifier for the generated action.
            action_name: Option display name for the generated action.
            additional_damage: Extra damage riders dealt by the attack.

        Returns:
            An attack action configured for the monster using the weapon

        Raises:
            ValueError: If the weapon does not contain complete damage data

        """
        name = self._require_name()
        damage_type = self._require_damage_type()
        dice_count, die_size = self._get_damage_dice(mode)
        attack_range = self._get_attack_range(mode)

        base_damage = DamageRoll(
            dice_count=dice_count,
            die_size=die_size,
            modifier=damage_modifier,
            damage_type=damage_type,
        )

        return AttackAction(
            action_id=action_id or self._default_action_id(mode),
            name=action_name or name,
            origin="gear",
            timing="action",
            attack_range=attack_range,
            attack_bonus=attack_bonus,
            reach_ft=self._get_reach_ft(mode),
            reach_m=self._get_reach_m(mode),
            normal_range_ft=self._get_normal_range_ft(mode),
            long_range_ft=self._get_long_range_ft(mode),
            normal_range_m=self._get_normal_range_m(mode),
            long_range_m=self._get_long_range_m(mode),
            damage=(base_damage, *additional_damage),
        )

    def _get_damage_dice(
        self,
        mode: WeaponAttackMode,
    ) -> tuple[int, int]:
        """Return the damage dice for the selected attack mode."""
        if mode == "melee_two_handed":
            if "versatile" not in self.properties:
                raise ValueError(f"Weapon {self.name!r} is not versatile")
            if self.versatile_dice_count is None or self.versatile_die_size is None:
                raise ValueError(f"Weapon {self.name!r} has no versatile damage")
            return (
                self.versatile_dice_count,
                self.versatile_die_size,
            )
        if self.damage_dice_count is None or self.damage_die_size is None:
            raise ValueError(f"Weapon {self.name!r} has incomplete damage dice")
        return self.damage_dice_count, self.damage_die_size

    def _get_attack_range(
        self,
        mode: WeaponAttackMode,
    ) -> AttackRange:
        """Return the attack-range category for a weapon-use mode."""
        if mode in {
            "melee_one_handed",
            "melee_two_handed",
        }:
            if self.weapon_type != "melee":
                raise ValueError(f"Weapon {self.name!r} is not a melee weapon")
            if mode == "melee_two_handed" and "versatile" not in self.properties:
                raise ValueError(f"Weapon {self.name!r} is not versatile")
            return "melee"
        if mode == "thrown":
            if "thrown" not in self.properties:
                raise ValueError(f"Weapon {self.name!r} cannot be thrown")
            return "ranged"
        if self.weapon_type != "ranged":
            raise ValueError(f"Weapon {self.name!r} is not a ranged weapon")
        return "ranged"

    def _get_reach_ft(
        self,
        mode: WeaponAttackMode,
    ) -> float | None:
        """Return imperial reach for a melee attack."""
        if mode in {
            "melee_one_handed",
            "melee_two_handed",
        }:
            return self.reach_ft
        return None

    def _get_reach_m(
        self,
        mode: WeaponAttackMode,
    ) -> float | None:
        """Return metric reach for a melee attack."""
        if mode in {
            "melee_one_handed",
            "melee_two_handed",
        }:
            return self.reach_m
        return None

    def _get_normal_range_ft(
        self,
        mode: WeaponAttackMode,
    ) -> float | None:
        """Return imperial normal range for a ranged attack."""
        if mode == "thrown":
            return self.thrown_normal_range_ft
        if mode == "ranged":
            return self.normal_range_ft
        return None

    def _get_long_range_ft(
        self,
        mode: WeaponAttackMode,
    ) -> float | None:
        """Return imperial long range for a ranged attack."""
        if mode == "thrown":
            return self.thrown_long_range_ft
        if mode == "ranged":
            return self.long_range_ft
        return None

    def _get_normal_range_m(
        self,
        mode: WeaponAttackMode,
    ) -> float | None:
        """Return metric normal range for a ranged attack."""
        if mode == "thrown":
            return self.thrown_normal_range_m
        if mode == "ranged":
            return self.normal_range_m
        return None

    def _get_long_range_m(
        self,
        mode: WeaponAttackMode,
    ) -> float | None:
        """Return metric long range for a ranged attack."""
        if mode == "thrown":
            return self.thrown_long_range_m
        if mode == "ranged":
            return self.long_range_m
        return None

    def _require_name(self) -> str:
        """Return the weapon name or raise an error."""
        if self.name is None:
            raise ValueError("Weapon has no name")
        return self.name

    def _require_damage_type(self) -> DamageType:
        """Return the damage type or raise an error."""
        if self.damage_type is None:
            raise ValueError(f"Weapon {self.name!r} has no damage type")
        return self.damage_type

    def _default_action_id(
        self,
        mode: WeaponAttackMode,
    ) -> str:
        """Generate a stable default action identifier."""
        normalized_name = self._require_name().casefold().replace(" ", "_")
        return f"weapon:{normalized_name}:{mode}"

    def _default_action_name(
        self,
        mode: WeaponAttackMode,
    ) -> str:
        """Generate a display name for the attack action."""
        name = self._require_name()

        match mode:
            case "melee_two_handed":
                return f"{name} (Two-Handed)"
            case "thrown":
                return f"{name} (Thrown)"
            case _:
                return name

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
class Armor(Gear):
    """Represent armor worn by a monster."""

    gear_type: Literal["armor"] = field(
        default="armor",
        init=False,
    )
    armor_class: int | None = field(default=None, init=False)
    stealth_disadvantage: bool = field(
        default=False,
        init=False,
    )
    dexterity_modifier_cap: int | None = field(
        default=None,
        init=False,
    )
    strength_requirement: int | None = field(
        default=None,
        init=False,
    )

    def apply_reference_details(
        self,
        details: ArmorDetails,
    ) -> None:
        """Populate this armor with reference data.

        Args: details: Armor data loaded from the gear reference.

        """
        self.name = details["name"]
        self.category = details["category"]
        self.armor_class = details["armour_class"]
        self.stealth_disadvantage = details["stealth_disadvantage"]
        self.dexterity_modifier_cap = details.get("dexterity_modifier_cap")
        self.strength_requirement = details.get("strength_requirement")
