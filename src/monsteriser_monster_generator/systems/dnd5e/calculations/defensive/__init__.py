from .damage_adjustments import (
    DAMAGE_ADJUSTMENT_POLICY,
    DamageAdjustmentPolicy,
    calculate_damage_adjustment_multiplier,
    describe_damage_adjustment_policy,
)
from .defensive_cr import (
    DefensiveChallengeRatingResult,
    calculate_monster_defensive_cr,
)
from .effective_health import (
    DefensiveHealthResult,
    calculate_effective_hit_points,
)

__all__ = [
    "DAMAGE_ADJUSTMENT_POLICY",
    "DamageAdjustmentPolicy",
    "DefensiveChallengeRatingResult",
    "DefensiveHealthResult",
    "calculate_damage_adjustment_multiplier",
    "calculate_effective_hit_points",
    "calculate_monster_defensive_cr",
    "describe_damage_adjustment_policy",
]
