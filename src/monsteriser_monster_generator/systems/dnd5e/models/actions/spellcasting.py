"""Define monster spellcasting models."""

from dataclasses import dataclass, field
from typing import Literal

from ..model_types import AbilityName
from .attacks import AttackAction, SavingThrowAction
from .base import MonsterAction
from .usage import ActionUsage


@dataclass(kw_only=True, frozen=True, slots=True)
class SpellDefinition:
    """Represent a spell that may be used by a monster."""

    spell_id: str
    name: str
    level: int
    description: str = ""

    attack: AttackAction | None = None
    saving_throw: SavingThrowAction | None = None

    def __post_init__(self) -> None:
        """Validate the spell definition."""
        if self.level < 0:
            raise ValueError("Spell level cannot be negative")
        if self.attack is not None and self.saving_throw is not None:
            raise ValueError(
                "A spell definition cannot contain both an attack and saving-throw action"
            )


@dataclass(kw_only=True, frozen=True, slots=True)
class PreparedSpell:
    """Represent a spell and its monster-specific usage."""

    spell: SpellDefinition
    usage: ActionUsage


@dataclass(kw_only=True, frozen=True, slots=True)
class SpellcastingAction(MonsterAction):
    """Represent a spellcasting action."""

    category: Literal["spellcasting"] = field(
        default="spellcasting",
        init=False,
    )

    spellcasting_ability: AbilityName
    spell_attack_bonus: int
    spell_save_difficulty_class: int
    spells: tuple[PreparedSpell, ...]
