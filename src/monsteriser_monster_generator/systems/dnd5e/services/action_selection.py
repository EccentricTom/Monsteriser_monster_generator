"""Control the selection of prebuilt monster actions."""

from dataclasses import dataclass

from ..catalogs.action_catalog import is_recommended_natural_attack
from ..catalogs.action_template import NaturalAttackTemplate
from ..models.model_types import MonsterType


@dataclass(kw_only=True, frozen=True, slots=True)
class ActionSelectionPolicy:
    """Control which prebuilt attacks may be selected."""

    allow_cross_type_attacks: bool = False


def natural_attack_is_available(
    *, monster_type: MonsterType, template: NaturalAttackTemplate, policy: ActionSelectionPolicy
) -> bool:
    """Return whether a natural attack may be selected.

    Args:
        monster_type: Type of monster being created.
        template: Natural attack being considered.
        policy: ActionSelectionPolicy,

    Returns:
        whether the template is available.

    """
    if is_recommended_natural_attack(monster_type=monster_type, template=template):
        return True

    return policy.allow_cross_type_attacks
