"""Define Multiattack actions and their component routines."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from itertools import combinations, groupby, product
from typing import Literal

from .base import MonsterAction


@dataclass(kw_only=True, frozen=True, slots=True)
class FixedActionUse:
    """Represent a required ability use within multiattack.

    Attributes:
        action_id: Unique identifier of the required ability.
        count: Number of consecutive times the ability is used.

    """

    action_id: str
    count: int = 1

    def __post_init__(self) -> None:
        """Validate the number of ability uses."""
        if self.count < 1:
            raise ValueError("Fixed action-use count must be positive.")


@dataclass(kw_only=True, frozen=True, slots=True)
class ChoiceActionUse:
    """Represent a choice between abilities in a multiattack.

    Attributes:
        action_ids: Identifiers of the abilities that may fill this step.
        count: Number of times the selected ability is used.

    """

    action_ids: tuple[str, ...]
    count: int = 1

    def __post_init__(self) -> None:
        """Validate the ability choice and count."""
        if not self.action_ids:
            raise ValueError("A Multiattack choice requires at least one action")

        if self.count < 1:
            raise ValueError("Choice action-use count must be positive")


type MultiattackStep = FixedActionUse | ChoiceActionUse


@dataclass(kw_only=True, frozen=True, slots=True)
class ActionSubstitution:
    """Describe permitted substitutions in a Multiattack action."""

    replaced_action_id: str
    replacement_action_ids: tuple[str, ...]
    maximum_replacements: int = 1

    def __post_init__(self) -> None:
        """Validate the substitution role."""
        if self.maximum_replacements < 1:
            raise ValueError("A substitution must provide at least one replacement")
        if not self.replacement_action_ids:
            raise ValueError("A subtitution requires at least one replacement")


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
    steps: tuple[MultiattackStep, ...]
    substitutions: tuple[ActionSubstitution, ...] = ()
    description_override: str | None = None

    def __post_init__(self) -> None:
        """Validate the Multiattack definition."""
        if not self.steps:
            raise ValueError("Multiattack must contain at least one step")

    def valid_routines(self) -> tuple[MultiattackRoutine, ...]:
        """Return every valid routine permitted by this multiattack.

        Step choices are expanded first. Substitution rules are then applied to every resulting sequence.

        Returns:
            All valid multiattack routines in tuple form.

        """
        routines = self._generate_step_sequences()

        for substitution in self.substitutions:
            routines = self._apply_substitution(
                routines=routines,
                substitution=substitution,
            )

        return tuple(MultiattackRoutine(action_ids=action_ids) for action_ids in sorted(routines))

    def _generate_step_sequences(self) -> set[tuple[str, ...]]:
        """Expand all Multiattack steps into concrete sequences.

        Returns:
            All sequences generated from fixed and choice steps.

        """
        partial_sequences: set[tuple[str, ...]] = {
            (),
        }

        for step in self.steps:
            step_sequences = self._expand_step(step)
            partial_sequences = {
                existing_sequence + step_sequence
                for existing_sequence in partial_sequences
                for step_sequence in step_sequences
            }

        return partial_sequences

    @staticmethod
    def _expand_step(
        step: MultiattackStep,
    ) -> tuple[tuple[str, ...], ...]:
        """Expand one step into its possible concrete sequences.

        Args:
            step:Fixed or choice-based multiattack step.

        Returns:
            Concrete sequences represented by the step.

        """
        if isinstance(step, FixedActionUse):
            return ((step.action_id,) * step.count,)

        return tuple((action_id,) * step.count for action_id in step.action_ids)

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

            maximum_replacements = min(
                substitution.maximum_replacements,
                len(replaceable_indexes),
            )

            for replacement_count in range(
                1,
                maximum_replacements + 1,
            ):
                expanded_routines.update(
                    MultiattackAction._generate_replacements(
                        routine=routine,
                        replaceable_indexes=replaceable_indexes,
                        replacement_action_ids=(substitution.replacement_action_ids),
                        replacement_count=replacement_count,
                    )
                )

        return expanded_routines

    @staticmethod
    def _generate_replacements(
        *,
        routine: tuple[str, ...],
        replaceable_indexes: tuple[int, ...],
        replacement_action_ids: tuple[str, ...],
        replacement_count: int,
    ) -> set[tuple[str, ...]]:
        """Generate valid routines for one substitution rule."""
        generated_routines: set[tuple[str, ...]] = set()

        for selected_indexes in combinations(
            replaceable_indexes,
            replacement_count,
        ):
            for replacements in product(
                replacement_action_ids,
                repeat=replacement_count,
            ):
                updated_routine = list(routine)

                for index, replacement in zip(selected_indexes, replacements, strict=True):
                    updated_routine[index] = replacement

                generated_routines.add(tuple(updated_routine))

        return generated_routines

    def generate_description(
        self,
        *,
        monster_name: str,
        unique_monster: bool,
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
        if self.description_override is not None:
            return self.description_override

        base_action_ids = self._description_action_ids()

        base_names = tuple(actions_by_id[action_id].name for action_id in base_action_ids)

        base_description = _describe_ordered_actions(base_names)

        if not unique_monster:
            monster_name = f"The {monster_name}"

        description = f"{monster_name} makes {len(base_names)} attacks: {base_description}"

        substitution_descriptions = tuple(
            _describe_substitutions(
                substitution=substitution,
                actions_by_id=actions_by_id,
            )
            for substitution in self.substitutions
        )

        if substitution_descriptions:
            description += " " + " ".join(substitution_descriptions)

        return description

    def _description_action_ids(self) -> tuple[str, ...]:
        """Return one representative sequence for description text.

        Fixed steps are included directly. For choice steps, the first listen action is used as the representative option.

        Returns:
            Representatvie ordered action identifiers.

        """
        action_ids: list[str] = []

        for step in self.steps:
            if isinstance(step, FixedActionUse):
                action_ids.extend([step.action_id] * step.count)
                continue
            action_ids.extend([step.action_ids[0] * step.count])

        return tuple(action_ids)


def _describe_ordered_actions(
    action_names: tuple[str, ...],
) -> str:
    """Describe an ordered collection of action names."""
    parts: list[str] = []

    for action_name, grouped_names in groupby(action_names):
        count = sum(1 for _ in grouped_names)
        attack_word = "attack" if count == 1 else "attacks"

        parts.append(f"{_number_word(count)} {action_name} {attack_word}")

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
