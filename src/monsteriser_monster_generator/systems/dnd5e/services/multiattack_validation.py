"""Validate Multiattack definitions against monster abilities."""

from ..models.actions import (
    AttackAction,
    MultiattackAction,
)
from ..models.base_monster import BaseMonster


def validate_monster_multiattacks(
    monster: BaseMonster,
) -> None:
    """Validate every Multiattack belonging to a monster.

    Args:
        monster: Monster whose Multiattack definitions are validated.

    Raises:
        ValueError: If an action identifier or Multiattack reference
            is invalid.

    """
    actions_by_id = monster.get_abilities_by_id()

    for ability in monster.abilities:
        if not isinstance(ability, MultiattackAction):
            continue

        referenced_action_ids = _get_referenced_action_ids(ability)

        if ability.action_id in referenced_action_ids:
            raise ValueError("Multiattack cannot reference itself")

        missing_action_ids = referenced_action_ids - actions_by_id.keys()

        if missing_action_ids:
            missing_text = ", ".join(sorted(missing_action_ids))
            raise ValueError(f"Multiattack references unknown actions: {missing_text}")

        invalid_action_ids = tuple(
            action_id
            for action_id in sorted(referenced_action_ids)
            if not isinstance(
                actions_by_id[action_id],
                AttackAction,
            )
        )

        if invalid_action_ids:
            invalid_text = ", ".join(invalid_action_ids)
            raise ValueError(f"Multiattack may only reference attack actions: {invalid_text}")


def _get_referenced_action_ids(
    multiattack: MultiattackAction,
) -> set[str]:
    """Return every action identifier referenced by Multiattack."""
    referenced_action_ids = {action_use.action_id for action_use in multiattack.base_sequence}

    for substitution in multiattack.substitutions:
        referenced_action_ids.add(substitution.replaced_action_id)
        referenced_action_ids.update(substitution.replacement_action_ids)

    return referenced_action_ids
