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
Metadata handling module for electrochemical netCDF files.

This module provides classes for handling metadata in the
hierarchical netCDF files defined in the file format specification 
found in `design-docs/file_format_specs.md`.

The module abstracts xarray/netCDF complexity and provides a clean interface
for managing metadata across the hierarchical structure:

- Study-level metadata (root/global attributes)
- Cell-level metadata (cell group attributes) 
- Group-level metadata (organizational units for techniques/auxiliaries)
- Technique-level metadata (technique group attributes)  
- Auxiliary data metadata (auxiliary group attributes)

All metadata classes follow the Battery Data Genome (BDG) tier-based
organization with primary, secondary, and tertiary metadata levels.

Minimal example:
    ```python
    from echem_data_tool.file import StudyObject
    
    # Create study object (includes StudyMetadata automatically)
    study_obj = StudyObject()
    study_obj.metadata.id = "20250928_test_experiment"
    study_obj.metadata.description = "Example electrochemical study"
    study_obj.metadata.add_contributor("Jane Doe", "jane@example.edu", "Example Uni")
    
    # Add cell with metadata
    cell = study_obj.add_cell("cell_001")
    cell.metadata.id = "Cell-001"
    cell.metadata.type = "Three-electrode cell"
    cell.metadata.cathode = "Ferrocene"
    cell.metadata.anode = "Zn"
    cell.metadata.electrolyte = "ZnSO4 (aq)"
    
    # Add technique with metadata
    cv_tech = cell.add_technique("technique_001_CV")
    cv_tech.metadata.type = "Cyclic Voltammetry"
    cv_tech.metadata.add_setting("scan_rate", 0.1, "V/s")
    ```
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import xarray as xr


@dataclass
class Contributor:
    """Represents a contributor to the study.
    
    Attributes:
        name: Full name of the contributor
        email: Email address
        affiliation: Institution/organization
        additional_info: List of additional information as name-value pairs
    """
    name: str
    email: str
    affiliation: str
    additional_info: List[Dict[str, str]] = field(default_factory=list)
    
    def add_additional_info(self, name: str, value: str) -> None:
        """Add additional information (e.g., ORCID, contribution type)."""
        self.additional_info.append({"name": name, "value": value})
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "email": self.email,
            "affiliation": self.affiliation,
            "additional_info": self.additional_info
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Contributor:
        """Create Contributor from dictionary representation."""
        return cls(
            name=data["name"],
            email=data["email"],
            affiliation=data["affiliation"],
            additional_info=data.get("additional_info", [])
        )


@dataclass
class Funding:
    """Represents funding information.
    
    Attributes:
        agency: Funding agency name
        country: Country code or name
        grant_number: Grant/project number
    """
    agency: str
    country: str
    grant_number: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "agency": self.agency,
            "country": self.country,
            "grant_number": self.grant_number
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Funding:
        """Create Funding from dictionary representation."""
        return cls(
            agency=data["agency"],
            country=data["country"],
            grant_number=data["grant_number"]
        )


@dataclass
class SoftwareObject:
    """Represents software information.
    
    Attributes:
        name: Software name
        version: Software version
    """
    name: str
    version: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "version": self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SoftwareObject:
        """Create SoftwareObject from dictionary representation."""
        return cls(
            name=data["name"],
            version=data["version"]
        )


@dataclass
class Device:
    """Represents a device/instrument used in measurements.
    
    Attributes:
        name: Device name/identifier
        type: Type of device (potentiostat, sensor, etc.)
        manufacturer: Manufacturer name
        model: Model number/name
        software: Software object (optional)
    """
    name: str
    type: str
    manufacturer: str
    model: str
    software: Optional[SoftwareObject] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "name": self.name,
            "type": self.type,
            "manufacturer": self.manufacturer,
            "model": self.model
        }
        if self.software:
            result["software"] = self.software.to_dict()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Device:
        """Create Device from dictionary representation."""
        software = None
        if "software" in data:
            software = SoftwareObject.from_dict(data["software"])
        
        return cls(
            name=data["name"],
            type=data["type"],
            manufacturer=data["manufacturer"],
            model=data["model"],
            software=software
        )


@dataclass
class Parameter:
    """Represents a measurement parameter or property.
    
    Attributes:
        name: Parameter name
        value: Parameter value (can be numeric, string, or list)
        unit: Unit of measurement (optional)
    """
    name: str
    value: Union[str, int, float, List[Any]]
    unit: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "name": self.name,
            "value": self.value
        }
        if self.unit is not None:
            result["unit"] = self.unit
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Parameter:
        """Create Parameter from dictionary representation."""
        return cls(
            name=data["name"],
            value=data["value"],
            unit=data.get("unit")
        )


@dataclass
class AmountObject:
    """Represents an amount with value and unit.
    
    Attributes:
        value: Amount value
        unit: Unit of measurement
    """
    value: Union[int, float]
    unit: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "value": self.value,
            "unit": self.unit
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AmountObject:
        """Create AmountObject from dictionary representation."""
        return cls(
            value=data["value"],
            unit=data["unit"]
        )


@dataclass
class Material:
    """Represents a material component.
    
    Attributes:
        name: Material name
        type: Material type (active_material, binder, etc.)
        amount: Amount object with value and unit
        id: Optional material ID for tracking
    """
    name: str
    type: str
    amount: AmountObject
    id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "name": self.name,
            "type": self.type,
            "amount": self.amount.to_dict()
        }
        if self.id:
            result["id"] = self.id
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Material:
        """Create Material from dictionary representation."""
        return cls(
            name=data["name"],
            type=data["type"],
            amount=AmountObject.from_dict(data["amount"]),
            id=data.get("id")
        )


@dataclass
class CellComponent:
    """Represents a cell component (electrode, separator, etc.).
    
    Attributes:
        name: Component name
        materials: List of materials in the component
        procedures: List of manufacturing/preparation procedures
        properties: List of physical/chemical properties
    """
    name: str
    materials: List[Material] = field(default_factory=list)
    procedures: List[Parameter] = field(default_factory=list)
    properties: List[Parameter] = field(default_factory=list)
    
    def add_material(self, name: str, type: str, amount_value: Union[int, float], amount_unit: str, id: Optional[str] = None) -> Material:
        """Add a material to this component."""
        amount = AmountObject(value=amount_value, unit=amount_unit)
        material = Material(name=name, type=type, amount=amount, id=id)
        self.materials.append(material)
        return material
    
    def add_procedure(self, name: str, value: Union[str, int, float, List[Any]], 
                     unit: Optional[str] = None) -> Parameter:
        """Add a procedure parameter."""
        procedure = Parameter(name=name, value=value, unit=unit)
        self.procedures.append(procedure)
        return procedure
    
    def add_property(self, name: str, value: Union[str, int, float, List[Any]], 
                    unit: Optional[str] = None) -> Parameter:
        """Add a property parameter."""
        property_param = Parameter(name=name, value=value, unit=unit)
        self.properties.append(property_param)
        return property_param
    
    def find_material(self, name: str) -> Optional[Material]:
        """Find a material by name."""
        for material in self.materials:
            if material.name == name:
                return material
        return None
    
    def find_procedure(self, name: str) -> Optional[Parameter]:
        """Find a procedure by name."""
        for procedure in self.procedures:
            if procedure.name == name:
                return procedure
        return None
    
    def find_property(self, name: str) -> Optional[Parameter]:
        """Find a property by name."""
        for property_param in self.properties:
            if property_param.name == name:
                return property_param
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "materials": [mat.to_dict() for mat in self.materials],
            "procedures": [proc.to_dict() for proc in self.procedures],
            "properties": [prop.to_dict() for prop in self.properties]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CellComponent:
        """Create CellComponent from dictionary representation."""
        component = cls(name=data["name"])
        
        # Reconstruct materials
        for mat_data in data.get("materials", []):
            component.materials.append(Material.from_dict(mat_data))
        
        # Reconstruct procedures
        for proc_data in data.get("procedures", []):
            component.procedures.append(Parameter.from_dict(proc_data))
        
        # Reconstruct properties
        for prop_data in data.get("properties", []):
            component.properties.append(Parameter.from_dict(prop_data))
        
        return component


@dataclass
class ChemistryObject:
    """Represents chemistry notation.
    
    Attributes:
        cathode: Cathode description
        anode: Anode description
        electrolyte: Electrolyte type description
    """
    cathode: str
    anode: str
    electrolyte: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "cathode": self.cathode,
            "anode": self.anode,
            "electrolyte": self.electrolyte
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ChemistryObject:
        """Create ChemistryObject from dictionary representation."""
        return cls(
            cathode=data["cathode"],
            anode=data["anode"],
            electrolyte=data["electrolyte"]
        )


@dataclass
class AssemblyObject:
    """Represents assembly information.
    
    Attributes:
        timestamp: Assembly timestamp (optional)
        manufacturer: Assembly manufacturer/provider/institution
        environment: Assembly environment description
    """
    timestamp: Optional[datetime] = None
    manufacturer: str = ""
    environment: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "manufacturer": self.manufacturer,
            "environment": self.environment
        }
        if self.timestamp:
            result["timestamp"] = self.timestamp.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AssemblyObject:
        """Create AssemblyObject from dictionary representation."""
        timestamp = None
        if "timestamp" in data:
            timestamp = datetime.fromisoformat(data["timestamp"])
        
        return cls(
            timestamp=timestamp,
            manufacturer=data.get("manufacturer", ""),
            environment=data.get("environment", "")
        )





@dataclass
class AdditionalNote:
    """Represents an additional note with name and value.
    
    Attributes:
        name: Short name for identification
        value: Note value content
    """
    name: str
    value: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "value": self.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AdditionalNote:
        """Create AdditionalNote from dictionary representation."""
        return cls(
            name=data["name"],
            value=data["value"]
        )


class BaseMetadata(ABC):
    """Abstract base class for all metadata types.
    
    Provides common functionality for handling BDG tier-based metadata
    organization and conversion to/from netCDF attributes.
    """
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary representation."""
        pass
    
    @abstractmethod
    def to_json(self) -> str:
        """Convert metadata to JSON string."""
        pass
    
    @abstractmethod
    def to_netcdf_attrs(self) -> Dict[str, Any]:
        """Convert to netCDF-compatible attributes.
        
        NetCDF attributes have limitations (no nested objects),
        so complex structures are serialized as JSON strings.
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_netcdf_attrs(cls, attrs: Dict[str, Any]) -> BaseMetadata:
        """Create metadata object from netCDF attributes."""
        pass


class StudyMetadata(BaseMetadata):
    """Study-level metadata for the root group.
    
    Contains file format metadata and essential study-wide parameters
    following BDG tier-based organization.
    
    Attributes:
        format_version: File format version
        timestamp: Creation timestamp of netCDF file
        id: Study identifier
        description: Study description
        contributors: List of contributors
        funding: List of funding sources
    """
    
    def __init__(self, id: str = "", description: str = "", 
                 format_version: str = "1.0.0",
                 timestamp: Optional[datetime] = None):
        self.format_version = format_version
        self.timestamp = timestamp or datetime.now()
        self.id = id
        self.description = description
        self.contributors: List[Contributor] = []
        self.funding: List[Funding] = []
    
    def add_contributor(self, name: str, email: str, affiliation: str, 
                       additional_info: Optional[List[tuple]] = None) -> Contributor:
        """Add a contributor to the study.
        
        Args:
            name: Full name of the contributor
            email: Email address
            affiliation: Institution/organization
            additional_info: Optional list of additional info tuples: (name, value)
                           e.g., [("orcid", "0000-0000-0000-0000"), ("role", "Principal Investigator")]
            
        Returns:
            The created Contributor object
        """
        contributor = Contributor(name=name, email=email, affiliation=affiliation)
        
        if additional_info:
            for info_data in additional_info:
                if len(info_data) >= 2:
                    contributor.add_additional_info(info_data[0], str(info_data[1]))
        
        self.contributors.append(contributor)
        return contributor
    
    def add_funding(self, agency: str, country: str, grant_number: str) -> Funding:
        """Add funding information."""
        funding = Funding(agency=agency, country=country, grant_number=grant_number)
        self.funding.append(funding)
        return funding
    
    def find_contributor(self, name: str) -> Optional[Contributor]:
        """Find a contributor by name."""
        for contributor in self.contributors:
            if contributor.name == name:
                return contributor
        return None
    
    def find_funding(self, agency: str) -> Optional[Funding]:
        """Find funding by agency name."""
        for funding in self.funding:
            if funding.agency == agency:
                return funding
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "file_metadata": {
                "format_version": self.format_version,
                "timestamp": self.timestamp.isoformat()
            },
            "metadata": {
                "id": self.id,
                "description": self.description,
                "contributors": [contrib.to_dict() for contrib in self.contributors],
                "funding": [fund.to_dict() for fund in self.funding]
            }
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def to_netcdf_attrs(self) -> Dict[str, Any]:
        """Convert to netCDF-compatible attributes."""
        # Store complex structures as JSON strings for netCDF compatibility
        return {
            "format_version": self.format_version,
            "timestamp": self.timestamp.isoformat(),
            "study_id": self.id,
            "study_description": self.description,
            "metadata_json": json.dumps(self.to_dict())
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StudyMetadata:
        """Create StudyMetadata from dictionary representation."""
        file_metadata = data.get("file_metadata", {})
        metadata = data.get("metadata", {})
        
        study = cls(
            id=metadata.get("id", ""),
            description=metadata.get("description", ""),
            format_version=file_metadata.get("format_version", "1.0.0"),
            timestamp=datetime.fromisoformat(file_metadata["timestamp"]) if "timestamp" in file_metadata else datetime.now()
        )
        
        # Reconstruct contributors
        for contrib_data in metadata.get("contributors", []):
            study.contributors.append(Contributor.from_dict(contrib_data))
        
        # Reconstruct funding
        for fund_data in metadata.get("funding", []):
            study.funding.append(Funding.from_dict(fund_data))
        
        return study
    
    @classmethod
    def from_json(cls, json_str: str) -> StudyMetadata:
        """Create StudyMetadata from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def from_netcdf_attrs(cls, attrs: Dict[str, Any]) -> StudyMetadata:
        """Create from netCDF attributes."""
        # Try to load from JSON first, fallback to individual attributes
        if "metadata_json" in attrs:
            data = json.loads(attrs["metadata_json"])
            study = cls(
                id=data["metadata"]["id"],
                description=data["metadata"]["description"],
                format_version=data["file_metadata"]["format_version"],
                timestamp=datetime.fromisoformat(data["file_metadata"]["timestamp"])
            )
            # Reconstruct contributors and funding
            for contrib_data in data["metadata"].get("contributors", []):
                contributor = Contributor(
                    name=contrib_data["name"],
                    email=contrib_data["email"],
                    affiliation=contrib_data["affiliation"],
                    additional_info=contrib_data.get("additional_info", [])
                )
                study.contributors.append(contributor)
            
            for fund_data in data["metadata"].get("funding", []):
                funding = Funding(
                    agency=fund_data["agency"],
                    country=fund_data["country"],
                    grant_number=fund_data["grant_number"]
                )
                study.funding.append(funding)
            
            return study
        else:
            # Fallback to individual attributes
            return cls(
                id=attrs.get("study_id", ""),
                description=attrs.get("study_description", ""),
                format_version=attrs.get("format_version", "1.0.0"),
                timestamp=datetime.fromisoformat(attrs["timestamp"]) if "timestamp" in attrs else datetime.now()
            )


class CellMetadata(BaseMetadata):
    """Cell-level metadata for cell groups.
    
    Contains physical and configuration details for electrochemical cells
    following BDG tier-based organization.
    
    Attributes:
        id: Cell identifier  
        type: Cell type description
        objective: Cell objective description
        chemistry: Chemistry object
        assembly: Assembly object
        nominal_capacity_ah: Nominal capacity in Ah
        components: List of cell components (electrodes, separator, electrolyte, etc.)
        additional_notes: Additional notes
    """
    
    def __init__(self, id: str = "", type: str = "", 
                 cathode: str = "", anode: str = "", electrolyte: str = "",
                 objective: str = "",
                 nominal_capacity_ah: Optional[float] = None,
                 assembly_timestamp: Optional[datetime] = None,
                 assembly_manufacturer: str = "",
                 assembly_environment: str = ""):
        self.id = id
        self.type = type
        self.objective = objective
        self.chemistry = ChemistryObject(cathode=cathode, anode=anode, electrolyte=electrolyte)
        self.assembly = AssemblyObject(timestamp=assembly_timestamp, manufacturer=assembly_manufacturer, environment=assembly_environment)
        self.nominal_capacity_ah = nominal_capacity_ah
        self.components: List[CellComponent] = []
        self.additional_notes: List[AdditionalNote] = []
    
    @property
    def cathode(self) -> str:
        """Get the cathode material."""
        return self.chemistry.cathode
    
    @cathode.setter
    def cathode(self, value: str):
        """Set the cathode material."""
        self.chemistry.cathode = value
    
    @property
    def anode(self) -> str:
        """Get the anode material."""
        return self.chemistry.anode
    
    @anode.setter
    def anode(self, value: str):
        """Set the anode material."""
        self.chemistry.anode = value
    
    @property
    def electrolyte(self) -> str:
        """Get the electrolyte material."""
        return self.chemistry.electrolyte
    
    @electrolyte.setter
    def electrolyte(self, value: str):
        """Set the electrolyte material."""
        self.chemistry.electrolyte = value
    
    @property
    def assembly_timestamp(self) -> Optional[datetime]:
        """Get the assembly timestamp."""
        return self.assembly.timestamp
    
    @assembly_timestamp.setter
    def assembly_timestamp(self, value: Optional[datetime]):
        """Set the assembly timestamp."""
        self.assembly.timestamp = value
    
    @property
    def assembly_manufacturer(self) -> str:
        """Get the assembly manufacturer."""
        return self.assembly.manufacturer
    
    @assembly_manufacturer.setter
    def assembly_manufacturer(self, value: str):
        """Set the assembly manufacturer."""
        self.assembly.manufacturer = value
    
    @property
    def assembly_environment(self) -> str:
        """Get the assembly environment."""
        return self.assembly.environment
    
    @assembly_environment.setter
    def assembly_environment(self, value: str):
        """Set the assembly environment."""
        self.assembly.environment = value
    
    def add_component(self, name: str, materials: Optional[List[tuple]] = None,
                     procedures: Optional[List[tuple]] = None,
                     properties: Optional[List[tuple]] = None) -> CellComponent:
        """Add a cell component (electrode, separator, electrolyte, etc.).
        
        Args:
            name: Component name (e.g., "cathode", "anode", "electrolyte")
            materials: Optional list of material tuples: (name, type, amount_value, amount_unit)
                      e.g., [("LiFePO4", "active_material", 85.0, "wt%"), ("Carbon", "additive", 10.0, "wt%")]
            procedures: Optional list of procedure tuples: (name, value, unit)
                       e.g., [("drying_temperature", 80, "°C"), ("coating_method", "doctor blade", None)]
            properties: Optional list of property tuples: (name, value, unit)
                       e.g., [("diameter", 0.6, "cm"), ("mass", 0.00100, "g")]
                      
        Returns:
            The created CellComponent object
        """
        component = CellComponent(name=name)
        
        if materials:
            for material_data in materials:
                if len(material_data) >= 4:
                    id_param = material_data[4] if len(material_data) >= 5 else None
                    component.add_material(material_data[0], material_data[1], material_data[2], material_data[3], id_param)
        
        if procedures:
            for procedure_data in procedures:
                if len(procedure_data) >= 2:
                    name_param, value_param = procedure_data[0], procedure_data[1]
                    unit_param = procedure_data[2] if len(procedure_data) >= 3 else None
                    component.add_procedure(name_param, value_param, unit_param)
        
        if properties:
            for property_data in properties:
                if len(property_data) >= 2:
                    name_param, value_param = property_data[0], property_data[1]
                    unit_param = property_data[2] if len(property_data) >= 3 else None
                    component.add_property(name_param, value_param, unit_param)
        
        self.components.append(component)
        return component
    
    def add_note(self, name: str, value: str) -> AdditionalNote:
        """Add an additional note."""
        note = AdditionalNote(name=name, value=value)
        self.additional_notes.append(note)
        return note
    
    def find_component(self, name: str) -> Optional[CellComponent]:
        """Find a component by name."""
        for component in self.components:
            if component.name == name:
                return component
        return None
    
    def find_note(self, name: str) -> Optional[AdditionalNote]:
        """Find a note by name."""
        for note in self.additional_notes:
            if note.name == name:
                return note
        return None
    

    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        primary = {
            "id": self.id,
            "type": self.type,
            "chemistry": self.chemistry.to_dict(),
            "assembly": self.assembly.to_dict()
        }
        
        if self.objective:
            primary["objective"] = self.objective
        if self.nominal_capacity_ah is not None:
            primary["nominal_capacity_ah"] = self.nominal_capacity_ah
        
        secondary = {}
        if self.components:
            secondary["components"] = [comp.to_dict() for comp in self.components]
        
        result = {
            "primary": primary,
        }
        
        if secondary:
            result["secondary"] = secondary
        
        if self.additional_notes:
            result["tertiary"] = {
                "additional_notes": [note.to_dict() for note in self.additional_notes]
            }
        
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def to_netcdf_attrs(self) -> Dict[str, Any]:
        """Convert to netCDF-compatible attributes."""
        return {
            "cell_id": self.id,
            "cell_type": self.type,
            "cell_cathode": self.chemistry.cathode,
            "cell_anode": self.chemistry.anode,
            "cell_electrolyte": self.chemistry.electrolyte,
            "cell_metadata_json": json.dumps(self.to_dict())
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CellMetadata:
        """Create CellMetadata from dictionary representation."""
        primary = data.get("primary", {})
        secondary = data.get("secondary", {})
        tertiary = data.get("tertiary", {})
        
        # Extract chemistry and assembly objects
        chemistry_data = primary.get("chemistry", {})
        assembly_data = primary.get("assembly", {})
        
        cell = cls(
            id=primary.get("id", ""),
            type=primary.get("type", ""),
            cathode=chemistry_data.get("cathode", ""),
            anode=chemistry_data.get("anode", ""),
            electrolyte=chemistry_data.get("electrolyte", ""),
            objective=primary.get("objective", ""),
            nominal_capacity_ah=primary.get("nominal_capacity_ah"),
            assembly_timestamp=datetime.fromisoformat(assembly_data["timestamp"]) if "timestamp" in assembly_data else None,
            assembly_manufacturer=assembly_data.get("manufacturer", ""),
            assembly_environment=assembly_data.get("environment", "")
        )
        
        # Reconstruct components
        for comp_data in secondary.get("components", []):
            cell.components.append(CellComponent.from_dict(comp_data))
        
        # Reconstruct additional notes
        for note_data in tertiary.get("additional_notes", []):
            cell.additional_notes.append(AdditionalNote.from_dict(note_data))
        
        return cell
    
    @classmethod
    def from_json(cls, json_str: str) -> CellMetadata:
        """Create CellMetadata from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def from_netcdf_attrs(cls, attrs: Dict[str, Any]) -> CellMetadata:
        """Create from netCDF attributes."""
        if "cell_metadata_json" in attrs:
            data = json.loads(attrs["cell_metadata_json"])
            primary = data["primary"]
            
            # Extract chemistry and assembly objects
            chemistry_data = primary.get("chemistry", {})
            assembly_data = primary.get("assembly", {})
            
            cell = cls(
                id=primary["id"],
                type=primary["type"],
                cathode=chemistry_data.get("cathode", ""),
                anode=chemistry_data.get("anode", ""),
                electrolyte=chemistry_data.get("electrolyte", ""),
                objective=primary.get("objective", ""),
                nominal_capacity_ah=primary.get("nominal_capacity_ah"),
                assembly_timestamp=datetime.fromisoformat(assembly_data["timestamp"]) if "timestamp" in assembly_data else None,
                assembly_manufacturer=assembly_data.get("manufacturer", ""),
                assembly_environment=assembly_data.get("environment", "")
            )
            
            # Reconstruct components
            secondary = data.get("secondary", {})
            for comp_data in secondary.get("components", []):
                component = CellComponent(name=comp_data["name"])
                # Reconstruct materials, procedures, properties
                for mat_data in comp_data.get("materials", []):
                    component.materials.append(Material.from_dict(mat_data))
                for proc_data in comp_data.get("procedures", []):
                    component.procedures.append(Parameter.from_dict(proc_data))
                for prop_data in comp_data.get("properties", []):
                    component.properties.append(Parameter.from_dict(prop_data))
                cell.components.append(component)
            
            # Reconstruct additional notes
            tertiary = data.get("tertiary", {})
            for note_data in tertiary.get("additional_notes", []):
                cell.additional_notes.append(AdditionalNote.from_dict(note_data))
            
            return cell
        else:
            # Fallback to individual attributes
            return cls(
                id=attrs.get("cell_id", ""),
                type=attrs.get("cell_type", ""),
                cathode=attrs.get("cell_cathode", ""),
                anode=attrs.get("cell_anode", ""),
                electrolyte=attrs.get("cell_electrolyte", "")
            )


class TechniqueMetadata(BaseMetadata):
    """Technique-level metadata for technique groups.
    
    Contains parameters and conditions for electrochemical measurements
    following BDG tier-based organization.
    
    Attributes:
        id: Technique sequence ID
        type: Technique type (CV, OCV, cycling, etc.)
        start: Start timestamp
        end: End timestamp (optional)
        auxiliary: Whether this is auxiliary data (always False for techniques)
        group_id: Group ID
        group_name: Group name
        devices: List of devices used
        settings: List of measurement settings
        additional_notes: Additional notes
    """
    
    def __init__(self, id: int = 0, type: str = "", start: Optional[datetime] = None,
                 end: Optional[datetime] = None):
        self.id = id
        self.type = type
        self.start = start if start is not None else datetime.now()
        self.end = end
        self.auxiliary = False
        self.group_id: Optional[int] = None
        self.group_name: Optional[str] = None
        self.devices: List[Device] = []
        self.settings: List[Parameter] = []
        self.additional_notes: List[AdditionalNote] = []
    
    def add_device(self, name: str, type: str, manufacturer: str, model: str,
                  software_name: Optional[str] = None, software_version: Optional[str] = None) -> Device:
        """Add a device used in this technique."""
        software = None
        if software_name and software_version:
            software = SoftwareObject(name=software_name, version=software_version)
        
        device = Device(
            name=name, type=type, manufacturer=manufacturer, model=model,
            software=software
        )
        self.devices.append(device)
        return device
    
    def add_setting(self, name: str, value: Union[str, int, float, List[Any]], 
                   unit: Optional[str] = None) -> Parameter:
        """Add a measurement setting."""
        setting = Parameter(name=name, value=value, unit=unit)
        self.settings.append(setting)
        return setting
    
    def add_note(self, name: str, value: str) -> AdditionalNote:
        """Add an additional note."""
        note = AdditionalNote(name=name, value=value)
        self.additional_notes.append(note)
        return note
    

    
    def find_device(self, name: str) -> Optional[Device]:
        """Find a device by name."""
        for device in self.devices:
            if device.name == name:
                return device
        return None
    
    def find_setting(self, name: str) -> Optional[Parameter]:
        """Find a setting by name."""
        for setting in self.settings:
            if setting.name == name:
                return setting
        return None
    
    def find_note(self, name: str) -> Optional[AdditionalNote]:
        """Find a note by name."""
        for note in self.additional_notes:
            if note.name == name:
                return note
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        primary = {
            "id": self.id,
            "auxiliary": self.auxiliary,
            "type": self.type,
            "start": self.start.isoformat(),
        }
        
        if self.group_id is not None:
            primary["group_id"] = self.group_id
        if self.group_name is not None:
            primary["group_name"] = self.group_name
        if self.end:
            primary["end"] = self.end.isoformat()
        
        secondary = {}
        if self.devices:
            secondary["devices"] = [device.to_dict() for device in self.devices]
        if self.settings:
            secondary["settings"] = [setting.to_dict() for setting in self.settings]
        
        result = {"primary": primary}
        
        if secondary:
            result["secondary"] = secondary
        
        if self.additional_notes:
            result["tertiary"] = {
                "additional_notes": [note.to_dict() for note in self.additional_notes]
            }
        
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def to_netcdf_attrs(self) -> Dict[str, Any]:
        """Convert to netCDF-compatible attributes."""
        return {
            "technique_id": self.id,
            "technique_type": self.type,
            "technique_start": self.start.isoformat(),
            "technique_auxiliary": self.auxiliary,
            "technique_metadata_json": json.dumps(self.to_dict())
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TechniqueMetadata:
        """Create TechniqueMetadata from dictionary representation."""
        primary = data.get("primary", {})
        secondary = data.get("secondary", {})
        tertiary = data.get("tertiary", {})
        
        technique = cls(
            id=primary.get("id", 0),
            type=primary.get("type", ""),
            start=datetime.fromisoformat(primary["start"]) if "start" in primary else datetime.now(),
            end=datetime.fromisoformat(primary["end"]) if "end" in primary else None,
            auxiliary=primary.get("auxiliary", False) if isinstance(primary.get("auxiliary"), bool) else primary.get("auxiliary", "False").lower() == "true"
        )
        
        # Reconstruct devices
        for device_data in secondary.get("devices", []):
            technique.devices.append(Device.from_dict(device_data))
        
        # Reconstruct settings
        for setting_data in secondary.get("settings", []):
            technique.settings.append(Parameter.from_dict(setting_data))
        
        # Reconstruct additional notes
        for note_data in tertiary.get("additional_notes", []):
            technique.additional_notes.append(AdditionalNote.from_dict(note_data))
        
        return technique
    
    @classmethod
    def from_json(cls, json_str: str) -> TechniqueMetadata:
        """Create TechniqueMetadata from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def from_netcdf_attrs(cls, attrs: Dict[str, Any]) -> TechniqueMetadata:
        """Create from netCDF attributes."""
        if "technique_metadata_json" in attrs:
            data = json.loads(attrs["technique_metadata_json"])
            primary = data["primary"]
            
            technique = cls(
                id=primary["id"],
                type=primary["type"],
                start=datetime.fromisoformat(primary["start"]),
                end=datetime.fromisoformat(primary["end"]) if "end" in primary else None,
                auxiliary=primary.get("auxiliary", False) if isinstance(primary.get("auxiliary"), bool) else primary.get("auxiliary", "False").lower() == "true"
            )
            
            # Reconstruct devices and settings
            secondary = data.get("secondary", {})
            for device_data in secondary.get("devices", []):
                technique.devices.append(Device.from_dict(device_data))
            
            for setting_data in secondary.get("settings", []):
                technique.settings.append(Parameter.from_dict(setting_data))
            
            # Reconstruct additional notes
            tertiary = data.get("tertiary", {})
            for note_data in tertiary.get("additional_notes", []):
                technique.additional_notes.append(AdditionalNote.from_dict(note_data))
            
            return technique
        else:
            # Fallback to individual attributes
            return cls(
                id=attrs.get("technique_id", 0),
                type=attrs.get("technique_type", ""),
                start=datetime.fromisoformat(attrs["technique_start"]) if "technique_start" in attrs else datetime.now(),
                auxiliary=attrs.get("technique_auxiliary", False)
            )


class AuxiliaryMetadata(BaseMetadata):
    """Auxiliary data metadata for auxiliary groups.
    
    Contains information for parallel measurements and monitoring
    following BDG tier-based organization.
    
    Attributes:
        id: Auxiliary sequence ID
        type: Data type (temperature, UV-Vis, etc.)
        start: Start timestamp
        end: End timestamp (optional)  
        auxiliary: Whether this is auxiliary data (always True)
        group_id: Group ID (managed automatically by GroupClass)
        group_name: Group name (managed automatically by GroupClass)
        parent_techniques: List of parent technique IDs
        devices: List of devices used
        settings: List of measurement settings
        additional_notes: Additional notes
    """
    
    def __init__(self, id: int = 0, type: str = "", start: Optional[datetime] = None,
                 end: Optional[datetime] = None,
                 parent_techniques: Optional[List[int]] = None):
        self.id = id
        self.type = type
        self.start = start if start is not None else datetime.now()
        self.end = end
        self.auxiliary = True
        self.group_id: Optional[int] = None
        self.group_name: Optional[str] = None
        self.parent_techniques = parent_techniques or []
        self.devices: List[Device] = []
        self.settings: List[Parameter] = []
        self.additional_notes: List[AdditionalNote] = []
    
    def add_parent_technique(self, technique_id: int) -> None:
        """Add a parent technique ID for synchronization."""
        if technique_id not in self.parent_techniques:
            self.parent_techniques.append(technique_id)
    
    def add_device(self, name: str, type: str, manufacturer: str, model: str,
                  software_name: Optional[str] = None, software_version: Optional[str] = None) -> Device:
        """Add a device used in auxiliary measurement."""
        software = None
        if software_name and software_version:
            software = SoftwareObject(name=software_name, version=software_version)
        
        device = Device(
            name=name, type=type, manufacturer=manufacturer, model=model,
            software=software
        )
        self.devices.append(device)
        return device
    
    def add_setting(self, name: str, value: Union[str, int, float, List[Any]], 
                   unit: Optional[str] = None) -> Parameter:
        """Add a measurement setting."""
        setting = Parameter(name=name, value=value, unit=unit)
        self.settings.append(setting)
        return setting
    
    def add_note(self, name: str, value: str) -> AdditionalNote:
        """Add an additional note."""
        note = AdditionalNote(name=name, value=value)
        self.additional_notes.append(note)
        return note
    

    
    def add_parent_technique(self, technique_id: int) -> None:
        """Add a parent technique ID for synchronization."""
        if technique_id not in self.parent_techniques:
            self.parent_techniques.append(technique_id)
    
    def add_device(self, name: str, type: str, manufacturer: str, model: str,
                  software_name: Optional[str] = None, software_version: Optional[str] = None) -> Device:
        """Add a device used in this auxiliary measurement."""
        software = None
        if software_name and software_version:
            software = SoftwareObject(name=software_name, version=software_version)
        
        device = Device(
            name=name, type=type, manufacturer=manufacturer, model=model,
            software=software
        )
        self.devices.append(device)
        return device
    
    def add_setting(self, name: str, value: Union[str, int, float, List[Any]], 
                   unit: Optional[str] = None) -> Parameter:
        """Add a measurement setting."""
        setting = Parameter(name=name, value=value, unit=unit)
        self.settings.append(setting)
        return setting
    
    def add_note(self, name: str, value: str) -> AdditionalNote:
        """Add an additional note."""
        note = AdditionalNote(name=name, value=value)
        self.additional_notes.append(note)
        return note
    
    def find_device(self, name: str) -> Optional[Device]:
        """Find a device by name."""
        for device in self.devices:
            if device.name == name:
                return device
        return None
    
    def find_setting(self, name: str) -> Optional[Parameter]:
        """Find a setting by name."""
        for setting in self.settings:
            if setting.name == name:
                return setting
        return None
    
    def find_note(self, name: str) -> Optional[AdditionalNote]:
        """Find a note by name."""
        for note in self.additional_notes:
            if note.name == name:
                return note
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        primary = {
            "id": self.id,
            "auxiliary": self.auxiliary,
            "type": self.type,
            "start": self.start.isoformat(),
        }
        
        if self.group_id is not None:
            primary["group_id"] = self.group_id
        if self.group_name is not None:
            primary["group_name"] = self.group_name
        if self.end:
            primary["end"] = self.end.isoformat()
        if self.parent_techniques:
            primary["parent_techniques"] = self.parent_techniques
        
        secondary = {}
        if self.devices:
            secondary["devices"] = [device.to_dict() for device in self.devices]
        if self.settings:
            secondary["settings"] = [setting.to_dict() for setting in self.settings]
        
        result = {"primary": primary}
        
        if secondary:
            result["secondary"] = secondary
        
        if self.additional_notes:
            result["tertiary"] = {
                "additional_notes": [note.to_dict() for note in self.additional_notes]
            }
        
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def to_netcdf_attrs(self) -> Dict[str, Any]:
        """Convert to netCDF-compatible attributes."""
        return {
            "auxiliary_id": self.id,
            "auxiliary_type": self.type,
            "auxiliary_start": self.start.isoformat(),
            "auxiliary_metadata_json": json.dumps(self.to_dict())
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AuxiliaryMetadata:
        """Create AuxiliaryMetadata from dictionary representation."""
        primary = data.get("primary", {})
        secondary = data.get("secondary", {})
        tertiary = data.get("tertiary", {})
        
        auxiliary = cls(
            id=primary.get("id", 0),
            type=primary.get("type", ""),
            start=datetime.fromisoformat(primary["start"]) if "start" in primary else datetime.now(),
            end=datetime.fromisoformat(primary["end"]) if "end" in primary else None,
            parent_techniques=primary.get("parent_techniques", [])
        )
        
        # Reconstruct devices
        for device_data in secondary.get("devices", []):
            auxiliary.devices.append(Device.from_dict(device_data))
        
        # Reconstruct settings
        for setting_data in secondary.get("settings", []):
            auxiliary.settings.append(Parameter.from_dict(setting_data))
        
        # Reconstruct additional notes
        for note_data in tertiary.get("additional_notes", []):
            auxiliary.additional_notes.append(AdditionalNote.from_dict(note_data))
        
        return auxiliary
    
    @classmethod
    def from_json(cls, json_str: str) -> AuxiliaryMetadata:
        """Create AuxiliaryMetadata from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def from_netcdf_attrs(cls, attrs: Dict[str, Any]) -> AuxiliaryMetadata:
        """Create from netCDF attributes."""
        if "auxiliary_metadata_json" in attrs:
            data = json.loads(attrs["auxiliary_metadata_json"])
            primary = data["primary"]
            
            auxiliary = cls(
                id=primary["id"],
                type=primary["type"],
                start=datetime.fromisoformat(primary["start"]),
                end=datetime.fromisoformat(primary["end"]) if "end" in primary else None,
                parent_techniques=primary.get("parent_techniques", [])
            )
            
            # Reconstruct devices and settings
            secondary = data.get("secondary", {})
            for device_data in secondary.get("devices", []):
                auxiliary.devices.append(Device.from_dict(device_data))
            
            for setting_data in secondary.get("settings", []):
                auxiliary.settings.append(Parameter.from_dict(setting_data))
            
            # Reconstruct additional notes
            tertiary = data.get("tertiary", {})
            for note_data in tertiary.get("additional_notes", []):
                auxiliary.additional_notes.append(AdditionalNote.from_dict(note_data))
            
            return auxiliary
        else:
            # Fallback to individual attributes
            return cls(
                id=attrs.get("auxiliary_id", 0),
                type=attrs.get("auxiliary_type", ""),
                start=datetime.fromisoformat(attrs["auxiliary_start"]) if "auxiliary_start" in attrs else datetime.now()
            )


# =============================================================================
# GROUP METADATA CLASS
# =============================================================================

class GroupMetadata:
    """Metadata for technique/auxiliary groups.
    
    Groups are organizational units that contain related techniques and/or 
    auxiliary measurements. They have their own metadata including:
    - Basic identification (id, name, description)
    - Purpose and objectives
    - Custom notes and annotations
    
    Example:
        ```python
        group = GroupMetadata(id=1, name="CV_Analysis")
        group.description = "Cyclic voltammetry experiments at different scan rates"
        group.purpose = "Rate capability analysis"
        group.add_note("temperature", "25°C")
        ```
    """
    
    def __init__(self, id: int, name: str, description: str = ""):
        """Initialize group metadata.
        
        Args:
            id: Unique group ID within the cell
            name: Group name (e.g., "CV_Analysis", "Characterization")
            description: Optional description of the group's purpose
        """
        # Primary metadata
        self.id = id
        self.name = name
        self.description = description
        self.purpose = ""
        self.created_timestamp = datetime.now()
        
        # Additional notes
        self.additional_notes: List[AdditionalNote] = []
    
    def add_note(self, name: str, value: Any) -> AdditionalNote:
        """Add an additional note to this group."""
        note = AdditionalNote(name=name, value=value)
        self.additional_notes.append(note)
        return note
    
    def find_note(self, name: str) -> Optional[AdditionalNote]:
        """Find an additional note by name."""
        for note in self.additional_notes:
            if note.name == name:
                return note
        return None
    
    def remove_note(self, name: str) -> bool:
        """Remove an additional note by name. Returns True if found and removed."""
        for i, note in enumerate(self.additional_notes):
            if note.name == name:
                del self.additional_notes[i]
                return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary following BDG hierarchy."""
        return {
            "primary": {
                "id": self.id,
                "name": self.name,
                "description": self.description,
                "purpose": self.purpose,
                "created_timestamp": self.created_timestamp.isoformat()
            },
            "tertiary": {
                "additional_notes": [note.to_dict() for note in self.additional_notes]
            }
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2, default=str)
    
    def to_netcdf_attrs(self) -> Dict[str, Any]:
        """Convert to netCDF attributes."""
        attrs = {
            "group_metadata_json": self.to_json(),
            "group_id": self.id,
            "group_name": self.name,
            "group_description": self.description,
            "group_purpose": self.purpose,
            "group_created": self.created_timestamp.isoformat()
        }
        
        # Add individual note attributes
        for i, note in enumerate(self.additional_notes):
            attrs[f"group_note_{i}_name"] = note.name
            attrs[f"group_note_{i}_value"] = str(note.value)
        
        return attrs
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GroupMetadata:
        """Create from dictionary."""
        primary = data["primary"]
        group = cls(
            id=primary["id"],
            name=primary["name"],
            description=primary.get("description", "")
        )
        group.purpose = primary.get("purpose", "")
        if "created_timestamp" in primary:
            group.created_timestamp = datetime.fromisoformat(primary["created_timestamp"])
        
        # Reconstruct additional notes
        tertiary = data.get("tertiary", {})
        for note_data in tertiary.get("additional_notes", []):
            group.additional_notes.append(AdditionalNote.from_dict(note_data))
        
        return group
    
    @classmethod
    def from_netcdf_attrs(cls, attrs: Dict[str, Any]) -> GroupMetadata:
        """Create from netCDF attributes."""
        if "group_metadata_json" in attrs:
            data = json.loads(attrs["group_metadata_json"])
            return cls.from_dict(data)
        else:
            # Fallback to individual attributes
            group = cls(
                id=attrs.get("group_id", 0),
                name=attrs.get("group_name", ""),
                description=attrs.get("group_description", "")
            )
            group.purpose = attrs.get("group_purpose", "")
            if "group_created" in attrs:
                group.created_timestamp = datetime.fromisoformat(attrs["group_created"])
            
            return group

