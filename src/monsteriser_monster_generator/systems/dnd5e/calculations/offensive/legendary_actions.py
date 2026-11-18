"""Calculate Legendary Action damage for D&D 5E 2024 Monsters."""

from dataclasses import dataclass

from ...models.base_monster import BaseMonster
from .damage import calculate_action_average_damage


@dataclass(kw_only=True, frozen=True, slots=True)
class LegendaryActionRoutine:
    """Summarise damage contributedby Legendary Action."""

    action_ids: tuple[str, ...]


@dataclass(kw_only=True, frozen=True, slots=True)
class LegendaryActionDamageResult:
    """Summarise damage contributed by Legendary Actions."""

    uses_available: int
    routine: LegendaryActionRoutine
    average_damage_per_round: float


def calculate_legendary_action_damage(
    *,
    monster: BaseMonster,
) -> LegendaryActionDamageResult:
    """Calculate average Legendary Action damage per round."""
    legendary_actions = monster.get_abilities_by_timing(
        "legendary_action",
    )

    empty_routine = LegendaryActionRoutine(
        action_ids=(),
    )

    if monster.legendary_action_uses == 0 or not legendary_actions:
        return LegendaryActionDamageResult(
            uses_available=monster.legendary_action_uses,
            routine=empty_routine,
            average_damage_per_round=0.0,
        )

    actions_by_id = monster.get_abilities_by_id()

    action_damage = {
        action.action_id: calculate_action_average_damage(
            action=action,
            actions_by_id=actions_by_id,
        )
        for action in legendary_actions
    }

    selected_action_ids: list[str] = []
    selected_counts: dict[str, int] = {}
    average_damage_per_round = 0.0

    for _ in range(monster.legendary_action_uses):
        best_action_id: str | None = None
        best_damage = 0.0

        for action in legendary_actions:
            uses = selected_counts.get(
                action.action_id,
                0,
            )

            if action.max_uses_per_round is not None and uses >= action.max_uses_per_round:
                continue

            damage = action_damage[action.action_id]

            if damage <= best_damage:
                continue

            best_action_id = action.action_id
            best_damage = damage

        if best_action_id is None:
            break

        selected_action_ids.append(best_action_id)
        selected_counts[best_action_id] = selected_counts.get(best_action_id, 0) + 1
        average_damage_per_round += best_damage

    return LegendaryActionDamageResult(
        uses_available=monster.legendary_action_uses,
        routine=LegendaryActionRoutine(
            action_ids=tuple(selected_action_ids),
        ),
        average_damage_per_round=average_damage_per_round,
    )
