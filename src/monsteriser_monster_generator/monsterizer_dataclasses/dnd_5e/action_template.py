"""Define resuable templates for monster actions."""

from dataclasses import dataclass
from typing import Literal

from .actions import AttackAction, DamageRoll
from .model_types import AttackRange, DamageType

type AbilityModifierName = Literal[
    "strength_modifier",
    "dexterity_modifier",
    "constitution_modifier",
    "charisma_modifier",
    "wisdom_modifier",
    "intelligence_modifier",
]


@dataclass(kw_only=True, frozen=True, slots=True)
class NaturalAttackTemplate:
    """Describe a resuable natural attack."""

    template_id: str
    name: str
    attack_range: AttackRange
    damage_dice_count: int
    damage_die_size: int
    damage_type: DamageType
    ability_modifier: AbilityModifierName

    reach_ft: float | None = None
    reach_m: float | None = None
    description: str = ""

    def create_action(self, *, attack_bonus: int, damage_modifier: int) -> AttackAction:
        """Create a configured natural attack action from the template.

        Args:
            attack_bonus: the modifier for the attack roll.
            damage_modifier: the modifier for the damage roll.

        Returns:
            A congifured natural attack action.

        """
        return AttackAction(
            action_id=f"natural:{self.template_id!r}",
            name=self.name,
            origin="natural",
            description=self.description,
            attack_range=self.attack_range,
            attack_bonus=attack_bonus,
            reach_ft=self.reach_ft,
            reach_m=self.reach_m,
            damage=(
                DamageRoll(
                    dice_count=self.damage_dice_count,
                    die_size=self.damage_die_size,
                    modifier=damage_modifier,
                    damage_type=self.damage_type,
                ),
            ),
        )
