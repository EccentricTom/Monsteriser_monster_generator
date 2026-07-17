"""Define usage restrictions for monster abilities."""

from dataclasses import dataclass, field
from typing import Literal

from ..model_types import RechargeValue


@dataclass(kw_only=True, frozen=True, slots=True)
class AtWillUsage:
    """Represent an ability that can be used at will."""

    usage_type: Literal["at_will"] = field(
        default="at_will",
        init=False,
    )


@dataclass(kw_only=True, frozen=True, slots=True)
class LimitedUsage:
    """Repesent an ability that has a limited number of uses."""

    uses: int
    period: Literal["day", "rest"]

    usage_type: Literal["limited"] = field(
        default="limited",
        init=False,
    )

    def __post_init__(self) -> None:
        """Validate that the ability can be used at least once."""
        if self.uses < 1:
            raise ValueError("Limited use ability need to be usuable at least once.")


@dataclass(kw_only=True, frozen=True, slots=True)
class RechargeUsage:
    """Represent an ability that recharges on specified d6 results."""

    recharge_minimum: RechargeValue

    usage_type: Literal["recharge"] = field(
        default="recharge",
        init=False,
    )

    @property
    def recharge_probability(self) -> float:
        """Return the probability of recharging on a d6 roll."""
        successfull_results = 7 - self.recharge_minimum
        return successfull_results / 6


type ActionUsage = AtWillUsage | LimitedUsage | RechargeUsage
