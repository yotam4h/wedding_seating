from __future__ import annotations

from typing import List, Optional, TypedDict


class GuestRequiredFields(TypedDict):
    name: str


class Guest(GuestRequiredFields, total=False):
    group: Optional[str]
    vip: bool
    avoid: List[str]
    friends: List[str]


Table = List[Guest]
Tables = List[Table]
