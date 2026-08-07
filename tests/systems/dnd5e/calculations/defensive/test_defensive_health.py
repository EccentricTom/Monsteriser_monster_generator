"""Test D&D 5E 2024 defensive health calculations."""

from collections.abc import Callable

import pytest
from pytest import raises

from monsteriser_monster_generator.systems.dnd5e.calculations.defensive_health import (
    DAMAGE_ADJUSTMENT_POLICY,
    DefensiveHealthResult,
    calculate_effective_hit_points,
    describe_damage_adjustment_policy,
    get_adjusted_damage_types,
    get_immunity_hit_point_multiplier,
    get_resistance_hit_point_multiplier,
    validate_damage_adjustment_categories,
)
from monsteriser_monster_generator.systems.dnd5e.models.base_monster import (
    BaseMonster,
)
from monsteriser_monster_generator.systems.dnd5e.models.damage_adjustments import (
    DamageAdjustment,
    Immunity,
    Resistance,
    Vulnerability,
)


def test_calculate_effective_hit_points_without_multiplier() -> None:
    """Return base HP when no defensive multiplier applies."""
    monster = BaseMonster(
        name="Test Monster",
        hitpoints=40,
    )

    result = calculate_effective_hit_points(
        monster=monster,
    )

    assert result == DefensiveHealthResult(
        base_hit_points=40,
        hit_point_multiplier=1.0,
        effective_hit_points=40.0,
    )


def test_calculate_effective_hit_points_applies_multiplier() -> None:
    """Apply the supplied defensive HP multiplier."""
    monster = BaseMonster(
        name="Test Monster",
        hitpoints=40,
    )

    result = calculate_effective_hit_points(
        monster=monster,
        hit_point_multiplier=1.5,
    )

    assert result == DefensiveHealthResult(
        base_hit_points=40,
        hit_point_multiplier=1.5,
        effective_hit_points=60.0,
    )


def test_calculate_effective_hit_points_accepts_fractional_result() -> None:
    """Preserve fractional effective hit points."""
    monster = BaseMonster(
        name="Test Monster",
        hitpoints=35,
    )

    result = calculate_effective_hit_points(
        monster=monster,
        hit_point_multiplier=1.5,
    )

    assert result.effective_hit_points == 52.5


def test_calculate_effective_hit_points_rejects_zero_multiplier() -> None:
    """Reject a zero hit-point multiplier."""
    monster = BaseMonster(
        name="Test Monster",
        hitpoints=40,
    )

    with raises(
        ValueError,
        match="Hit-point multiplier must be positive",
    ):
        calculate_effective_hit_points(
            monster=monster,
            hit_point_multiplier=0.0,
        )


@pytest.mark.parametrize(
    "hitpoints",
    [0, -2],
)
def test_calculate_effective_hit_points_rejects_non_positive_hit_points(hitpoints: int) -> None:
    """Reject a monster with non-positive points."""
    monster = BaseMonster(
        name="Test Monster",
        hitpoints=hitpoints,
    )

    with raises(ValueError, match="Monster hit points must be positive"):
        calculate_effective_hit_points(monster=monster)


@pytest.mark.parametrize(
    "multiplier",
    [
        0.0,
        -1.0,
        -0.5,
    ],
)
def test_calculate_effective_hit_points_rejects_invalid_multiplier(
    multiplier: float,
) -> None:
    """Reject non-positive hit-point multipliers."""
    monster = BaseMonster(
        name="Test Monster",
        hitpoints=40,
    )

    with raises(
        ValueError,
        match="Hit-point multiplier must be positive",
    ):
        calculate_effective_hit_points(
            monster=monster,
            hit_point_multiplier=multiplier,
        )


def test_get_adjusted_damage_types_returns_unique_types() -> None:
    """Return each adjusted damage type only once."""
    adjustments = [
        Resistance(damage_type="fire"),
        Resistance(damage_type="cold"),
        Resistance(damage_type="fire"),
    ]

    result = get_adjusted_damage_types(adjustments)

    assert result == frozenset(
        {
            "fire",
            "cold",
        }
    )


def test_get_adjusted_damage_types_accepts_all_adjustment_types() -> None:
    """Normalize all supported damage-adjustment subclasses."""
    adjustments: list[DamageAdjustment] = [
        Resistance(damage_type="fire"),
        Immunity(damage_type="poison"),
        Vulnerability(damage_type="radiant"),
    ]

    result = get_adjusted_damage_types(adjustments)

    assert result == frozenset(
        {
            "fire",
            "poison",
            "radiant",
        }
    )


def test_get_adjusted_damage_types_accepts_empty_adjustments() -> None:
    """Return an empty set when no adjustments are supplied."""
    result = get_adjusted_damage_types([])

    assert result == frozenset()


@pytest.mark.parametrize(
    ("challenge_rating", "expected_multiplier"),
    [
        (1, 2.0),
        (4, 2.0),
        (5, 1.5),
        (10, 1.5),
        (11, 1.25),
        (16, 1.25),
        (17, 1.0),
        (30, 1.0),
    ],
)
def test_get_resistance_hit_point_multiplier(
    challenge_rating: int,
    expected_multiplier: float,
) -> None:
    """Return the resistance multiplier for the CR range."""
    result = get_resistance_hit_point_multiplier(
        expected_challenge_rating=challenge_rating,
    )

    assert result == expected_multiplier


@pytest.mark.parametrize(
    ("challenge_rating", "expected_multiplier"),
    [
        (1, 2.0),
        (4, 2.0),
        (5, 2.0),
        (10, 2.0),
        (11, 1.5),
        (16, 1.5),
        (17, 1.25),
        (30, 1.25),
    ],
)
def test_get_immunity_hit_point_multiplier(
    challenge_rating: int,
    expected_multiplier: float,
) -> None:
    """Return the immunity multiplier for the CR range."""
    result = get_immunity_hit_point_multiplier(
        expected_challenge_rating=challenge_rating,
    )

    assert result == expected_multiplier


@pytest.mark.parametrize(
    "challenge_rating",
    [0, -1],
)
@pytest.mark.parametrize(
    "multiplier_function",
    [
        get_resistance_hit_point_multiplier,
        get_immunity_hit_point_multiplier,
    ],
)
def test_hit_point_multiplier_rejects_non_positive_cr(
    challenge_rating: int,
    multiplier_function: Callable[..., float],
) -> None:
    """Reject a non-positive expected challenge rating."""
    with raises(
        ValueError,
        match="Expected challenge rating must be positive",
    ):
        multiplier_function(
            expected_challenge_rating=challenge_rating,
        )


def test_damage_adjustment_policy_defaults() -> None:
    """Expose the expected default damage-adjustment policy."""
    policy = DAMAGE_ADJUSTMENT_POLICY

    assert policy.significance_threshold == 3
    assert policy.vulnerability_multiplier == 0.5
    assert policy.immunity_overrides_resistance
    assert not policy.allow_cross_category_duplicates
    assert not policy.distinguish_physical_damage


def test_describe_damage_adjustment_policy_includes_threshold() -> None:
    """Describe the configured significance threshold."""
    result = describe_damage_adjustment_policy()

    assert "At least 3 unique damage types" in result


def test_describe_damage_adjustment_policy_includes_vulnerability_multiplier() -> None:
    """Describe the configured vulnerability multiplier."""
    result = describe_damage_adjustment_policy()

    assert "×0.5 hit-point multiplier" in result


def test_describe_damage_adjustment_policy_explains_immunity_precedence() -> None:
    """Explain that immunity takes precedence over resistance."""
    result = describe_damage_adjustment_policy()

    assert "immunity takes precedence" in result


def test_validate_damage_adjustment_categories_accepts_distinct_types() -> None:
    """Accept damage types that occur in only one category."""
    monster = BaseMonster(
        name="Test Monster",
        resistances=[
            Resistance(damage_type="fire"),
        ],
        immunities=[
            Immunity(damage_type="poison"),
        ],
        vulnerabilities=[
            Vulnerability(damage_type="radiant"),
        ],
    )

    validate_damage_adjustment_categories(
        monster=monster,
    )


@pytest.mark.parametrize(
    ("resistances", "immunities", "vulnerabilities", "expected_type"),
    [
        (
            [Resistance(damage_type="fire")],
            [Immunity(damage_type="fire")],
            [],
            "fire",
        ),
        (
            [Resistance(damage_type="cold")],
            [],
            [Vulnerability(damage_type="cold")],
            "cold",
        ),
        (
            [],
            [Immunity(damage_type="poison")],
            [Vulnerability(damage_type="poison")],
            "poison",
        ),
    ],
)
def test_validate_damage_adjustment_categories_rejects_overlap(
    resistances: list[Resistance],
    immunities: list[Immunity],
    vulnerabilities: list[Vulnerability],
    expected_type: str,
) -> None:
    """Reject damage types that occur in multiple adjustment categories."""
    monster = BaseMonster(
        name="Test Monster",
        resistances=resistances,
        immunities=immunities,
        vulnerabilities=vulnerabilities,
    )

    with raises(
        ValueError,
        match=(f"Damage types cannot appear in multiple adjustment categories: {expected_type}"),
    ):
        validate_damage_adjustment_categories(
            monster=monster,
        )


def test_validate_damage_adjustment_categories_reports_all_overlaps() -> None:
    """Report every damage type found in multiple categories."""
    monster = BaseMonster(
        name="Test Monster",
        resistances=[
            Resistance(damage_type="fire"),
            Resistance(damage_type="cold"),
        ],
        immunities=[
            Immunity(damage_type="fire"),
        ],
        vulnerabilities=[
            Vulnerability(damage_type="cold"),
        ],
    )

    with raises(
        ValueError,
        match=("Damage types cannot appear in multiple adjustment categories: cold, fire"),
    ):
        validate_damage_adjustment_categories(
            monster=monster,
        )
