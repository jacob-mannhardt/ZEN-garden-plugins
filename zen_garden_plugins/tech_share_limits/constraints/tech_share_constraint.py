"""Shared helpers for the technology share constraints."""

import numpy as np
import xarray as xr
from zen_garden.model.component_types.constraint import GenericConstraint


class TechShareConstraint(GenericConstraint):
    """Base class with helpers to restrict constraints to binding entries."""

    @staticmethod
    def get_active_entries(
        share: xr.DataArray, carrier_dim: str, is_lower_bound: bool
    ) -> tuple[xr.DataArray, dict[str, np.ndarray]] | None:
        """Return the mask of binding shares and the technologies and carriers.

        Upper bounds bind where the share is finite, lower bounds where the
        share is finite and positive. The returned selection contains only the
        technologies and carriers with at least one binding entry, which keeps
        the size of the constraint small.

        Args:
            share: share parameter indexed by technology, carrier, node, year.
            carrier_dim: name of the carrier dimension of ``share``.
            is_lower_bound: whether ``share`` is a lower bound.

        Returns:
            The mask on the selection and the selection, or ``None`` if no
            entry binds.
        """
        mask = share.copy(data=np.isfinite(share.values))
        if is_lower_bound:
            mask = mask & (share > 0)
        if not mask.any():
            return None
        selection = {}
        for dim in ("set_conversion_technologies", carrier_dim):
            is_active = mask.any([d for d in mask.dims if d != dim]).values
            selection[dim] = mask.coords[dim].values[is_active]
        return mask.sel(selection), selection
