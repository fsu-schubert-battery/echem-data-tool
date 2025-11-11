# Copyright (C) 2025 Friedrich-Schiller-Universität Jena, HIPOLE Jena
# Authors: Christian Stolze, Sebastian Witt, Felix Nagler
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Data container classes for raw measurement data.

This module provides lightweight wrappers for managing data variables
within techniques and auxiliary measurements:

- DataVariable: Individual data arrays with metadata (attributes, dimensions)
- DataGroup: Collections of related data variables

These classes abstract xarray/netCDF operations for data storage and provide
a clean interface for adding, accessing, and managing measurement data
(time series, voltages, currents, temperatures, etc.) within the hierarchical
study structure.

Data groups correspond to the 'data' subgroups within technique_XXX and
auxiliary_XXX groups in the netCDF file format.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

import numpy as np
import xarray as xr


@dataclass
class DataVariable:
    """Represents a data variable with its values and attributes.
    
    This corresponds to individual data arrays within netCDF data groups,
    providing a clean interface for managing measurement data with metadata.
    
    Attributes:
        name: Variable name (e.g., "time", "potential", "current")
        data: Variable data (array-like)
        attributes: Variable attributes (units, description, etc.)
        dimensions: Dimension names for the variable
    """
    name: str
    data: Union[List, np.ndarray]
    attributes: Dict[str, Any] = field(default_factory=dict)
    dimensions: List[str] = field(default_factory=lambda: ["time"])
    
    def to_xarray_variable(self) -> xr.DataArray:
        """Convert to xarray DataArray for analysis and file I/O."""
        return xr.DataArray(
            data=self.data,
            dims=self.dimensions,
            attrs=self.attributes,
            name=self.name
        )


@dataclass
class DataGroup:
    """Represents a data group containing multiple data variables.
    
    This corresponds to the 'data' subgroup within technique and auxiliary groups
    in the netCDF structure. It provides methods for managing collections of
    related data variables with group-level metadata.
    
    Attributes:
        variables: Dictionary of data variables {name: DataVariable}
        attributes: Group-level attributes
    """
    variables: Dict[str, DataVariable] = field(default_factory=dict)
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    def add_variable(self, name: str, data: Union[List, np.ndarray], 
                    attributes: Optional[Dict[str, Any]] = None,
                    dimensions: Optional[List[str]] = None) -> DataVariable:
        """Add a data variable to this group.
        
        Args:
            name: Variable name
            data: Variable data (array-like)
            attributes: Variable attributes (units, description, etc.)
            dimensions: Dimension names (defaults to ["time"])
            
        Returns:
            The created DataVariable
        """
        if dimensions is None:
            dimensions = ["time"]
        
        var = DataVariable(
            name=name,
            data=data,
            attributes=attributes or {},
            dimensions=dimensions
        )
        self.variables[name] = var
        return var
    
    def get_variable(self, name: str) -> Optional[DataVariable]:
        """Get a data variable by name.
        
        Args:
            name: Variable name
            
        Returns:
            DataVariable if found, None otherwise
        """
        return self.variables.get(name)
    
    def remove_variable(self, name: str) -> bool:
        """Remove a data variable.
        
        Args:
            name: Variable name
            
        Returns:
            True if found and removed, False otherwise
        """
        if name in self.variables:
            del self.variables[name]
            return True
        return False
    
    def list_variables(self) -> List[str]:
        """List all variable names in this data group.
        
        Returns:
            List of variable names
        """
        return list(self.variables.keys())
    
    def to_xarray_dataset(self) -> xr.Dataset:
        """Convert to xarray Dataset for analysis and file I/O.
        
        Returns:
            xarray Dataset with all variables and group attributes
        """
        data_vars = {
            name: var.to_xarray_variable() 
            for name, var in self.variables.items()
        }
        return xr.Dataset(data_vars=data_vars, attrs=self.attributes)