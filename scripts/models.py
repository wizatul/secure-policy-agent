from dataclasses import dataclass
from typing import List

@dataclass
class PolicyRule:
    id: str
    description: str
    severity: str

@dataclass
class RedFlag:
    id: str
    text: str