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
Data handling classes for electrochemical data.

This module provides classes for managing data variables and data groups
that correspond to the 'data' subgroups within technique and auxiliary groups
in the netCDF file structure.

The module provides a clean abstraction for:
- DataVariable: Individual data arrays with metadata
- DataGroup: Collections of data variables (netCDF groups)

Example:
    ```python
    from echem_data_tool.file.data import DataVariable, DataGroup
    
    # Create data group for a technique
    data_group = DataGroup()
    
    # Add variables with metadata
    data_group.add_variable("time", [0, 1, 2, 3], {"units": "s"})
    data_group.add_variable("potential", [0.1, 0.2, 0.3, 0.4], {"units": "V"})
    data_group.add_variable("current", [0.01, 0.02, 0.01, 0.0], {"units": "A"})
    
    # Access variables
    time_data = data_group.get_variable("time")
    print(f"Time units: {time_data.attributes['units']}")
    
    # Convert to xarray for analysis
    dataset = data_group.to_xarray_dataset()
    ```
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