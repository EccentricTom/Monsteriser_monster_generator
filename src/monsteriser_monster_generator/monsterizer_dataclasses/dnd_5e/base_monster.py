"""Define the base monster model."""

from dataclasses import dataclass, field

from dataclasses_json import dataclass_json

from .damage_adjustments import Immunity, Resistance, Vulnerability
from .gear import Gear
from .model_types import MonsterSize


@dataclass_json
@dataclass(kw_only=True)
class BaseMonster:
    """Base dataclass for all monsters.

    All monster types derive from this base.
    """

    name: str
    size: MonsterSize = "medium"
    hitpoints: int = 10
    hit_die_size: int = 8
    hit_die_count: int = 1

    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10

    is_spellcaster: bool = field(default=False)
    is_legendary: bool = field(default=False)
    innate_spellcasting: bool = field(default=False)

    traits: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    bonus_actions: list[str] = field(default_factory=list)
    gear: list[Gear] = field(default_factory=list)

    resistances: list[Resistance] = field(default_factory=list)
    immunities: list[Immunity] = field(default_factory=list)
    vulnerabilities: list[Vulnerability] = field(default_factory=list)

    armor_class: int = field(init=False)
    current_cr: float = field(init=False)

    expected_cr: int = field(default=1)

    def __post_init__(self) -> None:
        """Set up ability modifiers and base armor class."""
        self.strength_modifier = self.calculate_ability_modifier(self.strength)
        self.dexterity_modifier = self.calculate_ability_modifier(self.dexterity)
        self.constitution_modifier = self.calculate_ability_modifier(self.constitution)
        self.intelligence_modifier = self.calculate_ability_modifier(self.intelligence)
        self.wisdom_modifier = self.calculate_ability_modifier(self.wisdom)
        self.charisma_modifier = self.calculate_ability_modifier(self.charisma)
        self.armor_class = 10 + self.dexterity_modifier
        self.current_cr = self.expected_cr

    @staticmethod
    def calculate_ability_modifier(ability_score: int) -> int:
        """Calculate the modifier for an ability score.

        Args:
            ability_score: Ability to modify, e.g. Strength.

        Returns:
            The corresponding modifier.

        """
        return (ability_score - 10) // 2
