from dataclasses import dataclass, field

@dataclass
class BaseMonster:
    name: str
    size: str = field(default="medium")
    hitpoints: int = field(default=10)
    hit_die_size: int = field(default=8)
    hit_die_num: int = field(default=1)
