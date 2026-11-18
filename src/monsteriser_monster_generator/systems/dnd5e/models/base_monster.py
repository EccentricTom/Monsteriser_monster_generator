"""Define the base monster model."""

from dataclasses import dataclass, field

from dataclasses_json import dataclass_json

from .actions import MonsterAction
from .damage_adjustments import Immunity, Resistance, Vulnerability
from .gear import Gear
from .model_types import ActionTiming, MonsterSize
from .traits import MonsterTrait


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
    legendary_action_uses: int = 0
    innate_spellcasting: bool = field(default=False)

    traits: list[MonsterTrait] = field(default_factory=list[MonsterTrait])
    abilities: list[MonsterAction] = field(default_factory=list[MonsterAction])
    gear: list[Gear] = field(default_factory=list[Gear])

    resistances: list[Resistance] = field(default_factory=list[Resistance])
    immunities: list[Immunity] = field(default_factory=list[Immunity])
    vulnerabilities: list[Vulnerability] = field(default_factory=list[Vulnerability])

    armor_class: int = field(init=False)
    current_cr: float = field(init=False)

    expected_cr: float = field(default=1)

    def __post_init__(self) -> None:
        """Validate legendary action uses and initialize armor class and CR."""
        if self.legendary_action_uses < 0:
            raise ValueError("Legendary Action uses cannot be negative")
        if self.legendary_action_uses > 0 and not self.is_legendary:
            raise ValueError("A monster with Legendary Action uses must be legendary.")

        self.armor_class = 10 + self.dexterity_modifier
        self.current_cr = self.expected_cr

    @property
    def strength_modifier(self) -> int:
        """Return the modifier for the current Strength score."""
        return self.calculate_ability_modifier(self.strength)

    @property
    def dexterity_modifier(self) -> int:
        """Return the modifier for the current Dexterity score."""
        return self.calculate_ability_modifier(self.dexterity)

    @property
    def constitution_modifier(self) -> int:
        """Return the modifier for the current Constitution score."""
        return self.calculate_ability_modifier(self.constitution)

    @property
    def intelligence_modifier(self) -> int:
        """Return the modifier for the current Intelligence score."""
        return self.calculate_ability_modifier(self.intelligence)

    @property
    def wisdom_modifier(self) -> int:
        """Return the modifier for the current Wisdom score."""
        return self.calculate_ability_modifier(self.wisdom)

    @property
    def charisma_modifier(self) -> int:
        """Return the modifier for the current Charisma score."""
        return self.calculate_ability_modifier(self.charisma)

    @staticmethod
    def calculate_ability_modifier(ability_score: int) -> int:
        """Calculate the modifier for an ability score.

        Args:
            ability_score: Ability to modify, e.g. Strength.

        Returns:
            The corresponding modifier.

        """
        return (ability_score - 10) // 2

    def get_abilities_by_timing(
        self,
        timing: ActionTiming,
    ) -> tuple[MonsterAction, ...]:
        """Return abilities matching an action-economy timing.

        Args:
            timing: Action timing to retrieve.

        Returns:
            Abilities matching the requested timing.

        """
        return tuple(ability for ability in self.abilities if ability.timing == timing)

    def get_abilities_by_id(self) -> dict[str, MonsterAction]:
        """Return abilities indexed by identifier.

        Returns:
            Abilities mapped by their unique action identifiers.

        Raises:
            ValueError: If multiple abilities use the same identifier.

        """
        abilities_by_id: dict[str, MonsterAction] = {}

        for ability in self.abilities:
            if ability.action_id in abilities_by_id:
                raise ValueError(f"Duplicate action identifier: {ability.action_id!r}")
            abilities_by_id[ability.action_id] = ability

        return abilities_by_id

    def get_traits_by_type[TraitType: MonsterTrait](
        self,
        trait_type: type[TraitType],
    ) -> tuple[TraitType, ...]:
        """Return traits matching a specific trait type.

        Args:
            trait_type: Trait model to retrieve.

        Returns:
            Traits matching the requested type

        """
        return tuple(trait for trait in self.traits if isinstance(trait, trait_type))
