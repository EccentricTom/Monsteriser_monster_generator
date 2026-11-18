"""Tests for legendary action calculations for D&D 5e 2024 Monsters."""

from monsteriser_monster_generator.systems.dnd5e.calculations.offensive.legendary_actions import (
    LegendaryActionDamageResult,
    LegendaryActionRoutine,
    calculate_legendary_action_damage,
)
from monsteriser_monster_generator.systems.dnd5e.models.actions import (
    AttackAction,
    DamageRoll,
    SavingThrowAction,
)
from monsteriser_monster_generator.systems.dnd5e.models.base_monster import (
    BaseMonster,
)


def create_legendary_attack(
    *,
    action_id: str,
    dice_count: int,
    die_size: int,
    modifier: int = 0,
    max_uses_per_round: int | None = None,
) -> AttackAction:
    """Create a Legendary Action attack for tests."""
    return AttackAction(
        action_id=action_id,
        name=action_id.replace("_", " ").title(),
        origin="natural",
        timing="legendary_action",
        attack_range="melee",
        attack_bonus=7,
        reach_ft=10,
        damage=(
            DamageRoll(
                dice_count=dice_count,
                die_size=die_size,
                modifier=modifier,
                damage_type="slashing",
            ),
        ),
        max_uses_per_round=max_uses_per_round,
    )


def test_legendary_action_damage_uses_strongest_action() -> None:
    """Use the strongest unrestricted Legendary Action for every use."""
    claw = create_legendary_attack(
        action_id="claw",
        dice_count=2,
        die_size=6,
        modifier=3,
    )

    tail = create_legendary_attack(
        action_id="tail",
        dice_count=2,
        die_size=8,
        modifier=3,
    )

    monster = BaseMonster(
        name="Legendary Monster",
        is_legendary=True,
        legendary_action_uses=3,
        abilities=[
            claw,
            tail,
        ],
    )

    result = calculate_legendary_action_damage(
        monster=monster,
    )

    assert result == LegendaryActionDamageResult(
        uses_available=3,
        routine=LegendaryActionRoutine(
            action_ids=(
                "tail",
                "tail",
                "tail",
            ),
        ),
        average_damage_per_round=36.0,
    )


def test_legendary_action_damage_respects_maximum_uses_per_round() -> None:
    """Use a restricted Legendary Action only up to its per-round limit."""
    sonic_boom = create_legendary_attack(
        action_id="sonic_boom",
        dice_count=4,
        die_size=10,
        modifier=0,
        max_uses_per_round=1,
    )

    tail_swipe = create_legendary_attack(
        action_id="tail_swipe",
        dice_count=2,
        die_size=8,
        modifier=3,
    )

    monster = BaseMonster(
        name="Legendary Monster",
        is_legendary=True,
        legendary_action_uses=3,
        abilities=[
            sonic_boom,
            tail_swipe,
        ],
    )

    result = calculate_legendary_action_damage(
        monster=monster,
    )

    assert result == LegendaryActionDamageResult(
        uses_available=3,
        routine=LegendaryActionRoutine(
            action_ids=(
                "sonic_boom",
                "tail_swipe",
                "tail_swipe",
            ),
        ),
        average_damage_per_round=46.0,
    )


def test_legendary_action_damage_ignores_non_damaging_action() -> None:
    """Ignore non-damaging options when selecting Legendary Action damage."""
    menacing_presence = SavingThrowAction(
        action_id="menacing_presence",
        name="Menacing Presence",
        origin="special",
        timing="legendary_action",
        ability="wisdom",
        difficulty_class=15,
        failure_effect_str="the target is frightened",
        max_uses_per_round=1,
    )

    tail = create_legendary_attack(
        action_id="tail",
        dice_count=2,
        die_size=8,
        modifier=3,
    )

    monster = BaseMonster(
        name="Legendary Monster",
        is_legendary=True,
        legendary_action_uses=3,
        abilities=[
            menacing_presence,
            tail,
        ],
    )

    result = calculate_legendary_action_damage(
        monster=monster,
    )

    assert result == LegendaryActionDamageResult(
        uses_available=3,
        routine=LegendaryActionRoutine(
            action_ids=(
                "tail",
                "tail",
                "tail",
            ),
        ),
        average_damage_per_round=36.0,
    )


def test_legendary_action_damage_returns_zero_when_actions_do_no_damage() -> None:
    """Return zero when no Legendary Action deals damage."""
    frighten = SavingThrowAction(
        action_id="frighten",
        name="Frighten",
        origin="special",
        timing="legendary_action",
        ability="wisdom",
        difficulty_class=15,
        failure_effect_str="the target is frightened",
        max_uses_per_round=1,
    )

    monster = BaseMonster(
        name="Legendary Monster",
        is_legendary=True,
        legendary_action_uses=3,
        abilities=[frighten],
    )

    result = calculate_legendary_action_damage(
        monster=monster,
    )

    assert result == LegendaryActionDamageResult(
        uses_available=3,
        routine=LegendaryActionRoutine(
            action_ids=(),
        ),
        average_damage_per_round=0.0,
    )


def test_legendary_action_damage_returns_zero_without_uses() -> None:
    """Return zero when the monster has no Legendary Action uses."""
    tail = create_legendary_attack(
        action_id="tail",
        dice_count=2,
        die_size=8,
        modifier=3,
    )

    monster = BaseMonster(
        name="Legendary Monster",
        is_legendary=True,
        legendary_action_uses=0,
        abilities=[tail],
    )

    result = calculate_legendary_action_damage(
        monster=monster,
    )

    assert result == LegendaryActionDamageResult(
        uses_available=0,
        routine=LegendaryActionRoutine(
            action_ids=(),
        ),
        average_damage_per_round=0.0,
    )
