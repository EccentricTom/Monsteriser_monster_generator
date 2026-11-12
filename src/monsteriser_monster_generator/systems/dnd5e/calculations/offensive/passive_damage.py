"""Calculations related to passive damage traits for monsters in D&D 5E 2024."""

from dataclasses import dataclass

from ...models.base_monster import BaseMonster
from ...models.traits import PassiveDamageTrait


@dataclass(frozen=True, slots=True, kw_only=True)
class PassiveDamageResult:
    """Summarise the passive damage used for offensive CR."""

    average_damage_per_round: float


def get_passive_damage_expected_targets(
    *,
    trait: PassiveDamageTrait,
) -> float:
    """Return the expected number of passive-damage instances per round."""
    if trait.expected_targets is not None:
        return trait.expected_targets

    if trait.trigger == "aura":
        return 2.0

    return 1.0


def calculate_passive_trait_average_damage(
    *,
    trait: PassiveDamageTrait,
) -> float:
    """Calculate the average damage contributed by a passive damage trait."""
    average_damage = sum(damage.average_damage() for damage in trait.damage)

    expected_targets = get_passive_damage_expected_targets(trait=trait)

    return average_damage * expected_targets


def calculate_passive_damage(
    *,
    monster: BaseMonster,
) -> PassiveDamageResult:
    """Calculate passive damage contributed by monster traits."""
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
