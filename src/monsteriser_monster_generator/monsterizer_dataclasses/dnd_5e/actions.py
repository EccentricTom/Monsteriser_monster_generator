"""Define actions available to monsters."""

from collections import Counter
from collections.abc import Mapping
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


def generate_multiattack_description(
    *,
    monster_name: str,
    unique_monster: bool,
    multiattack: MultiattackAction,
    actions_by_id: Mapping[str, MonsterAction],
) -> str:
    """Generate a readable description for a multiattack action.

    Args:
        monster_name: The name of the monster making the MultiAttack.
        unique_monster: Whether to use "The" in front of the monster name or not.
        multiattack: The multiattack action to be described.
        actions_by_id: Available actions indexed by ID.

    Returns:
        Generated description of a multiattack.

    """
    base_names = tuple(
        actions_by_id[action_use.action_id].name for action_use in multiattack.base_sequence
    )

    base_description = _describe_ordered_actions(base_names)

    if not unique_monster:
        monster_name = f"The {monster_name}"

    description = f"{monster_name} makes {len(base_names)} attacks: {base_description}"

    substitution_descriptions = tuple(
        _describe_substitutions(
            substitution=substitution,
            actions_by_id=actions_by_id,
        )
        for substitution in multiattack.substitutions
    )

    if substitution_descriptions:
        description += " " + " ".join(substitution_descriptions)

    return description


def _describe_ordered_actions(
    action_names: tuple[str, ...],
) -> str:
    """Describe an ordered collection of action names."""
    if len(action_names) == 1:
        return f"one {action_names[0]} attack"

    counted_names = Counter(action_names)

    # Use a compact count-based description when identical actions
    # are grouped together in the sequence.
    parts: list[str] = []
    seen: set[str] = set()

    for action_name in action_names:
        if action_name in seen:
            continue

        seen.add(action_name)
        count = counted_names[action_name]
        count_text = _number_word(count)

        attack_text = "attack" if count == 1 else "attacks"
        parts.append(f"{count_text} {action_name} {attack_text}")

    if len(parts) == 1:
        return parts[0]

    if len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"

    return f"{', '.join(parts[:-1])}, and {parts[-1]}"


def _describe_substitutions(
    *,
    substitution: ActionSubstitution,
    actions_by_id: Mapping[str, MonsterAction],
) -> str:
    """Describe one substitution rule."""
    replaced_name = actions_by_id[substitution.replaced_action_id].name

    replacement_names = tuple(
        actions_by_id[action_id].name for action_id in substitution.replacement_action_ids
    )

    replacement_text = _join_names(replacement_names)

    if substitution.maximum_replacements == 1:
        return f"It can replace one {replaced_name} attack with {replacement_text}."

    return (
        f"It can replace up to "
        f"{substitution.maximum_replacements} "
        f"{replaced_name} attacks with {replacement_text}."
    )


def _join_names(names: tuple[str, ...]) -> str:
    """Join names into readable prose."""
    if len(names) == 1:
        return f"a {names[0]} attack"

    if len(names) == 2:
        return f"a {names[0]} or {names[1]} attack"

    return f"one of its {', '.join(names[:-1])}, or {names[-1]} attacks"


def _number_word(number: int) -> str:
    """Return a readable number for an attack count."""
    number_words = {
        1: "one",
        2: "two",
        3: "three",
        4: "four",
        5: "five",
        6: "six",
    }

    return number_words.get(number, str(number))
