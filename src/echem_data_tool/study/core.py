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
Core classes for the study module.

This module defines the main hierarchical classes that form the structure
of an electrochemical study:
- StudyObject: Top-level container for organizing electrochemical experiments
- Cell: Cell groups with metadata and measurements
- Technique: Electrochemical measurement techniques
- Auxiliary: Auxiliary measurement data (temperature, pressure, etc.)
- Group: Organizational units for related techniques/auxiliaries

These classes provide the core functionality for building hierarchical study
structures that can be saved to and loaded from netCDF files according to
the file format specification in design-docs/file_format_specs.md. This 
hierarchy is as follows:

Study (Root)
├── Metadata (study-level)
├── Cells/
│   ├── Cell 1
│   │   ├── Metadata (cell-level)
│   │   ├── Groups/
│   │   │   ├── Group 1
│   │   │   │   ├── Technique 1 (with data variables)
│   │   │   │   ├── Technique 2
│   │   │   │   └── Auxiliary 1 (with data variables)
│   │   │   └── Group 2
│   │   │       ├── Technique 3
│   │   │       └── Auxiliary 2
│   │   ├── Ungrouped Techniques...
│   │   └── Ungrouped Auxiliaries...
│   └── Cell 2
│       ├── Metadata
│       ├── Groups...
│       └── [Techniques/Auxiliaries]
└── [Future Extensions]

"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import xarray as xr

from .metadata import StudyMetadata, CellMetadata, TechniqueMetadata, AuxiliaryMetadata, GroupMetadata
from .data import DataVariable, DataGroup


# =============================================================================
# HIERARCHICAL CLASSES  
# =============================================================================

class Technique:
    """Represents a technique with metadata and data.
    
    Corresponds to technique_XXX_YYYY groups in the netCDF structure.
    
    The technique provides two main properties:
    - .metadata: Access to technique metadata (TechniqueMetadata)
    - .data: Access to data variables (DataGroup)
    """
    
    def __init__(self, name: str, cell: Optional['Cell'] = None):
        self.name = name
        self.metadata = TechniqueMetadata()
        self._data = DataGroup()

    @property
    def data(self) -> DataGroup:
        """Access to the data group containing all data variables."""
        return self._data
    
    def to_xarray_group(self) -> xr.Dataset:
        """Convert to xarray Dataset for this technique."""
        # Create the data subgroup
        data_ds = self._data.to_xarray_dataset()
        
        # For now, we'll flatten the structure since xarray groups are complex
        # The metadata will be stored as attributes on the main dataset
        data_ds.attrs.update(self.metadata.to_netcdf_attrs())
        
        return data_ds


class Auxiliary:
    """Represents auxiliary data with metadata and data.
    
    Corresponds to auxiliary_XXX_YYYY groups in the netCDF structure.
    
    The auxiliary provides two main properties:
    - .metadata: Access to auxiliary metadata (AuxiliaryMetadata)
    - .data: Access to data variables (DataGroup)
    """
    
    def __init__(self, name: str, cell: Optional['Cell'] = None):
        self.name = name
        self.metadata = AuxiliaryMetadata()
        self._data = DataGroup()
    
    @property
    def data(self) -> DataGroup:
        """Access to the data group containing all data variables."""
        return self._data
    
    def to_xarray_group(self) -> xr.Dataset:
        """Convert to xarray Dataset for this auxiliary."""
        # Create the data subgroup
        data_ds = self._data.to_xarray_dataset()
        
        # Add metadata as attributes
        data_ds.attrs.update(self.metadata.to_netcdf_attrs())
        
        return data_ds

class Group:
    """Represents a technique/auxiliary group with metadata and member management.
    
    Groups are organizational units that contain related techniques and/or 
    auxiliary measurements. They provide:
    - Group-specific metadata
    - Methods to add/remove techniques and auxiliaries
    - Access to all group members
    
    Example:
        ```python
        cv_group = cell.add_group("CV_Analysis")
        cv_group.metadata.description = "Rate capability study"
        cv_technique = cv_group.add_technique("technique_001_CV")
        ```
    """
    
    def __init__(self, id: int, name: str, cell: Optional['Cell'] = None):
        """Initialize group.
        
        Args:
            id: Unique group ID within the cell
            name: Group name
            cell: Reference to parent CellGroup
        """
        self.id = id
        self.name = name
        self.metadata = GroupMetadata(id=id, name=name)
        
        # Group members
        self.techniques: Dict[str, 'Technique'] = {}
        self.auxiliary: Dict[str, 'Auxiliary'] = {}
    
    def add_technique(self, technique: Union['Technique', List['Technique']]) -> None:
        """Add technique(s) to this group.
        
        Args:
            technique: Technique object or list of Technique objects to add to this group
        """
        # Handle single technique
        if not isinstance(technique, list):
            # Set group references in metadata
            technique.metadata.group_id = self.id
            technique.metadata.group_name = self.name
            self.techniques[technique.name] = technique
            return
        
        # Handle list of techniques
        for tech in technique:
            # Set group references in metadata
            tech.metadata.group_id = self.id
            tech.metadata.group_name = self.name
            self.techniques[tech.name] = tech
    
    def add_auxiliary(self, auxiliary: Union['Auxiliary', List['Auxiliary']]) -> None:
        """Add auxiliary data to this group.
        
        Args:
            auxiliary: Auxiliary object or list of Auxiliary objects to add to this group
        """
        # Handle single auxiliary
        if not isinstance(auxiliary, list):
            # Set group references in metadata
            auxiliary.metadata.group_id = self.id
            auxiliary.metadata.group_name = self.name
            self.auxiliary[auxiliary.name] = auxiliary
            return
        
        # Handle list of auxiliaries
        for aux in auxiliary:
            # Set group references in metadata
            aux.metadata.group_id = self.id
            aux.metadata.group_name = self.name
            self.auxiliary[aux.name] = aux
    
    def remove_technique(self, technique: Union['Technique', List['Technique']]) -> Union[bool, List[bool]]:
        """Remove technique(s) from this group.
        
        Args:
            technique: Technique object or list of Technique objects to remove
            
        Returns:
            True/False if single technique was found and removed, or list of True/False for each technique
        """
        # Handle single technique
        if not isinstance(technique, list):
            if technique.name in self.techniques and self.techniques[technique.name] is technique:
                # Clear group references in metadata
                technique.metadata.group_id = None
                technique.metadata.group_name = None
                del self.techniques[technique.name]
                return True
            return False
        
        # Handle list of techniques
        results = []
        for tech in technique:
            if tech.name in self.techniques and self.techniques[tech.name] is tech:
                # Clear group references in metadata
                tech.metadata.group_id = None
                tech.metadata.group_name = None
                del self.techniques[tech.name]
                results.append(True)
            else:
                results.append(False)
        
        return results
    
    def remove_auxiliary(self, auxiliary: Union['Auxiliary', List['Auxiliary']]) -> Union[bool, List[bool]]:
        """Remove auxiliary data from this group.
        
        Args:
            auxiliary: Auxiliary object or list of Auxiliary objects to remove
            
        Returns:
            True/False if single auxiliary was found and removed, or list of True/False for each auxiliary
        """
        # Handle single auxiliary
        if not isinstance(auxiliary, list):
            if auxiliary.name in self.auxiliary and self.auxiliary[auxiliary.name] is auxiliary:
                # Clear group references in metadata
                auxiliary.metadata.group_id = None
                auxiliary.metadata.group_name = None
                del self.auxiliary[auxiliary.name]
                return True
            return False
        
        # Handle list of auxiliaries
        results = []
        for aux in auxiliary:
            if aux.name in self.auxiliary and self.auxiliary[aux.name] is aux:
                # Clear group references in metadata
                aux.metadata.group_id = None
                aux.metadata.group_name = None
                del self.auxiliary[aux.name]
                results.append(True)
            else:
                results.append(False)
        
        return results
    
    def list_techniques(self) -> List[str]:
        """List all technique names in this group."""
        return list(self.techniques.keys())
    
    def list_auxiliary(self) -> List[str]:
        """List all auxiliary names in this group."""
        return list(self.auxiliary.keys())
    
    def list_all(self) -> Dict[str, Union['Technique', 'Auxiliary']]:
        """Get all group members (techniques + auxiliaries)."""
        members = {}
        members.update(self.techniques)
        members.update(self.auxiliary)
        return members
    
    def count_all(self) -> int:
        """Get total number of members in this group."""
        return len(self.techniques) + len(self.auxiliary)
    
    def is_empty(self) -> bool:
        """Check if group has no members."""
        return self.count_all() == 0


class Cell:
    """Represents a cell with metadata, techniques, and auxiliary data.
    
    Corresponds to cell_XXX groups in the netCDF structure.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.metadata = CellMetadata()
        self.groups: Dict[str, Group] = {}
        self.techniques: Dict[str, Technique] = {}
        self.auxiliary: Dict[str, Auxiliary] = {}
    
    def add_technique(self, name: str, overwrite: bool = False) -> Technique:
        """Add a technique to this cell.
    
        Args:
            name: Technique name (e.g., "technique_001_CV")
            overwrite: If False (default), raises ValueError if technique already exists.
                      If True, overwrites existing technique.
    
        Returns:
            The created Technique
    
        Raises:
            ValueError: If technique with same name already exists and overwrite=False
        """
        if self.has_technique(name) and not overwrite:
            raise ValueError(f"Technique '{name}' already exists. Use overwrite=True to replace it.")
        
        technique = Technique(name, cell=self)
        self.techniques[name] = technique
        return technique
    
    def get_technique(self, name: str) -> Optional[Technique]:
        """Get a technique by name."""
        return self.techniques.get(name)
    
    def get_technique_by_id(self, technique_id: int) -> Optional[Technique]:
        """Get a technique by its metadata ID."""
        for technique in self.techniques.values():
            if technique.metadata.id == technique_id:
                return technique
        return None
    
    def remove_technique(self, name: str) -> bool:
        """Remove a technique. Returns True if found and removed."""
        if name in self.techniques:
            del self.techniques[name]
            return True
        return False
    
    def list_techniques(self) -> List[str]:
        """List all technique names."""
        return list(self.techniques.keys())
    
    def add_auxiliary(self, name: str, overwrite: bool = False) -> Auxiliary:
        """Add auxiliary data to this cell.
        
        Args:
            name: Auxiliary name (e.g., "auxiliary_001_temperature")
            overwrite: If False (default), raises ValueError if auxiliary already exists.
                      If True, overwrites existing auxiliary.
        
        Returns:
            The created Auxiliary
            
        Raises:
            ValueError: If auxiliary with same name already exists and overwrite=False
        """
        if self.has_auxiliary(name) and not overwrite:
            raise ValueError(f"Auxiliary '{name}' already exists. Use overwrite=True to replace it.")
        
        auxiliary = Auxiliary(name, cell=self)
        self.auxiliary[name] = auxiliary
        return auxiliary
    
    def get_auxiliary(self, name: str) -> Optional[Auxiliary]:
        """Get auxiliary data by name."""
        return self.auxiliary.get(name)
    
    def get_auxiliary_by_id(self, auxiliary_id: int) -> Optional[Auxiliary]:
        """Get auxiliary data by its metadata ID."""
        for aux in self.auxiliary.values():
            if aux.metadata.id == auxiliary_id:
                return aux
        return None
    
    def remove_auxiliary(self, name: str) -> bool:
        """Remove auxiliary data. Returns True if found and removed."""
        if name in self.auxiliary:
            del self.auxiliary[name]
            return True
        return False
    
    def list_auxiliary(self) -> List[str]:
        """List all auxiliary data names."""
        return list(self.auxiliary.keys())
    
    def has_technique(self, name: str) -> bool:
        """Check if a technique with the given name exists."""
        return name in self.techniques
    
    def has_auxiliary(self, name: str) -> bool:
        """Check if auxiliary data with the given name exists."""
        return name in self.auxiliary
    
    # -------------------------------------------------------------------------
    # GROUP MANAGEMENT OPERATIONS
    # -------------------------------------------------------------------------
    
    def add_group(self, name: str, id: Optional[int] = None, overwrite: bool = False) -> Group:
        """Add a group to this cell.
        
        Args:
            name: Group name
            id: Optional group ID (auto-generated if not provided)
            overwrite: If False (default), raises ValueError if group already exists.
                      If True, overwrites existing group.
        
        Returns:
            The created Group
        
        Raises:
            ValueError: If group already exists and overwrite=False
        """
        if name in self.groups and not overwrite:
            raise ValueError(f"Group '{name}' already exists. Use overwrite=True to replace it.")
        
        # Auto-generate ID if not provided
        if id is None:
            existing_ids = [group.id for group in self.groups.values()]
            id = 1
            while id in existing_ids:
                id += 1
        
        # Check for ID conflicts
        for existing_group in self.groups.values():
            if existing_group.id == id and existing_group.name != name and not overwrite:
                raise ValueError(f"Group ID {id} is already used by group '{existing_group.name}'")
        
        group = Group(id=id, name=name, cell=self)
        self.groups[name] = group
        return group
    
    def get_group(self, name: str) -> Optional[Group]:
        """Get a group by name."""
        return self.groups.get(name)
    
    def get_group_by_id(self, id: int) -> Optional[Group]:
        """Get a group by ID."""
        for group in self.groups.values():
            if group.id == id:
                return group
        return None
    
    def remove_group(self, name: str) -> bool:
        """Remove a group by name. Returns True if found and removed.
        
        Note: This will also remove all techniques/auxiliaries from the group.
        """
        if name in self.groups:
            group = self.groups[name]
            
            # Clear group references from all members when group is removed
            for technique in group.techniques.values():
                technique.metadata.group_id = None
                technique.metadata.group_name = None
            
            for auxiliary in group.auxiliary.values():
                auxiliary.metadata.group_id = None
                auxiliary.metadata.group_name = None
            
            del self.groups[name]
            return True
        return False
    
    def list_groups(self) -> Dict[str, Group]:
        """List all groups as {group_name: Group} mapping."""
        return self.groups.copy()
    
    def has_group(self, name: str) -> bool:
        """Check if a group with the given name exists."""
        return name in self.groups
    
    def has_group_id(self, id: int) -> bool:
        """Check if a group with the given ID exists."""
        return any(group.id == id for group in self.groups.values())
    
    def get_group_name_by_id(self, id: int) -> Optional[str]:
        """Get group name by ID (for backward compatibility)."""
        group = self.get_group_by_id(id)
        return group.name if group else None


# =============================================================================
# MAIN STUDY OBJECT CLASS
# =============================================================================

class StudyObject:
    """Object-oriented representation of an electrochemical study with hierarchical netCDF storage.
    
    This class provides complete abstraction of xarray/netCDF operations and
    mirrors the study structure with:

    - Study-level metadata
    - Cells with metadata
    - Techniques with data
    - Auxiliary data with data
    
    The class handles all xarray complexity internally and provides a clean,
    intuitive API for working with electrochemical study data.
    """
    
    def __init__(self):
        """Initialize empty study object."""

        # study-level metadata
        self.metadata: StudyMetadata = StudyMetadata()

        # study-level groups
        self.cells: Dict[str, Cell] = {}
        # self.future_extensions: Dict[str, FutureExtensionGroup] = {} # Placeholder for future extensions
    
    # -------------------------------------------------------------------------
    # CELL-LEVEL OPERATIONS
    # -------------------------------------------------------------------------
    
    def add_cell(self, name: str, overwrite: bool = False) -> Cell:
        """Add a cell to the study.
        
        Args:
            name: Cell name (e.g., "cell_001")
            overwrite: If False (default), raises ValueError if cell already exists.
                      If True, overwrites existing cell.
        
        Returns:
            The created Cell
            
        Raises:
            ValueError: If cell with same name already exists and overwrite=False
        """
        if self.has_cell(name) and not overwrite:
            raise ValueError(f"Cell '{name}' already exists. Use overwrite=True to replace it.")
        
        cell = Cell(name)
        self.cells[name] = cell
        return cell

    def get_cell(self, name: str) -> Optional[Cell]:
        """Get a cell by name."""
        return self.cells.get(name)

    def get_cell_by_id(self, cell_id: str) -> Optional[Cell]:
        """Get a cell by its metadata ID."""
        for cell in self.cells.values():
            if cell.metadata.id == cell_id:
                return cell
        return None
    
    def remove_cell(self, name: str) -> bool:
        """Remove a cell. Returns True if found and removed."""
        if name in self.cells:
            del self.cells[name]
            return True
        return False
    
    def list_cells(self) -> List[str]:
        """List all cell names."""
        return list(self.cells.keys())
    
    def has_cell(self, name: str) -> bool:
        """Check if a cell with the given name exists."""
        return name in self.cells
    
    # -------------------------------------------------------------------------
    # FILE I/O OPERATIONS
    # -------------------------------------------------------------------------
    
    def to_xarray_dataset(self) -> xr.Dataset:
        """Convert study object to xarray Dataset.
        
        This flattens the hierarchical structure into a single dataset
        with appropriate variable naming and metadata organization.
        """
        # Start with empty dataset
        data_vars = {}
        attrs = {}
        
        # Add study metadata as global attributes
        attrs.update(self.metadata.to_netcdf_attrs())
        
        # Process each cell
        for cell_name, cell in self.cells.items():
            # Add cell metadata to global attributes with prefix
            cell_attrs = cell.metadata.to_netcdf_attrs()
            for attr_name, attr_value in cell_attrs.items():
                attrs[f"{cell_name}_{attr_name}"] = attr_value
            
            # Process techniques
            for technique_name, technique in cell.techniques.items():
                # Add technique metadata to global attributes
                tech_attrs = technique.metadata.to_netcdf_attrs()
                tech_prefix = f"{cell_name}_{technique_name}"
                for attr_name, attr_value in tech_attrs.items():
                    attrs[f"{tech_prefix}_{attr_name}"] = attr_value
                
                # Add technique data variables
                for var_name, var in technique.data.variables.items():
                    full_var_name = f"{tech_prefix}_{var_name}"
                    data_vars[full_var_name] = var.to_xarray_variable()
            
            # Process auxiliary data
            for aux_name, aux in cell.auxiliary.items():
                # Add auxiliary metadata to global attributes
                aux_attrs = aux.metadata.to_netcdf_attrs()
                aux_prefix = f"{cell_name}_{aux_name}"
                for attr_name, attr_value in aux_attrs.items():
                    attrs[f"{aux_prefix}_{attr_name}"] = attr_value
                
                # Add auxiliary data variables
                for var_name, var in aux.data.variables.items():
                    full_var_name = f"{aux_prefix}_{var_name}"
                    data_vars[full_var_name] = var.to_xarray_variable()
        
        return xr.Dataset(data_vars=data_vars, attrs=attrs)
    
    def save(self, filename: Union[str, Path], engine: str = "h5netcdf") -> None:
        """Save study object to netCDF file.
        
        Args:
            filename: Output filename
            engine: NetCDF engine to use ("h5netcdf" or "netcdf4")
        """
        ds = self.to_xarray_dataset()
        ds.to_netcdf(filename, engine=engine)
    
    @classmethod
    def load(cls, filename: Union[str, Path]) -> StudyObject:
        """Load study object from netCDF file.
        
        Args:
            filename: Input filename
            
        Returns:
            StudyObject instance loaded from file
        """
        ds = xr.open_dataset(filename)
        
        study_obj = cls()
        
        # Extract study metadata from global attributes and update the automatically created instance
        try:
            if "metadata_json" in ds.attrs:
                study_data = json.loads(ds.attrs["metadata_json"])
                # Update the automatically created StudyMetadata instance
                study_obj.metadata.id = study_data["metadata"]["id"]
                study_obj.metadata.description = study_data["metadata"]["description"]
                study_obj.metadata.format_version = study_data["file_metadata"]["format_version"]
                study_obj.metadata.timestamp = datetime.fromisoformat(study_data["file_metadata"]["timestamp"])
            else:
                # Fallback to individual attributes - update the existing instance
                loaded_metadata = StudyMetadata.from_netcdf_attrs(ds.attrs)
                study_obj.metadata.id = loaded_metadata.id
                study_obj.metadata.description = loaded_metadata.description
                study_obj.metadata.format_version = loaded_metadata.format_version
                study_obj.metadata.timestamp = loaded_metadata.timestamp
        except (KeyError, json.JSONDecodeError, ValueError):
            # If metadata extraction fails, set minimal values on existing instance
            study_obj.metadata.id = "unknown"
            study_obj.metadata.description = ""
        
        # Extract cell, technique, and auxiliary data
        # This is complex and would require parsing the flattened attribute names
        # For now, we'll implement a basic version
        
        # TODO: Implement full reconstruction of hierarchical structure
        # This requires parsing attribute names like:
        # - cell_001_cell_id, cell_001_cell_type, etc. for cell metadata
        # - cell_001_technique_001_CV_technique_id, etc. for technique metadata
        # - cell_001_auxiliary_001_temperature_auxiliary_id, etc. for auxiliary metadata
        # And reconstructing data variables with prefixes like:
        # - cell_001_technique_001_CV_time, cell_001_technique_001_CV_potential, etc.
        
        return study_obj
    
    # -------------------------------------------------------------------------
    # UTILITY METHODS
    # -------------------------------------------------------------------------
    
    def validate(self) -> List[str]:
        """Validate study structure and return list of issues."""
        issues = []
        
        if not self.metadata.id:
            issues.append("Study metadata has no ID set")
        
        if not self.cells:
            issues.append("No cells defined")
        
        for cell_name, cell in self.cells.items():
            if not cell.metadata:
                issues.append(f"Cell {cell_name} has no metadata")
            
            if not cell.techniques and not cell.auxiliary:
                issues.append(f"Cell {cell_name} has no techniques or auxiliary data")
            
            # Check for technique ID conflicts
            tech_ids = [tech.metadata.id for tech in cell.techniques.values()]
            if len(tech_ids) != len(set(tech_ids)):
                issues.append(f"Cell {cell_name} has duplicate technique IDs")
            
            # Check for auxiliary ID conflicts
            aux_ids = [aux.metadata.id for aux in cell.auxiliary.values()]
            if len(aux_ids) != len(set(aux_ids)):
                issues.append(f"Cell {cell_name} has duplicate auxiliary IDs")
        
        return issues
    
    def print_structure(self, show_metadata: bool = True, show_data: bool = False) -> None:
        """Print a visual tree structure of the study object to terminal.
        
        Args:
            show_metadata: Whether to show metadata details
            show_data: Whether to show data variable details
        """
        print("📁 StudyObject Structure")
        print("=" * 50)
        
        # Study level
        print(f"🔬 Study: {self.metadata.id}")
        if show_metadata:
            print(f"   📝 Description: {self.metadata.description[:60]}{'...' if len(self.metadata.description) > 60 else ''}")
            print(f"   📅 Created: {self.metadata.timestamp.strftime('%Y-%m-%d %H:%M')}")
            print(f"   👥 Contributors: {len(self.metadata.contributors)}")
            print(f"   💰 Funding: {len(self.metadata.funding)} sources")
        
        # Study subgroups level
        study_subgroups = []
        if self.cells:
            study_subgroups.append(("cells", len(self.cells)))
        # Future subgroups can be added here:
        # if self.future_extensions:
        #     study_subgroups.append(("extensions", len(self.future_extensions)))
        
        if not study_subgroups:
            print("   └── (no subgroups)")
            return
        
        for i, (subgroup_name, count) in enumerate(study_subgroups):
            is_last_subgroup = (i == len(study_subgroups) - 1)
            subgroup_connector = "└──" if is_last_subgroup else "├──"
            subgroup_prefix = "   " if is_last_subgroup else "│  "
            
            print(f"   {subgroup_connector} 📂 {subgroup_name}/ ({count} items)")
            
            # Show cells as sub-items of the cells subgroup
            if subgroup_name == "cells":
                if not self.cells:
                    print(f"   {subgroup_prefix}    └── (no cells)")
                    continue
                
                # Cells level - now properly nested under cells/ subgroup
                cell_names = list(self.cells.keys())
                for j, (cell_name, cell) in enumerate(self.cells.items()):
                    is_last_cell = (j == len(self.cells) - 1)
                    cell_connector = "└──" if is_last_cell else "├──"
                    cell_prefix = f"{subgroup_prefix}    {'   ' if is_last_cell else '│  '}"
                    
                    print(f"   {subgroup_prefix}    {cell_connector} 🔋 {cell_name}")
                    if show_metadata:
                        print(f"   {cell_prefix}    📋 ID: {cell.metadata.id}")
                        print(f"   {cell_prefix}    🏷️  Type: {cell.metadata.type}")
                        print(f"   {cell_prefix}    🧪 Chemistry: {cell.metadata.cathode} | {cell.metadata.electrolyte} | {cell.metadata.anode}")
                        print(f"   {cell_prefix}    ⚙️  Components: {len(cell.metadata.components)}")
                    
                    # Group techniques and auxiliaries by their groups
                    all_items = []
                    for tech_name, tech in cell.techniques.items():
                        all_items.append(("technique", tech_name, tech))
                    for aux_name, aux in cell.auxiliary.items():
                        all_items.append(("auxiliary", aux_name, aux))
                    
                    if not all_items:
                        print(f"   {cell_prefix}    └── (no techniques or auxiliary)")
                        continue
                    
                    # Organize items by groups using the new group management
                    groups = {}
                    ungrouped = []
                    
                    for item_type, item_name, item_obj in all_items:
                        # Get group info from the object's metadata
                        group_id = item_obj.metadata.group_id
                        group_name = item_obj.metadata.group_name
                        
                        if group_id is not None and group_name is not None:
                            # Verify group exists in cell's group registry
                            cell_group = cell.get_group_by_id(group_id)
                            if cell_group is not None:
                                # Use the group from cell registry (authoritative source)
                                group_key = f"{cell_group.name}_{group_id}"
                                
                                if group_key not in groups:
                                    groups[group_key] = {
                                        'name': cell_group.name,
                                        'id': group_id,
                                        'items': []
                                    }
                                groups[group_key]['items'].append((item_type, item_name, item_obj))
                            else:
                                # Group ID not found in registry, treat as ungrouped
                                ungrouped.append((item_type, item_name, item_obj))
                        else:
                            ungrouped.append((item_type, item_name, item_obj))
                    
                    # Display grouped items first
                    group_keys = list(groups.keys())
                    total_groups = len(group_keys)
                    has_ungrouped = len(ungrouped) > 0
                    
                    for g_idx, group_key in enumerate(group_keys):
                        group_data = groups[group_key]
                        is_last_group = (g_idx == total_groups - 1) and not has_ungrouped
                        group_connector = "└──" if is_last_group else "├──"
                        group_prefix = f"{cell_prefix}    {'   ' if is_last_group else '│  '}"
                        
                        # Display group header
                        group_display = f"📁 Group: {group_data['name']}"
                        if group_data['id'] is not None:
                            group_display += f" (ID: {group_data['id']})"
                        group_display += f" ({len(group_data['items'])} items)"
                        
                        print(f"   {cell_prefix}    {group_connector} {group_display}")
                        
                        # Display items within the group
                        for item_idx, (item_type, item_name, item_obj) in enumerate(group_data['items']):
                            is_last_item = (item_idx == len(group_data['items']) - 1)
                            item_connector = "└──" if is_last_item else "├──"
                            # Fixed prefix calculation for metadata indentation under grouped items
                            metadata_prefix = f"{group_prefix}    {'   ' if is_last_item else '│  '}"
                            
                            icon = "📊" if item_type == "technique" else "🔍"
                            print(f"   {group_prefix}    {item_connector} {icon} {item_name}")
                            
                            if show_metadata:
                                print(f"   {metadata_prefix}    📋 ID: {item_obj.metadata.id}")
                                print(f"   {metadata_prefix}    🏷️  Type: {item_obj.metadata.type}")
                                if hasattr(item_obj.metadata, 'start') and item_obj.metadata.start:
                                    duration = ""
                                    if hasattr(item_obj.metadata, 'end') and item_obj.metadata.end:
                                        duration = f" → {item_obj.metadata.end.strftime('%H:%M')}"
                                    print(f"   {metadata_prefix}    📅 Time: {item_obj.metadata.start.strftime('%Y-%m-%d %H:%M')}{duration}")
                                print(f"   {metadata_prefix}    🔧 Devices: {len(item_obj.metadata.devices)}")
                                print(f"   {metadata_prefix}    ⚙️  Settings: {len(item_obj.metadata.settings)}")
                            
                            if show_data and item_obj.data.variables:
                                data_vars = list(item_obj.data.variables.keys())
                                print(f"   {metadata_prefix}    📊 Data vars: {', '.join(data_vars[:3])}{' ...' if len(data_vars) > 3 else ''}")
                    
                    # Display ungrouped items directly under cell
                    if ungrouped:
                        for item_idx, (item_type, item_name, item_obj) in enumerate(ungrouped):
                            # Last ungrouped item is the last item overall (regardless of groups)
                            is_last_item = (item_idx == len(ungrouped) - 1)
                            item_connector = "└──" if is_last_item else "├──"
                            metadata_prefix = f"{cell_prefix}    {'   ' if is_last_item else '│  '}"
                            
                            icon = "📊" if item_type == "technique" else "🔍"
                            print(f"   {cell_prefix}    {item_connector} {icon} {item_name}")
                            
                            if show_metadata:
                                print(f"   {metadata_prefix}    📋 ID: {item_obj.metadata.id}")
                                print(f"   {metadata_prefix}    🏷️  Type: {item_obj.metadata.type}")
                                if hasattr(item_obj.metadata, 'start') and item_obj.metadata.start:
                                    duration = ""
                                    if hasattr(item_obj.metadata, 'end') and item_obj.metadata.end:
                                        duration = f" → {item_obj.metadata.end.strftime('%H:%M')}"
                                    print(f"   {metadata_prefix}    📅 Time: {item_obj.metadata.start.strftime('%Y-%m-%d %H:%M')}{duration}")
                                print(f"   {metadata_prefix}    🔧 Devices: {len(item_obj.metadata.devices)}")
                                print(f"   {metadata_prefix}    ⚙️  Settings: {len(item_obj.metadata.settings)}")
                            
                            if show_data and item_obj.data.variables:
                                data_vars = list(item_obj.data.variables.keys())
                                print(f"   {metadata_prefix}    📊 Data vars: {', '.join(data_vars[:3])}{' ...' if len(data_vars) > 3 else ''}")
    
    def plot_structure(self, filename: Optional[str] = None, format: str = "svg", 
                      show_metadata: bool = False) -> None:
        """Create a clean hierarchical diagram using Mermaid syntax.
        
        Note: Formats "png", "svg", and "pdf" require an internet connection and use 
        the external Mermaid service via mermaid-py library. Use "mmd" format to 
        generate only the Mermaid code file for offline use.
        
        Args:
            filename: Output filename (if None, uses default name)
            format: Output format ("png", "svg", "pdf", "mmd") - SVG recommended for best quality, mmd for offline use
            show_metadata: Whether to include metadata details in nodes
        """
        # Handle mmd format (Mermaid code only) without requiring mermaid-py
        if format.lower() == "mmd":
            if filename is None:
                filename = "file_structure.mmd"
            elif '.' not in filename:
                filename = f"{filename}.mmd"
            
            # Generate and save Mermaid code directly
            mermaid_code = self._generate_mermaid_graph(show_metadata)
            with open(filename, 'w') as f:
                f.write(mermaid_code)
            print(f"✅ Mermaid code saved as: {filename}")
            print("   💡 You can render this manually at: https://mermaid.live/")
            print("   💡 Or use mermaid-cli: npx @mermaid-js/mermaid-cli -i file.mmd -o file.svg")
            return
        
        # For rendering formats, check mermaid-py availability
        try:
            from mermaid import Mermaid
        except ImportError:
            print("⚠️  Cannot create structure plot: mermaid-py not installed")
            print("   → Install with: poetry add mermaid-py")
            print("   → Or use format='mmd' to generate Mermaid code only")
            return
        
        if filename is None:
            filename = f"file_structure.{format}"
        elif '.' not in filename:
            filename = f"{filename}.{format}"
        
        # Generate Mermaid graph syntax
        mermaid_code = self._generate_mermaid_graph(show_metadata)
        
        # Create Mermaid instance and render
        try:
            # Create Mermaid instance with the graph code
            mermaid = Mermaid(mermaid_code)
            
            # Render the diagram based on format
            if format.lower() == "svg":

                mermaid.to_svg(filename)
                
                # Check if file was created successfully (mermaid-py sometimes fails silently)
                if Path(filename).exists() and Path(filename).stat().st_size > 0:
                    print(f"✅ Structure diagram saved as: {filename}")
                else:
                    # SVG generation failed (likely due to service unavailability)
                    print(f"⚠️  SVG generation failed (service may be unavailable)")
                    raise Exception("SVG file empty or not created")
                    
            elif format.lower() == "pdf":
                # PDF not directly supported by mermaid-py, fallback to SVG for better quality
                print("   ℹ️  PDF format not supported by mermaid-py, using SVG instead")
                svg_filename = filename.replace('.pdf', '.svg')
                mermaid.to_svg(svg_filename)
                
                if Path(svg_filename).exists() and Path(svg_filename).stat().st_size > 0:
                    filename = svg_filename
                    print(f"✅ Structure diagram saved as: {filename}")
                else:
                    raise Exception("SVG file empty or not created")
                    
            else:  # Default to PNG
                mermaid.to_png(filename)
                
                if Path(filename).exists() and Path(filename).stat().st_size > 0:
                    print(f"✅ Structure diagram saved as: {filename}")
                else:
                    raise Exception("PNG file empty or not created")
            
        except Exception as e:
            print(f"⚠️  Diagram generation failed: {e}")
            print("   → This is likely due to mermaid-py service being temporarily unavailable")
            print("   → Saving Mermaid code for manual rendering")
            
            # Fallback: Save Mermaid code as text file
            text_filename = filename.replace(f".{format}", ".mmd")
            with open(text_filename, 'w') as f:
                f.write(mermaid_code)
            print(f"✅ Mermaid code saved as: {text_filename}")
            print("   💡 You can render this manually at: https://mermaid.live/")
            print("   💡 Or use mermaid-cli: npx @mermaid-js/mermaid-cli -i file.mmd -o file.svg")
            print("   💡 Or use format='mmd' directly to skip online rendering")
    
    def _generate_mermaid_graph(self, show_metadata: bool = False) -> str:
        """Generate Mermaid Entity Relationship Diagram with group entities."""
        lines = [
            '%%{',
            '   init: {',
            '     "theme": "forest"',
            '   }',
            '}%%',
            'erDiagram'
        ]
        lines.append("")
        
        # Define Study entity
        lines.append('    "Study" {')
        lines.append(f'        string id "{self.metadata.id}"')
        if show_metadata:
            lines.append(f'        int contributors "{len(self.metadata.contributors)}"')
            lines.append(f'        int funding "{len(self.metadata.funding)}"')
            lines.append(f'        datetime timestamp "{self.metadata.timestamp.strftime("%Y-%m-%d %H:%M")}"')
        lines.append("    }")
        lines.append("")
        
        if not self.cells:
            lines.append('    "Empty Study" {')
            lines.append('        string message "no_cells_defined"')
            lines.append("    }")
            lines.append('    "Study" ||--|| "Empty Study" : contains')
        else:
            # Add each cell as entity
            for i, (cell_name, cell) in enumerate(self.cells.items()):
                cell_entity = f'"{cell_name}"'
                
                lines.append(f"    {cell_entity} {{")
                lines.append(f'        string name "{cell_name}"')
                if show_metadata:
                    lines.append(f'        string id "{cell.metadata.id}"')
                    lines.append(f'        string type "{cell.metadata.type}"')
                    lines.append(f'        int components "{len(cell.metadata.components)}"')
                lines.append("    }")
                lines.append("")
                
                # Connect study to cell
                lines.append(f'    "Study" ||--o{{ {cell_entity} : contains')
                lines.append("")
                
                # Organize items by groups
                all_items = []
                for tech_name, tech in cell.techniques.items():
                    all_items.append(("technique", tech_name, tech))
                for aux_name, aux in cell.auxiliary.items():
                    all_items.append(("auxiliary", aux_name, aux))
                
                # Group items using the new group management
                groups = {}
                ungrouped = []
                
                for item_type, item_name, item_obj in all_items:
                    # Get group info from the object's metadata
                    group_id = item_obj.metadata.group_id
                    group_name = item_obj.metadata.group_name
                    
                    if group_id is not None and group_name is not None:
                        # Verify group exists in cell's group registry
                        cell_group = cell.get_group_by_id(group_id)
                        if cell_group is not None:
                            # Use the group from cell registry (authoritative source)
                            group_key = f"{cell_group.name}_{group_id}"
                            
                            if group_key not in groups:
                                groups[group_key] = {
                                    'name': cell_group.name,
                                    'id': group_id,
                                    'items': []
                                }
                            groups[group_key]['items'].append((item_type, item_name, item_obj))
                        else:
                            # Group ID not found in registry, treat as ungrouped
                            ungrouped.append((item_type, item_name, item_obj))
                    else:
                        ungrouped.append((item_type, item_name, item_obj))
                
                # Add group entities
                group_counter = 0
                for group_key, group_data in groups.items():
                    group_counter += 1
                    # Make group entity name unique by including cell name
                    group_entity = f'"{cell_name}_{group_data["name"]}"'
                    
                    lines.append(f"    {group_entity} {{")
                    lines.append(f'        string name "{group_data["name"]}"')
                    if show_metadata:
                        if group_data['id'] is not None:
                            lines.append(f'        int group_id "{group_data["id"]}"')
                        lines.append(f'        int items "{len(group_data["items"])}"')
                    lines.append("    }")
                    lines.append("")
                    
                    # Connect cell to group
                    lines.append(f"    {cell_entity} ||--o{{ {group_entity} : performed")
                    lines.append("")
                    
                    # Add items within the group
                    item_counter = 0
                    for item_type, item_name, item_obj in group_data['items']:
                        item_counter += 1
                        # Make item entity name unique by including cell name
                        item_entity = f'"{cell_name}_{item_name}"'
                        
                        lines.append(f"    {item_entity} {{")
                        lines.append(f'        string name "{item_name.split("_")[-1]}"')
                        if show_metadata:
                            lines.append(f'        int id "{item_obj.metadata.id}"')
                            lines.append(f'        string type "{item_obj.metadata.type}"')
                            lines.append(f'        datetime start "{item_obj.metadata.start.strftime("%Y-%m-%d %H:%M:%S") if item_obj.metadata.start else "N/A"}"')
                            lines.append(f'        datetime end "{item_obj.metadata.end.strftime("%Y-%m-%d %H:%M:%S") if item_obj.metadata.end else "N/A"}"')
                            lines.append(f'        int devices "{len(item_obj.metadata.devices)}"')
                            lines.append(f'        int settings "{len(item_obj.metadata.settings)}"')

                        lines.append("    }")
                        lines.append("")
                        
                        # Connect group to item
                        lines.append(f"    {group_entity} ||--|| {item_entity} : includes")
                        lines.append("")
                
                # Add ungrouped items directly to cell
                ungrouped_counter = 0
                for item_type, item_name, item_obj in ungrouped:
                    ungrouped_counter += 1
                    # Make item entity name unique by including cell name
                    item_entity = f'"{cell_name}_{item_name}"'
                    
                    lines.append(f"    {item_entity} {{")
                    lines.append(f'        string name "{item_name.split("_")[-1]}"')
                    if show_metadata:
                        lines.append(f'        int id "{item_obj.metadata.id}"')
                        lines.append(f'        string type "{item_obj.metadata.type}"')
                        lines.append(f'        datetime start "{item_obj.metadata.start.strftime("%Y-%m-%d %H:%M:%S") if item_obj.metadata.start else "N/A"}"')
                        lines.append(f'        datetime end "{item_obj.metadata.end.strftime("%Y-%m-%d %H:%M:%S") if item_obj.metadata.end else "N/A"}"')
                        lines.append(f'        int devices "{len(item_obj.metadata.devices)}"')
                        lines.append(f'        int settings "{len(item_obj.metadata.settings)}"')
                    lines.append("    }")
                    lines.append("")
                    
                    # Connect cell directly to ungrouped item
                    lines.append(f"    {cell_entity} ||--|| {item_entity} : performed")
                    lines.append("")
        
        return "\n".join(lines)
    

