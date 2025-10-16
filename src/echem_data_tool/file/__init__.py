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
File handling module for electrochemical netCDF data.

This module provides object-oriented classes for working with hierarchical
netCDF files containing electrochemical data and metadata.

Main components:
- StudyObject: Complete study abstraction with data and metadata
- Metadata classes: StudyMetadata, CellMetadata, TechniqueMetadata, AuxiliaryMetadata

Example:
    ```python
    from echem_data_tool.file import StudyObject
    
    # Create new study
    study_obj = StudyObject()
    
    # Set study metadata
    study_obj.metadata.id = "test_study"
    study_obj.metadata.description = "Example electrochemical study"
    
    # Add cell with metadata
    cell = study_obj.add_cell("cell_001")
    cell.metadata.id = "Cell-001"
    cell.metadata.type = "coin"
    cell.metadata.cathode = "LFP"
    cell.metadata.anode = "Li"
    cell.metadata.electrolyte = "LiPF6"
    
    # Add technique to cell
    cv_technique = cell.add_technique("technique_001_CV")
    cv_technique.metadata.type = "Cyclic Voltammetry"
    cv_technique.data.add_variable("time", [0, 1, 2], {"units": "s"})
    cv_technique.data.add_variable("potential", [0.1, 0.2, 0.3], {"units": "V"})
    
    # Save to file
    study_obj.save("experiment.nc")
    ```
"""

from .file import (
    StudyObject,
    Cell,
    Technique,
    Auxiliary,
    Group
)

from .data import (
    DataGroup,
    DataVariable
)

from .metadata import (
    StudyMetadata,
    CellMetadata,
    TechniqueMetadata,
    AuxiliaryMetadata,
    GroupMetadata,
    Contributor,
    Funding,
    SoftwareObject,
    Device,
    Parameter,
    AmountObject,
    Material,
    CellComponent,
    ChemistryObject,
    AssemblyObject,
    AdditionalNote,
    BaseMetadata
)

__all__ = [
    # Study structure classes
    "StudyObject",
    "Cell",
    "Technique", 
    "Auxiliary",
    "Group",
    "DataGroup",
    "DataVariable",
    
    # Metadata classes
    "StudyMetadata",
    "CellMetadata", 
    "TechniqueMetadata",
    "AuxiliaryMetadata",
    "GroupMetadata",
    
    # Helper classes
    "Contributor",
    "Funding",
    "SoftwareObject",
    "Device", 
    "Parameter",
    "AmountObject",
    "Material",
    "CellComponent",
    "ChemistryObject",
    "AssemblyObject", 
    "AdditionalNote",
    "BaseMetadata"
]