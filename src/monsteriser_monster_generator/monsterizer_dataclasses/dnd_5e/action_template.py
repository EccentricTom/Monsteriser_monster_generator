"""Define resuable templates for monster actions."""

from dataclasses import dataclass, replace
from typing import Literal

from .actions_complete import AttackAction, DamageRoll
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
class DamageTemplate:
    """Describe one damage component of an attack template."""

    dice_count: int
    die_size: int
    damage_type: DamageType
    add_ability_modifier: bool = False
    flat_modifier: int = 0

    def create_damage_roll(
        self,
        *,
        ability_modifier: int,
    ) -> DamageRoll:
        """Create a configured damage roll.

        Args:
        ability_modifier: Monster ability modifier used by the attack.
        Returns: A configured damage roll.

        """
        modifier = self.flat_modifier
        if self.add_ability_modifier:
            modifier += ability_modifier
        return DamageRoll(
            dice_count=self.dice_count,
            die_size=self.die_size,
            modifier=modifier,
            damage_type=self.damage_type,
        )


@dataclass(kw_only=True, frozen=True, slots=True)
class NaturalAttackTemplate:
    """Describe a resuable natural attack."""

    template_id: str
    name: str
    attack_range: AttackRange
    ability_modifier: AbilityModifierName
    damage: tuple[DamageTemplate, ...]

    reach_ft: float | None = None
    reach_m: float | None = None
    normal_range_ft: float | None = None
    long_range_ft: float | None = None
    normal_range_m: float | None = None
    long_range_m: float | None = None

    description: str = ""

    def create_action(
        self,
        *,
        attack_bonus: int,
        ability_modifier: int,
        action_id: str | None = None,
        action_name: str | None = None,
        additional_damage: tuple[DamageTemplate, ...] = (),
    ) -> AttackAction:
        """Create a configured natural attack action from the template.

        Args:
            attack_bonus: the modifier for the attack roll.
            ability_modifier: ability modifier to add to the eligible roll.
            action_id: optional unique identifier for the action
            action_name: optional display name for the configured action.
            additional_damage: Extra damage riders to the attack
            damage_modifier: the modifier for the damage roll.

        Returns:
            A congifured natural attack action.

        """
        damage_templates = self.damage + additional_damage

        return AttackAction(
            action_id=action_id or f"natural:{self.template_id!r}",
            name=action_name or self.name,
            origin="natural",
            description=self.description,
            attack_range=self.attack_range,
            attack_bonus=attack_bonus,
            reach_ft=self.reach_ft,
            reach_m=self.reach_m,
            normal_range_ft=self.normal_range_ft,
            long_range_ft=self.long_range_ft,
            normal_range_m=self.normal_range_m,
            long_range_m=self.long_range_m,
            damage=tuple(
                damage_template.create_damage_roll(
                    ability_modifier=ability_modifier,
                )
                for damage_template in damage_templates
            ),
        )

    def with_additional_damage(
        self,
        *additional_damage: DamageTemplate,
        template_id: str | None = None,
        name: str | None = None,
    ) -> "NaturalAttackTemplate":
        """Create a derived template with additinal damage components.

        Args:
            additional_damage: Damage components added to the template.
            template_id: Optional unique template identifier
            name: Optional display name for the template.

        Returns:
            A completed Natural attack template containing additional damage.

        """
        return replace(
            self,
            template_id=template_id or self.template_id,
            name=name or self.name,
            damage=self.damage + additional_damage,
        )


BITE = NaturalAttackTemplate(
    template_id="bite",
    name="Bite",
    attack_range="melee",
    ability_modifier="strength_modifier",
    reach_ft=5,
    reach_m=1.5,
    damage=(
        DamageTemplate(
            dice_count=1,
            die_size=6,
            damage_type="piercing",
            add_ability_modifier=True,
        ),
    ),
)

CLAW = NaturalAttackTemplate(
    template_id="claw",
    name="Claw",
    attack_range="melee",
    ability_modifier="strength_modifier",
    reach_ft=5,
    reach_m=1.5,
    damage=(
        DamageTemplate(
            dice_count=1,
            die_size=6,
            damage_type="slashing",
            add_ability_modifier=True,
        ),
    ),
)
TENTACLE = NaturalAttackTemplate(
    template_id="tentacle",
    name="Tentacle",
    attack_range="melee",
    ability_modifier="strength_modifier",
    reach_ft=10,
    reach_m=3,
    damage=(
        DamageTemplate(
            dice_count=1,
            die_size=8,
            damage_type="bludgeoning",
            add_ability_modifier=True,
        ),
    ),
)
SLAM = NaturalAttackTemplate(
    template_id="slam",
    name="Slam",
    attack_range="melee",
    ability_modifier="strength_modifier",
    reach_ft=5,
    reach_m=1.5,
    damage=(
        DamageTemplate(
            dice_count=1,
            die_size=8,
            damage_type="bludgeoning",
            add_ability_modifier=True,
        ),
    ),
)
