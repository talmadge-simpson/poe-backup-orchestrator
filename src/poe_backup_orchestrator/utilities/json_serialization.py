"""Deterministic JSON serialization utilities."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


def deterministic_json(data: Mapping[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
