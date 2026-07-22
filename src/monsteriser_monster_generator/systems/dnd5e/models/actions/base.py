"""Define the base action model for monsters."""

from dataclasses import dataclass, field

from ..model_types import (
    ActionCategory,
    ActionOrigin,
    ActionTiming,
)
from .usage import ActionUsage, AtWillUsage, LimitedUsage, RechargeUsage


@dataclass(kw_only=True, frozen=True, slots=True)
class MonsterAction:
    """An action availabel to a monster."""

    action_id: str
    name: str
    category: ActionCategory
    origin: ActionOrigin

    timing: ActionTiming = "action"
    usage: ActionUsage = field(default_factory=AtWillUsage)
    description: str = ""

    def display_name(self) -> str:
        """Return the action name with its usage notation."""
        if isinstance(self.usage, RechargeUsage):
            minimum = self.usage.recharge_minimum

            if minimum == 6:
                return f"{self.name} (Recharge 6)"

            return f"{self.name} (Recharge {minimum} - 6)"

        if isinstance(self.usage, LimitedUsage):
            period = self.usage.period.capitalize()
            return f"{self.name} ({self.usage.uses}/{period})"

        return self.name
