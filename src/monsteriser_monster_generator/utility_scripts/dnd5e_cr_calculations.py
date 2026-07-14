"""Collection of functions used in CR calculations."""

from monsterizer_dataclasses.dnd5e_dataclasses import BaseMonster


# Attack bonus expectation
def expected_ab_calc(monster: BaseMonster) -> int:
    """Calculate the expected attack bonus of a monster.

    NB: This is an approximation, use best judgement and as a guideline
    """
    expected_cr = monster.expected_cr
    return int(3.5 + expected_cr / 2)


# Difficulty class expection
def expected_dc_calc(monster: BaseMonster) -> int:
    """Calculate the expected difficulty class of a monster.

    NB: This is an approximation, use best judgement and as a guideline
    """
    expected_cr = monster.expected_cr
    return int(11.5 + expected_cr / 2)
