"""Export D&D 5E prebuilt action catalogs and templates."""

from .action_catalog import (
    get_all_natural_attack_templates,
    get_recommended_natural_attacks,
    is_recommended_natural_attack,
)
from .action_template import (
    BITE,
    CLAW,
    SLAM,
    TENTACLE,
    DamageTemplate,
    NaturalAttackTemplate,
)

__all__ = [
    "BITE",
    "CLAW",
    "SLAM",
    "TENTACLE",
    "DamageTemplate",
    "NaturalAttackTemplate",
    "get_all_natural_attack_templates",
    "get_recommended_natural_attacks",
    "is_recommended_natural_attack",
]
