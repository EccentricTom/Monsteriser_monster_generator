"""Define attack-roll and saving-throw actions."""

from dataclasses import dataclass, field
from typing import Literal

from ..model_types import AttackRange
from .base import MonsterAction
from .effects import ConditionEffect, DamageRoll, SavingThrowDamage


@dataclass(kw_only=True, frozen=True, slots=True)
class AttackAction(MonsterAction):
    """A monster action that deals damage.

    This allows for a single attact that can have different die rolls for different damage types.
    """

    category: Literal["attack"] = field(
        default="attack",
        init=False,
    )

    attack_range: AttackRange
    attack_bonus: int
    damage: tuple[DamageRoll, ...]

    conditions: tuple[ConditionEffect, ...] = ()

    reach_ft: float | None = None
    reach_m: float | None = None

    normal_range_ft: float | None = None
    long_range_ft: float | None = None
    normal_range_m: float | None = None
    long_range_m: float | None = None

    hit_effect_text: str | None = None
    description_override: str | None = None

    def average_damage(self) -> float:
        """Average damage of the attack."""
        return sum(damage_roll.average_damage() for damage_roll in self.damage)

    def generate_description(self) -> str:
        """Generate a description of the attack action based on DnD 2024 wording.

        Return:
            Description override or the generated description.

        """
        if self.description_override is not None:
            return self.description_override
        attack_text = self._attack_roll_text()
        damage_text = self._damage_roll_text()

        description = f"{attack_text} Hit: {damage_text}"

        if self.hit_effect_text is not None:
            description += f"{self.hit_effect_text}"

        return description

    def _attack_roll_text(self) -> str:
        """Generate the text for an attack roll part of the description.

        NB: Currently only imperial measurements are used for range/reach
        """
        attack_bonus = f"{self.attack_bonus:d}"

        match self.attack_range:
            case "melee":
                return f"Melee attack roll: {attack_bonus}, reach {self._format_reach()}."
            case "ranged":
                return f"Melee attack roll: {attack_bonus}, range {self._format_range()}."
            case "melee_or_ranged":
                return (
                    f"Melee or ranged attack roll: {attack_bonus}, "
                    f"reach {self._format_reach} or range {self._format_range()}."
                )

    def _damage_roll_text(self) -> str:
        """Generate the text for the damage roll part of the description.

        This shows both the roll and the average damage.
        """
        if not self.damage:
            raise ValueError(f"Action {self.action_id!r} has no damage")

        damage_parts = tuple(damage_roll.stat_block_text() for damage_roll in self.damage)

        return " plus ".join(damage_parts)

    def _format_reach(self) -> str:
        """Format the reach of the attack for the description."""
        if not self.reach_ft:
            raise ValueError(f"Melee attack {self.action_id!r} has no reach")
        return f"{self.reach_ft:g} ft"

    def _format_range(self) -> str:
        """Format the range of the attack for the description."""
        if self.normal_range_ft is None:
            raise ValueError(f"Ranged attack {self.action_id!r} has no normal range")

        if self.long_range_ft is None:
            return f"{self.normal_range_ft:g} ft"

        return f"{self.normal_range_ft:g}/{self.long_range_ft} ft"


@dataclass(kw_only=True, frozen=True, slots=True)
class SavingThrowAction(MonsterAction):
    """Represent an action resolved with a saving throw."""

    category: Literal["saving_throw"] = field(
        default="saving_throw",
        init=False,
    )

    saving_throw: SavingThrowDamage
    conditions: tuple[ConditionEffect, ...] = ()

    target_description: str
    area_description: str | None = None
    expected_targets: float = 1.0
    failure_effect_str: str | None = None
    success_effect_str: str | None = None
    description_override: str | None = None

    def __post_init__(self) -> None:
        """Validate the expected target count."""
        if self.expected_targets <= 0:
            raise ValueError("Must have at least one expected target.")

    def generate_description(self) -> str:
        """Generate the description of the action requiring a saving throw."""
        if self.description_override is not None:
            return self.description_override

        effect = self.saving_throw
        ability = effect.ability.capitalize()

        description = (
            f"a{ability} Saving Throw: "
            f"DC {effect.difficulty_class}, "
            f"{self.target_description}. "
            f"Failure: {self._failed_save_damage_text()}."
        )

        if self.failure_effect_str is not None:
            description = description[:-1] + f"and {self.failure_effect_str}"

        if effect.success_outcome == "half":
            description += "Success: Half damage."
        elif self.success_effect_str is not None:
            description += f"Success: {self.success_effect_str}"

        return description

    def _failed_save_damage_text(self) -> str:
        """Generate the description of what happens on a failed save."""
        damage_parts = tuple(
            damage_roll.stat_block_text() for damage_roll in self.saving_throw.damage
        )

        return " plus ".join(damage_parts)
