"""Validate Multiattack definitions against monster abilities."""

from ..models.actions import (
    FixedActionUse,
    MultiattackAction,
)
from ..models.base_monster import BaseMonster


def validate_monster_multiattacks(
    monster: BaseMonster,
) -> None:
    """Validate every Multiattack belonging to a monster."""
    actions_by_id = monster.get_abilities_by_id()

    for ability in monster.abilities:
        if not isinstance(
            ability,
            MultiattackAction,
        ):
            continue

        referenced_action_ids = _get_referenced_action_ids(ability)

        if ability.action_id in referenced_action_ids:
            raise ValueError("Multiattack cannot reference itself")

        missing_action_ids = referenced_action_ids - actions_by_id.keys()

        if missing_action_ids:
            missing_text = ", ".join(sorted(missing_action_ids))

            raise ValueError(f"Multiattack references unknown actions: {missing_text}")

        nested_multiattack_ids = tuple(
            action_id
            for action_id in sorted(referenced_action_ids)
            if isinstance(
                actions_by_id[action_id],
                MultiattackAction,
            )
        )

        if nested_multiattack_ids:
            nested_text = ", ".join(nested_multiattack_ids)

            raise ValueError(f"Multiattack cannot reference another Multiattack: {nested_text}")

        invalid_timing_ids = tuple(
            action_id
            for action_id in sorted(referenced_action_ids)
            if actions_by_id[action_id].timing != "action"
        )

        if invalid_timing_ids:
            invalid_text = ", ".join(invalid_timing_ids)

            raise ValueError(
                f"Multiattack may only reference action-timing abilities: {invalid_text}"
            )


def _get_referenced_action_ids(
    multiattack: MultiattackAction,
) -> set[str]:
    """Return every action identifier referenced by Multiattack."""
    referenced_action_ids: set[str] = set()

    for step in multiattack.steps:
        if isinstance(step, FixedActionUse):
            referenced_action_ids.add(step.action_id)
        else:
            referenced_action_ids.update(step.action_ids)

    for substitution in multiattack.substitutions:
        referenced_action_ids.add(substitution.replaced_action_id)
        referenced_action_ids.update(substitution.replacement_action_ids)

    return referenced_action_ids
