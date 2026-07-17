"""Associate recommended natural attacks with monster types."""

from .action_template import BITE, CLAW, SLAM, TENTACLE, NaturalAttackTemplate
from .model_types import MonsterType

RECOMMENDED_NATURAL_ATTACKS: dict[MonsterType, tuple[NaturalAttackTemplate, ...]] = {
    "Aberration": (BITE, CLAW, TENTACLE),
    "Beast": (BITE, CLAW, TENTACLE),
    "Celestial": (SLAM,),
    "Construct": (SLAM,),
    "Dragon": (
        BITE,
        CLAW,
    ),
    "Elemental": (SLAM,),
    "Fey": (CLAW,),
    "Fiend": (
        BITE,
        CLAW,
    ),
    "Giant": (SLAM,),
    "Humanoid": (),
    "Monstrosity": (
        BITE,
        CLAW,
        TENTACLE,
    ),
    "Ooze": (SLAM,),
    "Plant": (
        SLAM,
        TENTACLE,
    ),
    "Undead": (
        BITE,
        CLAW,
        SLAM,
    ),
}


def get_recommended_natural_attacks(
    monster_type: MonsterType,
) -> tuple[NaturalAttackTemplate, ...]:
    """Return recommended natural attacks for a monster type.

    These are recommendations only, and can be adjusted with additional damage riders.

    Args:
        monster_type: The type of monster being queried.

    Returns:
        Recommened immutable natural attack templates.

    """
    return RECOMMENDED_NATURAL_ATTACKS[monster_type]


def is_recommended_natural_attack(
    *, monster_type: MonsterType, template: NaturalAttackTemplate
) -> bool:
    """Check if natural attack template fits the monster type.

    Args:
        monster_type: the type of monster being checked.
        template: The natural attack template to be checked.

    Returns:
        Whether the template suits the passed monster type.

    """
    return template in RECOMMENDED_NATURAL_ATTACKS[monster_type]


def get_all_natural_attack_templates() -> tuple[NaturalAttackTemplate, ...]:
    """Return all unique natural attack templates."""
    templates_by_id: dict[str, NaturalAttackTemplate] = {}

    for templates in RECOMMENDED_NATURAL_ATTACKS.values():
        for template in templates:
            templates_by_id[template.template_id] = template

    return tuple(templates_by_id.values())
