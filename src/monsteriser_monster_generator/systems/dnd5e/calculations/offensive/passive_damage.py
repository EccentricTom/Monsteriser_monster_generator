"""Calculations related to pasive damage traits for monsters in D&D 5E 2024."""

from dataclasses import dataclass

from ...models.base_monster import BaseMonster
from ...models.traits import PassiveDamageTrait


@dataclass(frozen=True, slots=True, kw_only=True)
class PassiveDamageResult:
    """Summarise the passive damage used for offensive CR."""

    average_damage_per_round: float


def calculate_passive_trait_average_damage(
    *,
    trait: PassiveDamageTrait,
) -> float:
    """Calculate the average damage contributed by a passive damage trait."""
    average_damage = sum(damage_roll.average_damage() for damage_roll in trait.damage)

    return average_damage * trait.expected_targets


def calculate_passive_damage(
    *,
    monster: BaseMonster,
) -> PassiveDamageResult:
    """Calculate passive Damage contributed by monster traits."""
    passive_traits = (trait for trait in monster.traits if isinstance(trait, PassiveDamageTrait))

    average_damage_per_round = sum(
        calculate_passive_trait_average_damage(
            trait=trait,
        )
        for trait in passive_traits
    )

    return PassiveDamageResult(
        average_damage_per_round=average_damage_per_round,
    )
