"""Define the base action model for monsters."""

from dataclasses import dataclass, field

from ..model_types import (
    ActionCategory,
    ActionOrigin,
    ActionTiming,
)
from .usage import ActionUsage, AtWillUsage


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
