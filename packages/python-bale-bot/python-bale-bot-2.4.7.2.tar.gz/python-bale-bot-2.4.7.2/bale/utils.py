from __future__ import annotations
from typing import Any

class _Missing:
    __slots__ = ()

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return False

    def __hash__(self):
        return 0

    def __repr__(self):
        return "..."

MISSING: Any = _Missing()