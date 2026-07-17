"""Define actions available to monsters."""

from dataclasses import dataclass, field
from itertools import combinations, product
from typing import Literal

from .model_types import DamageType

type ActionCategory = Literal["attack", "multiattack", "special", "spellcasting"]

type AttackRange = Literal["melee", "ranged", "melee_or_range"]

type ActionOrigin = Literal[
    "natural",
    "gear",
    "special",
    "custom",
]


@dataclass(kw_only=True, frozen=True, slots=True)
class DamageRoll:
    """One damage component of an attack."""

    dice_count: int
    die_size: int
    modifier: int = 0
    damage_type: DamageType

    def average_damage(self) -> float:
        """Average damage from one damage role."""
        average_die = (self.die_size + 1) / 2

        return self.dice_count * average_die + self.modifier


@dataclass(kw_only=True, frozen=True, slots=True)
class MonsterAction:
    """An action availabel to a monster."""

    action_id: str
    name: str
    category: ActionCategory
    origin: ActionOrigin
    description: str = ""


@dataclass(kw_only=True, frozen=True, slots=True)
class AttackAction(MonsterAction):
    """A monster action that deals damage.

    This allows for a single attact that can have different die rolls for different damage types.
    """

    category: Literal["attack"] = field(default="attack", init=False)
    attack_range: AttackRange
    attack_bonus: int
    damage: tuple[DamageRoll, ...]
    reach_ft: float | None = None
    reach_m: float | None = None
    normal_range_ft: float | None = None
    long_range_ft: float | None = None
    normal_range_m: float | None = None
    long_range_m: float | None = None

    def average_damage(self) -> float:
        """Average damage of the attack."""
        return sum(damage_roll.average_damage() for damage_roll in self.damage)


@dataclass(kw_only=True, frozen=True, slots=True)
class ActionUse:
    """Represent repeated use of an action within a routine."""

    action_id: str
    count: int = 1

    def __post_init__(self) -> None:
        """Validate the action-use count."""
        if self.count < 1:
            raise ValueError("Action-use count must be positive")


@dataclass(kw_only=True, frozen=True, slots=True)
class ActionSubstitution:
    """Describe permitted substitutions in a Multiattack action."""

    replaced_action_id: str
    replacement_action_ids: tuple[str, ...]
    maximum_replacements: int = 1

    def __post_init__(self) -> None:
        """Validate the substitution role."""
        if self.maximum_replacements < 1:
            raise ValueError("A substitution must provide at least one replacement.")


@dataclass(kw_only=True, frozen=True, slots=True)
class MultiattackRoutine:
    """Represent one concrete, valid Multiattack sequence."""

    action_ids: tuple[str, ...]


@dataclass(kw_only=True, frozen=True, slots=True)
class MultiattackAction(MonsterAction):
    """Represent an ordered sequence of attacks with substitutions."""

    category: Literal["multiattack"] = field(
        default="multiattack",
        init=False,
    )
    base_sequence: tuple[ActionUse, ...]
    substitutions: tuple[ActionSubstitution, ...] = ()

    def __post_init__(self) -> None:
        """Validate the existence of a base sequence."""
        if not self.base_sequence:
            raise ValueError("Multiattack should contain at least one action.")

    def valid_routines(self) -> tuple[MultiattackRoutine, ...]:
        """Return every valid routine permitted by this multiattack.

        Returns:
            All valid multiattack routines in tuple form.

        """
        routines: set[tuple[str, ...]] = {
            tuple(action_use.action_id for action_use in self.base_sequence)
        }

        for substitution in self.substitutions:
            routines = self._apply_substitution(
                routines,
                substitution,
            )

        return tuple(MultiattackRoutine(action_ids=routine) for routine in sorted(routines))

    @staticmethod
    def _apply_substitution(
        routines: set[tuple[str, ...]], substitution: ActionSubstitution
    ) -> set[tuple[str, ...]]:
        """Apply one substitution rule to a collection of routines."""
        expanded_routines = set(routines)

        for routine in routines:
            replaceable_indexes = tuple(
                index
                for index, action_id in enumerate(routine)
                if action_id == substitution.replaced_action_id
            )

            new_routines = MultiattackAction._generate_substitutions(
                routine=routine, replaceable_indexes=replaceable_indexes, substitution=substitution
            )
            expanded_routines.update(new_routines)

        return expanded_routines

    @staticmethod
    def _generate_substitutions(
        *,
        routine: tuple[str, ...],
        replaceable_indexes: tuple[int, ...],
        substitution: ActionSubstitution,
    ) -> set[tuple[str, ...]]:
        """Generate valid routines for one substitution rule."""
        generated: set[tuple[str, ...]] = set()

        for replacement_count in range(
            1,
            min(
                substitution.maximum_replacements,
                len(
                    replaceable_indexes,
                ),
            )
            + 1,
        ):
            generated.update(
                MultiattackAction._replace_actions(
                    routine=routine,
                    replaceable_indexes=replaceable_indexes,
                    replacement_action_ids=(substitution.replacement_action_ids),
                    replacement_count=replacement_count,
                )
            )

        return generated

    @staticmethod
    def _replace_actions(
        *,
        routine: tuple[str, ...],
        replaceable_indexes: tuple[int, ...],
        replacement_action_ids: tuple[str, ...],
        replacement_count: int,
    ) -> set[tuple[str, ...]]:
        """Return routines with selected actions replaced."""
        generated: set[tuple[str, ...]] = set()

        for indexes in combinations(
            replaceable_indexes,
            replacement_count,
        ):
            for replacements in product(
                replacement_action_ids,
                repeat=replacement_count,
            ):
                updated_routine = list(routine)

                for index, replacement in zip(indexes, replacements, strict=True):
                    updated_routine[index] = replacement

                generated.add(tuple(updated_routine))

        return generated
