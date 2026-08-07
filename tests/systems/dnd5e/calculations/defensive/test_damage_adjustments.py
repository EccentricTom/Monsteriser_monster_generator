"""Test D&D 5E 2024 defensive health calculations."""

from collections.abc import Callable

import pytest
from pytest import raises

from monsteriser_monster_generator.systems.dnd5e.calculations.defensive.damage_adjustments import (
    DAMAGE_ADJUSTMENT_POLICY,
    describe_damage_adjustment_policy,
    get_immunity_hit_point_multiplier,
    get_resistance_hit_point_multiplier,
    has_significant_damage_adjustments,
    validate_damage_adjustment_categories,
)
from monsteriser_monster_generator.systems.dnd5e.calculations.defensive.effective_health import (
    calculate_damage_adjustment_multiplier,
    get_adjusted_damage_types,
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


@pytest.mark.parametrize(
    ("adjustments", "expected"),
    [
        (
            [
                Resistance(damage_type="fire"),
                Resistance(damage_type="cold"),
            ],
            False,
        ),
        (
            [
                Resistance(damage_type="fire"),
                Resistance(damage_type="cold"),
                Resistance(damage_type="lightning"),
            ],
            True,
        ),
        (
            [
                Resistance(damage_type="fire"),
                Resistance(damage_type="fire"),
                Resistance(damage_type="cold"),
            ],
            False,
        ),
    ],
)
def test_has_significant_damage_adjustments(
    adjustments: list[DamageAdjustment],
    expected: bool,
) -> None:
    """Determine significance from unique damage types."""
    result = has_significant_damage_adjustments(
        adjustments,
    )

    assert result is expected


def test_damage_adjustment_multiplier_defaults_to_one() -> None:
    """Return no adjustment when the monster has none."""
    monster = BaseMonster(
        name="Test Monster",
        expected_cr=5,
    )

    result = calculate_damage_adjustment_multiplier(
        monster=monster,
    )

    assert result == 1.0


def test_damage_adjustment_multiplier_ignores_insignificant_resistance() -> None:
    """Ignore fewer than three unique resistances."""
    monster = BaseMonster(
        name="Test Monster",
        resistances=[
            Resistance(damage_type="fire"),
            Resistance(damage_type="cold"),
        ],
        expected_cr=5,
    )

    result = calculate_damage_adjustment_multiplier(
        monster=monster,
    )

    assert result == 1.0


def test_damage_adjustment_multiplier_applies_resistance() -> None:
    """Apply the CR-based resistance multiplier."""
    monster = BaseMonster(
        name="Test Monster",
        resistances=[
            Resistance(damage_type="fire"),
            Resistance(damage_type="cold"),
            Resistance(damage_type="lightning"),
        ],
        expected_cr=5,
    )

    result = calculate_damage_adjustment_multiplier(
        monster=monster,
    )

    assert result == 1.5


def test_damage_adjustment_multiplier_applies_immunity() -> None:
    """Apply the CR-based immunity multiplier."""
    monster = BaseMonster(
        name="Test Monster",
        immunities=[
            Immunity(damage_type="fire"),
            Immunity(damage_type="cold"),
            Immunity(damage_type="lightning"),
        ],
        expected_cr=11,
    )

    result = calculate_damage_adjustment_multiplier(
        monster=monster,
    )

    assert result == 1.5


def test_damage_adjustment_multiplier_prefers_immunity_over_resistance() -> None:
    """Use immunity rather than stacking qualifying defenses."""
    monster = BaseMonster(
        name="Test Monster",
        resistances=[
            Resistance(damage_type="fire"),
            Resistance(damage_type="cold"),
            Resistance(damage_type="lightning"),
        ],
        immunities=[
            Immunity(damage_type="poison"),
            Immunity(damage_type="psychic"),
            Immunity(damage_type="necrotic"),
        ],
        expected_cr=5,
    )

    result = calculate_damage_adjustment_multiplier(
        monster=monster,
    )

    assert result == 2.0


def test_damage_adjustment_multiplier_applies_vulnerability() -> None:
    """Halve effective HP for significant vulnerabilities."""
    monster = BaseMonster(
        name="Test Monster",
        vulnerabilities=[
            Vulnerability(damage_type="fire"),
            Vulnerability(damage_type="cold"),
            Vulnerability(damage_type="radiant"),
        ],
        expected_cr=5,
    )

    result = calculate_damage_adjustment_multiplier(
        monster=monster,
    )

    assert result == 0.5


def test_damage_adjustment_multiplier_ignores_insignificant_vulnerability() -> None:
    """Ignore fewer than three unique vulnerabilities."""
    monster = BaseMonster(
        name="Test Monster",
        vulnerabilities=[
            Vulnerability(damage_type="fire"),
            Vulnerability(damage_type="cold"),
        ],
        expected_cr=5,
    )

    result = calculate_damage_adjustment_multiplier(
        monster=monster,
    )

    assert result == 1.0


def test_damage_adjustment_multiplier_combines_resistance_and_vulnerability() -> None:
    """Apply vulnerability after a qualifying resistance multiplier."""
    monster = BaseMonster(
        name="Test Monster",
        resistances=[
            Resistance(damage_type="fire"),
            Resistance(damage_type="cold"),
            Resistance(damage_type="lightning"),
        ],
        vulnerabilities=[
            Vulnerability(damage_type="radiant"),
            Vulnerability(damage_type="psychic"),
            Vulnerability(damage_type="force"),
        ],
        expected_cr=5,
    )

    result = calculate_damage_adjustment_multiplier(
        monster=monster,
    )

    assert result == 0.75


def test_damage_adjustment_multiplier_combines_immunity_and_vulnerability() -> None:
    """Apply vulnerability after a qualifying immunity multiplier."""
    monster = BaseMonster(
        name="Test Monster",
        immunities=[
            Immunity(damage_type="fire"),
            Immunity(damage_type="cold"),
            Immunity(damage_type="lightning"),
        ],
        vulnerabilities=[
            Vulnerability(damage_type="radiant"),
            Vulnerability(damage_type="psychic"),
            Vulnerability(damage_type="force"),
        ],
        expected_cr=5,
    )

    result = calculate_damage_adjustment_multiplier(
        monster=monster,
    )

    assert result == 1.0


@pytest.mark.parametrize(
    "expected_challenge_rating",
    [0, -1],
)
def test_damage_adjustment_multiplier_rejects_non_positive_cr(
    expected_challenge_rating: int,
) -> None:
    """Reject a non-positive expected challenge rating."""
    monster = BaseMonster(name="Test Monster", expected_cr=expected_challenge_rating)

    with raises(
        ValueError,
        match="Expected challenge rating must be positive",
    ):
        calculate_damage_adjustment_multiplier(
            monster=monster,
        )
