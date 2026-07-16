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
