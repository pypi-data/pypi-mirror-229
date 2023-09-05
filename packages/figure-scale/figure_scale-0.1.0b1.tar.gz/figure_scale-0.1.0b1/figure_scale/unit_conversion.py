"""Hold the table of conversion factors from other units to inches."""
from __future__ import annotations

CONVERSION_TABLE: dict[str, float] = {
    "in": 1,
    "ft": 12,
    "yd": 36,
    "m": 0.0254**-1.0,
    "cm": 2.54**-1.0,
    "mm": 25.4**-1.0,
    "pt": 72.0**-1.0,
}
"""Conversion factors from other units to inches."""


def update_conversion_table(**kwargs):
    """Update the conversion table with new values."""
    if any(not isinstance(value, float) for value in kwargs.values()):
        raise TypeError("All values must be floats.")
    if any(value <= 0 for value in kwargs.values()):
        raise ValueError("All values must be positive non-zero numbers.")
    if any(not isinstance(key, str) for key in kwargs):
        raise TypeError("All keys must be strings.")
    if any(key in CONVERSION_TABLE for key in kwargs):
        raise ValueError("Cannot overwrite existing keys.")
    CONVERSION_TABLE.update(kwargs)
