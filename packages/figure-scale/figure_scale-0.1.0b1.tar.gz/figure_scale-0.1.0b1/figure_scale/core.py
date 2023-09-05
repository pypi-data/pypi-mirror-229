"""Module containing the core functionality of the project."""
from __future__ import annotations

import functools
from collections.abc import Sequence
from contextlib import contextmanager
from dataclasses import dataclass, replace
from typing import NamedTuple

from matplotlib.pyplot import rc_context

from figure_scale.unit_conversion import CONVERSION_TABLE


class FigSize(NamedTuple):
    """A named tuple to hold figure size information."""

    width: float
    height: float


GOLDEN_RATIO = (5.0**0.5 - 1.0) / 2.0
"""The golden ratio."""


@dataclass(frozen=True)
class FigureScale(Sequence):
    """Class to hold figure scale information."""

    width: float
    height_abs: float | None = None
    height_rel: float = GOLDEN_RATIO
    units: str = "in"

    def __post_init__(self):
        """Validate the values."""
        if self.units not in CONVERSION_TABLE:
            raise ValueError(
                "Unknown unit: {}. The available options are: {}".format(
                    self.units, ", ".join(CONVERSION_TABLE.keys())
                )
            )

    def replace(self, **kwargs) -> FigureScale:
        """Replace the attributes of the figure scale."""
        return replace(self, **kwargs)

    @contextmanager
    def __call__(self, **kwargs):
        """Replace the attributes of the figure scale."""
        with rc_context({"figure.figsize": self, **kwargs}):
            yield

    def __getitem__(self, index: slice | int):
        """Get the figure size."""
        return self._fig_size[index]

    def __len__(self) -> int:
        """Return the length of the figure size."""
        return len(self._fig_size)

    @functools.cached_property
    def _fig_size(self) -> FigSize:
        """Calculate the figure size."""
        if self.height_abs is None:
            height_abs = self.width * self.height_rel
        else:
            height_abs = self.height_abs

        try:
            factor = CONVERSION_TABLE[self.units]
        except KeyError as err:
            raise ValueError(f"Unknown unit: {self.units}. ") from err

        return FigSize(self.width * factor, height_abs * factor)
