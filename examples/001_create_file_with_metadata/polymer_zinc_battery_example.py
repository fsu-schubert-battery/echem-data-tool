#!/usr/bin/env python3

"""
Comprehensive example: Polymer/Zinc thin-film battery study
Demonstrates complete metadata handling with the new metadata module.

This example shows a realistic electrochemical study with:

- Study metadata with multiple contributors and funding sources
- Detailed cell construction with materials and procedures
- Multiple measurement techniques (CV and charge/discharge)
- Auxiliary temperature monitoring
- Complete metadata serialization and structure demonstration

NOTE: The example content is fictional and currently not fully consistent.
      It is for demonstration purposes only and will be improved in the future.

"""

import sys
import json
from datetime import datetime, timedelta
sys.path.append('src')

from echem_data_tool.study import (
    StudyObject
)

def create_polymer_zinc_study():
    """Create comprehensive metadata for a polymer/zinc thin-film battery study."""
    
    print("🔋 Creating Polymer/Zinc Thin-Film Battery Study")
    print("=" * 60)

    # =================================================================
    # CREATE STUDY OBJECT AND LAYOUT
    # =================================================================
    
    # create a new study object for this study
    my_first_study = StudyObject()

    # ADD CELL 1
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    cell = my_first_study.add_cell("cell_001")
    cv_technique = cell.add_technique("technique_001_CV")
    cv_technique_2 = cell.add_technique("technique_002_CV")
    gcd_technique = cell.add_technique("technique_003_GCD")
    temperature_aux = cell.add_auxiliary("auxiliary_001_temperature")

    # Group the CV techniques
    cv_group = cell.add_group(id=1, name="Cyclic Voltammetry")
    cv_group.add_technique([cv_technique, cv_technique_2])
    
    # ADD CELL 2
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    cell_2 = my_first_study.add_cell("cell_002")
    eis_technique = cell_2.add_technique("technique_001_EIS")
    cv_slow_technique = cell_2.add_technique("technique_002_CV")
    pressure_aux = cell_2.add_auxiliary("auxiliary_001_pressure")

    # NOTE: The layout can also be created on the fly, but the definition 
    #       at the top like done here provides immediate clarity about the
    #       structure.

    # =================================================================
    # 1. STUDY METADATA
    # =================================================================
    
    # Set study metadata directly on the study object
    my_first_study.metadata.id = "PZB_2025_001_ThinFilm_Characterization"
    my_first_study.metadata.description = (
        "Electrochemical characterization of polymer/zinc thin-film batteries "
        "fabricated via solution processing in inert atmosphere. Investigation "
        "of cycling stability and rate capability using cyclic voltammetry "
        "and galvanostatic charge-discharge protocols."
    )
    my_first_study.metadata.format_version = "1.0.0"
    
    # Add research team
    my_first_study.metadata.add_contributor(
        name="Dr. Elena Müller",
        email="elena.mueller@uni-jena.de", 
        affiliation="Friedrich-Schiller-Universität Jena, Institute of Physical Chemistry",
        additional_info=[
            ("orcid", "0000-0002-1234-5678"),
            ("role", "Principal Investigator")
        ]
    )
    
    my_first_study.metadata.add_contributor(
        name="Marcus Weber",
        email="marcus.weber@uni-jena.de",
        affiliation="Friedrich-Schiller-Universität Jena, Graduate School",
        additional_info=[
            ("orcid", "0000-0003-9876-5432"),
            ("role", "PhD Student - Cell Fabrication & Testing")
        ]
    )
    
    my_first_study.metadata.add_contributor(
        name="Dr. Sarah Chen",
        email="sarah.chen@uni-jena.de",
        affiliation="Friedrich-Schiller-Universität Jena, CEEC Jena",
        additional_info=[
            ("orcid", "0000-0001-2468-1357"),
            ("role", "Postdoctoral Researcher - Materials Development")
        ]
    )
    
    # Add funding sources
    my_first_study.metadata.add_funding(
        agency="Deutsche Forschungsgemeinschaft (DFG)",
        country="Germany", 
        grant_number="MU 1234/5-2"
    )
    
    my_first_study.metadata.add_funding(
        agency="Bundesministerium für Bildung und Forschung (BMBF)",
        country="Germany",
        grant_number="03EK3045A - FestBatt"
    )
    
    # Output summary
    print(f"✅ Study '{my_first_study.metadata.id}' created")
    print(f"   - {len(my_first_study.metadata.contributors)} contributors")
    print(f"   - {len(my_first_study.metadata.funding)} funding sources")    
    
    # =================================================================
    # 2. CELL METADATA - Thin-film battery construction
    # =================================================================
    base_timestamp = datetime.now() - timedelta(days=7)
    
    # add cell metadata 
    cell.metadata.id = "PZB-TF-001"
    cell.metadata.type = "Pouch Cell"
    cell.metadata.cathode = "PTAm"
    cell.metadata.anode = "Zn"
    cell.metadata.electrolyte = "aqueous"
    cell.metadata.objective = "Electrochemical characterization of polymer/zinc thin-film battery"
    cell.metadata.nominal_capacity_ah = 0.00015
    cell.metadata.assembly_timestamp = base_timestamp
    cell.metadata.assembly_manufacturer = "Friedrich-Schiller-Universität Jena"
    cell.metadata.assembly_environment = "Argon-filled glove box (H2O < 0.5 ppm, O2 < 0.5 ppm)"

    # ANODE: Zinc thin-film
    # NOTE Alternative 1 to add a component with all information at once
    cell.metadata.add_component(
        name="anode",
        materials=[
            ("Zinc", "active_material", 100.0, "wt%")
        ],
        procedures=[
            ("substrate_cleaning", "acetone/IPA/DI_water_sequence", None),
            ("deposition_method", "RF_sputtering", None),
            ("deposition_temperature", 150.0, "°C"),
            ("annealing_temperature", 300.0, "°C")
        ],
        properties=[
            ("thickness", 2.5, "µm"),
            ("sheet_resistance", 8.2, "Ω/sq"),
            ("surface_roughness_Ra", 45, "nm")
        ]
    )
    
    # CATHODE: PTAm (Poly(TEMPO-amide)) composite
    # NOTE: Alternative 2 to add a component with information step-by-step via methods
    cathode = cell.metadata.add_component(name="cathode")

    # Cathode materials
    cathode.add_material("Poly(TEMPO-amide)", "redox_active_polymer", 60.0, "wt%")
    cathode.add_material("SuperP", "conductive_additive", 35.0, "wt%")
    cathode.add_material("Cellulose", "binder", 5.0, "wt%")
    
    # Cathode fabrication procedures
    cathode.add_procedure("preparation", """
        1. Weigh the required amounts of dry PTAm, SuperP, and Cellulose.
        2. Disperse the materials in water using a Dispermat.
        3. Coat the slurry onto the substrate via doctor blading.
    """, None)
    cathode.add_procedure("mixing_method", "Dispermat", None)
    cathode.add_procedure("mixing_speed", 8000, "rpm")
    cathode.add_procedure("mixing_time", 30, "min")
    cathode.add_procedure("solvent", "isopropanol", None)
    cathode.add_procedure("coating_method", "doctor_blading", None)
    cathode.add_procedure("coating_speed", "1000", "µm/s")
    cathode.add_procedure("coating_thickness", 200, "µm")
    cathode.add_procedure("drying_temperature", 60.0, "°C")
    cathode.add_procedure("annealing_temperature", 100.0, "°C")
    
    # Cathode properties  
    cathode.add_property("mass_loading", 4.1, "mg/cm²")
    cathode.add_property("theoretical_capacity", 111, "mAh/g")
    cathode.add_property("dry_thickness", 20, "µm")
    
    # ELECTROLYTE: Solid polymer electrolyte
    cell.metadata.add_component(
        name="electrolyte", 
        materials=[
            ("Poly(ethylene oxide)", "polymer_host", 60.0, "wt%"),
            ("LiTFSI", "lithium_salt", 25.0, "wt%"),
            ("Zn(CF3SO3)2", "zinc_salt", 15.0, "wt%")
        ],
        procedures=[
            ("dissolution_method", "stirring", None),
            ("dissolution_solvent", "acetonitrile", None),
            ("dissolution_temperature", 60.0, "°C"),
            ("dissolution_time", 12, "h"),
            ("casting_method", "doctor_blade", None),
            ("evaporation_control", "controlled_atmosphere", None)
        ],
        properties=[
            ("ionic_conductivity", 2.1e-4, "S/cm"),
            ("thickness", 25, "µm")
        ]
    )

    # ANODE CURRENT COLLECTOR: Stainless steel foil
    cell.metadata.add_component(
        name="anode_current_collector",
        materials=[
            ("Stainless steel foil", "current_collector", 100.0, "wt%")
        ],
        properties=[
            ("thickness", 20, "µm")
        ]
    )

    # HOUSING/PACKAGING: Pouch cell packaging
    cell.metadata.add_component(
        name="housing",
        materials=[
            ("Aluminum-laminated film", "pouch_material", None, None)
        ],
        procedures=[
            ("sealing_method", "heat_sealing", None),
            ("sealing_temperature", 180.0, "°C"),
            ("pressing_force", 2.0, "MPa")
        ],
        properties=[
            ("barrier_thickness", 115, "µm"),
            ("moisture_barrier", "<0.01", "g/m²/day")
        ]
    )
    
    # Assembly parameters as structured data
    cell.metadata.add_note(
        name="glove_box_model",
        value="MBraun LABmaster dp"
    )
    
    cell.metadata.add_note(
        name="pressing_force",
        value="2 MPa"
    )
    
    cell.metadata.add_note(
        name="conditioning_protocol",
        value="24h at 60°C before electrochemical testing"
    )
    
    print(f"\n✅ Cell '{cell.metadata.id}' created")
    print(f"   - {len(cell.metadata.components)} components (including electrolyte)")
    print(f"   - Assembly: {cell.metadata.assembly.timestamp.strftime('%Y-%m-%d %H:%M') if cell.metadata.assembly.timestamp else 'N/A'}")
    
    # =================================================================
    # 3. TECHNIQUE 1: Cyclic Voltammetry (10 mV/s)
    # =================================================================
    cv_start = base_timestamp + timedelta(seconds=280)
    cv_end = cv_start + timedelta(seconds=28)
    
    # Set technique metadata properties
    cv_technique.metadata.id = 1
    cv_technique.metadata.type = "Cyclic Voltammetry"
    cv_technique.metadata.start = cv_start
    cv_technique.metadata.end = cv_end
    
    # CV equipment
    cv_technique.metadata.add_device(
        name="VMP3_Potentiostat",
        type="potentiostat",
        manufacturer="BioLogic Science Instruments",
        model="VMP3",
        software_name="EC-Lab",
        software_version="11.50"
    )
    
    # CV parameters
    cv_technique.metadata.add_setting("initial_potential", 0.8, "V")
    cv_technique.metadata.add_setting("initial_potential_hold", 30, "s")
    cv_technique.metadata.add_setting("vertex_potential_low", 0.8, "V") 
    cv_technique.metadata.add_setting("vertex_potential_high", 2.2, "V")
    cv_technique.metadata.add_setting("scan_rate", 10, "mV/s")
    cv_technique.metadata.add_setting("cycle_count", 1, None)
    cv_technique.metadata.add_setting("current_range", 10, "mA")
    cv_technique.metadata.add_setting("potential_range", [-2.5, 2.5], "V")
    cv_technique.metadata.add_setting("bandwidth", 7, None)
    
    cv_technique.metadata.add_note(
        name="measurement_purpose", 
        value="Electrochemical stability window determination and redox peak identification"
    )
    
    cv_technique.metadata.add_note(
        name="potentiostat_channel",
        value=1
    )
    
    print(f"\n✅ CV Technique created")
    print(f"   - Duration: {cv_start.strftime('%H:%M')} - {cv_end.strftime('%H:%M')}")
    print(f"   - {len(cv_technique.metadata.devices)} device, {len(cv_technique.metadata.settings)} parameters")
    
    # =================================================================
    # 4. TECHNIQUE 2: Cyclic Voltammetry (100 mV/s)
    # =================================================================
    cv2_start = cv_end
    cv2_end = cv2_start + timedelta(seconds=28)
    
    # Get existing technique (created in minimal example)
    cv_technique_2 = cell.get_technique("technique_002_CV")
    
    # Set technique metadata properties
    cv_technique_2.metadata.id = 2
    cv_technique_2.metadata.type = "Cyclic Voltammetry"
    cv_technique_2.metadata.start = cv2_start
    cv_technique_2.metadata.end = cv2_end
    
    # CV equipment (same potentiostat, different channel)
    cv_technique_2.metadata.add_device(
        name="VMP3_Potentiostat",
        type="potentiostat",
        manufacturer="BioLogic Science Instruments",
        model="VMP3",
        software_name="EC-Lab",
        software_version="11.50"
    )
    
    # CV parameters
    cv_technique_2.metadata.add_setting("initial_potential", 0.8, "V")
    cv_technique_2.metadata.add_setting("initial_potential_hold", 30, "s")
    cv_technique_2.metadata.add_setting("vertex_potential_low", 0.8, "V") 
    cv_technique_2.metadata.add_setting("vertex_potential_high", 2.2, "V")
    cv_technique_2.metadata.add_setting("scan_rate", 100, "mV/s")
    cv_technique_2.metadata.add_setting("cycle_count", 1, None)
    cv_technique_2.metadata.add_setting("current_range", 10, "mA")
    cv_technique_2.metadata.add_setting("potential_range", [-2.5, 2.5], "V")
    cv_technique_2.metadata.add_setting("bandwidth", 7, None)
    
    cv_technique_2.metadata.add_note(
        name="measurement_purpose", 
        value="Higher scan rate CV for kinetic analysis"
    )
    
    cv_technique_2.metadata.add_note(
        name="potentiostat_channel",
        value=1
    )
    
    print(f"\n✅ CV Technique 2 created")
    print(f"   - Duration: {cv2_start.strftime('%H:%M')} - {cv2_end.strftime('%H:%M')}")
    print(f"   - {len(cv_technique_2.metadata.devices)} device, {len(cv_technique_2.metadata.settings)} parameters")
    
    # =================================================================
    # 5. TECHNIQUE 3: Galvanostatic Charge/Discharge
    # =================================================================
    gcd_start = cv2_end + timedelta(hours=0.5)  # Rest period after second CV
    gcd_end = gcd_start + timedelta(hours=8)  # 8-hour cycling test
    
    # Get existing technique (created in minimal example)
    gcd_technique = cell.get_technique("technique_003_GCD")
    
    # Set technique metadata properties
    gcd_technique.metadata.id = 3
    gcd_technique.metadata.type = "Galvanostatic Charge-Discharge Cycling"
    gcd_technique.metadata.start = gcd_start
    gcd_technique.metadata.end = gcd_end
    
    # Same potentiostat, different channel
    gcd_technique.metadata.add_device(
        name="VMP3_Potentiostat", 
        type="potentiostat",
        manufacturer="BioLogic Science Instruments",
        model="VMP3",
        software_name="EC-Lab", 
        software_version="11.50"
    )
    
    # GCD parameters
    gcd_technique.metadata.add_setting("charge_current", 0.1, "mA")
    gcd_technique.metadata.add_setting("discharge_current", 0.1, "mA") 
    gcd_technique.metadata.add_setting("voltage_limit_high", 2.1, "V")
    gcd_technique.metadata.add_setting("voltage_limit_low", 0.9, "V")
    gcd_technique.metadata.add_setting("cycle_count", 20, None)
    gcd_technique.metadata.add_setting("current_range", 10, "mA")
    gcd_technique.metadata.add_setting("rest_time", 10, "min")
    gcd_technique.metadata.add_setting("c_rates", [0.2, 0.5, 1.0, 2.0], "C")
    gcd_technique.metadata.add_setting("cycles_per_rate", 5, None)
    
    gcd_technique.metadata.add_setting("temperature", 25, "°C")
    
    gcd_technique.metadata.add_note(
        name="measurement_purpose",
        value="Capacity retention and rate capability assessment"
    )
    
    gcd_technique.metadata.add_note(
        name="potentiostat_channel",
        value=2
    )
    
    print(f"\n✅ GCD Technique created") 
    print(f"   - Duration: {gcd_start.strftime('%H:%M')} - {gcd_end.strftime('%H:%M')}")
    print(f"   - {len(gcd_technique.metadata.devices)} device, {len(gcd_technique.metadata.settings)} parameters")
    
    # =================================================================
    # 6. AUXILIARY DATA: Temperature Monitoring
    # =================================================================
    # Temperature monitoring runs during all techniques
    temp_start = cv_start - timedelta(minutes=30)  # Start before first technique
    temp_end = gcd_end + timedelta(minutes=30)     # End after last technique
    
    # Get existing auxiliary (created in minimal example)
    temperature_aux = cell.get_auxiliary("auxiliary_001_temperature")
    
    # Set auxiliary metadata properties
    temperature_aux.metadata.id = 1
    temperature_aux.metadata.type = "Temperature Monitoring"
    temperature_aux.metadata.start = temp_start
    temperature_aux.metadata.end = temp_end
    temperature_aux.metadata.parent_techniques = [1, 2, 3]  # Monitor during all three techniques
    # No group needed - single temperature auxiliary
    
    # Temperature measurement equipment
    temperature_aux.metadata.add_device(
        name="TC_Cell_Surface",
        type="thermocouple", 
        manufacturer="Omega Engineering",
        model="5TC-TT-K-40-36",
        software_name="OMEGAware",
        software_version="2.1"
    )
    
    temperature_aux.metadata.add_device(
        name="DAQ_NI_6211",
        type="data_acquisition",
        manufacturer="National Instruments", 
        model="USB-6211",
        software_name="LabVIEW",
        software_version="2023"
    )
    
    # Temperature monitoring settings
    temperature_aux.metadata.add_setting("sampling_rate", 1.0, "Hz")
    temperature_aux.metadata.add_setting("temperature_range_min", 15, "°C")
    temperature_aux.metadata.add_setting("temperature_range_max", 45, "°C")
    temperature_aux.metadata.add_setting("thermocouple_type", "K", None)
    temperature_aux.metadata.add_setting("cold_junction_compensation", True, None)
    temperature_aux.metadata.add_setting("averaging_samples", 10, None)
    
    temperature_aux.metadata.add_setting("sensor_location", "cell_surface", None)
    temperature_aux.metadata.add_setting("adhesive_type", "thermally_conductive", None)
    temperature_aux.metadata.add_setting("reference_distance", 10, "cm")
    
    temperature_aux.metadata.add_note(
        name="measurement_purpose",
        value="Thermal monitoring for temperature-dependent performance correlation"
    )
    
    print(f"\n✅ Temperature monitoring created")
    print(f"   - Duration: {temp_start.strftime('%H:%M')} - {temp_end.strftime('%H:%M')}")
    print(f"   - Covers techniques: {temperature_aux.metadata.parent_techniques}")
    print(f"   - {len(temperature_aux.metadata.devices)} devices")
    
    print(f"\n✅ Cell was added to study object")
    print(f"   - Study object now contains {len(my_first_study.cells)} cell(s)")
    
    # =================================================================
    # 7. SECOND CELL - Different construction and testing
    # =================================================================
    
    print("\n" + "="*60)
    print("🔋 CREATING SECOND CELL - Different Configuration")
    print("="*60)
    
    # Second cell metadata - different construction approach
    cell_2.metadata.id = "PZB-TF-002"
    cell_2.metadata.type = "Coin Cell"
    cell_2.metadata.cathode = "PTMA"  # Different polymer
    cell_2.metadata.anode = "Zn"
    cell_2.metadata.electrolyte = "gel_polymer"
    cell_2.metadata.objective = "Performance comparison with different polymer cathode and gel electrolyte"
    cell_2.metadata.nominal_capacity_ah = 0.00012  # Slightly smaller capacity
    cell_2.metadata.assembly_timestamp = base_timestamp + timedelta(days=1)  # Assembled one day later
    cell_2.metadata.assembly_manufacturer = "Friedrich-Schiller-Universität Jena"
    cell_2.metadata.assembly_environment = "Dry room (relative humidity < 2%)"
    
    # ANODE: Electroplated zinc (different method)
    cell_2.metadata.add_component(
        name="anode",
        materials=[
            ("Zinc", "active_material", 100.0, "wt%")
        ],
        procedures=[
            ("substrate_cleaning", "plasma_cleaning", None),
            ("deposition_method", "electroplating", None),
            ("electrolyte_solution", "ZnSO4_0.1M", None),
            ("current_density", 5.0, "mA/cm²"),
            ("deposition_time", 45, "min"),
            ("post_treatment", "rinsing_DI_water", None)
        ],
        properties=[
            ("thickness", 3.2, "µm"),
            ("surface_roughness_Ra", 28, "nm"),
            ("grain_size", 150, "nm")
        ]
    )
    
    # CATHODE: PTMA (Poly(2,2,6,6-tetramethyl-1-piperidinyloxy-4-yl methacrylate))
    cathode_2 = cell_2.metadata.add_component(name="cathode")
    
    # Different polymer cathode materials
    cathode_2.add_material("Poly(TEMPO methacrylate)", "redox_active_polymer", 70.0, "wt%")
    cathode_2.add_material("Ketjen Black", "conductive_additive", 25.0, "wt%")
    cathode_2.add_material("PVDF", "binder", 5.0, "wt%")
    
    # Different fabrication process
    cathode_2.add_procedure("preparation", """
        1. Dissolve PTMA and PVDF in NMP solvent.
        2. Add Ketjen Black and mix using planetary mixer.
        3. Cast onto aluminum foil using automatic coater.
    """, None)
    cathode_2.add_procedure("mixing_method", "planetary_mixer", None)
    cathode_2.add_procedure("mixing_speed", 2000, "rpm")
    cathode_2.add_procedure("mixing_time", 45, "min")
    cathode_2.add_procedure("solvent", "N-methyl-2-pyrrolidone", None)
    cathode_2.add_procedure("coating_method", "automatic_coater", None)
    cathode_2.add_procedure("coating_speed", 500, "µm/s")
    cathode_2.add_procedure("wet_thickness", 150, "µm")
    cathode_2.add_procedure("drying_condition", "vacuum_80C_12h", None)
    
    # Different cathode properties
    cathode_2.add_property("mass_loading", 3.8, "mg/cm²")
    cathode_2.add_property("theoretical_capacity", 111, "mAh/g")
    cathode_2.add_property("dry_thickness", 18, "µm")
    cathode_2.add_property("porosity", 45, "%")
    
    # ELECTROLYTE: Gel polymer electrolyte (different from first cell)
    cell_2.metadata.add_component(
        name="electrolyte",
        materials=[
            ("PMMA", "polymer_matrix", 45.0, "wt%"),
            ("Propylene carbonate", "plasticizer", 30.0, "wt%"),
            ("Zn(ClO4)2", "zinc_salt", 20.0, "wt%"),
            ("Ethylene carbonate", "co_solvent", 5.0, "wt%")
        ],
        procedures=[
            ("preparation_method", "solution_casting", None),
            ("mixing_temperature", 80.0, "°C"),
            ("mixing_time", 8, "h"),
            ("gelation_time", 24, "h"),
            ("final_drying", "vacuum_40C_6h", None)
        ],
        properties=[
            ("ionic_conductivity", 1.8e-3, "S/cm"),  # Higher than first cell
            ("thickness", 30, "µm"),
            ("gel_fraction", 92, "%")
        ]
    )
    
    # CATHODE CURRENT COLLECTOR: Aluminum foil (different from SS in first cell)
    cell_2.metadata.add_component(
        name="cathode_current_collector",
        materials=[
            ("Aluminum foil", "current_collector", 100.0, "wt%")
        ],
        properties=[
            ("thickness", 15, "µm"),
            ("surface_treatment", "carbon_coating", None)
        ]
    )
    
    # HOUSING: Coin cell (different packaging)
    cell_2.metadata.add_component(
        name="housing",
        materials=[
            ("Stainless steel", "coin_cell_case", None, None)
        ],
        procedures=[
            ("assembly_method", "crimping", None),
            ("crimping_pressure", 1.5, "tons"),
            ("sealing_gasket", "polypropylene", None)
        ],
        properties=[
            ("case_diameter", 20, "mm"),
            ("case_height", 3.2, "mm")
        ]
    )
    
    # Assembly notes
    cell_2.metadata.add_note(
        name="assembly_tool",
        value="MSK-110 coin cell crimper"
    )
    
    cell_2.metadata.add_note(
        name="conditioning_protocol", 
        value="12h at room temperature, then 4h at 40°C"
    )
    
    print(f"\n✅ Second cell '{cell_2.metadata.id}' created")
    print(f"   - {len(cell_2.metadata.components)} components")
    print(f"   - Different: gel electrolyte, PTMA cathode, coin cell packaging")
    
    # =================================================================
    # 8. TECHNIQUE 4: Electrochemical Impedance Spectroscopy
    # =================================================================
    eis_start = base_timestamp + timedelta(days=1, hours=2)  # Day after first cell tests
    eis_end = eis_start + timedelta(minutes=45)
    
    eis_technique.metadata.id = 1
    eis_technique.metadata.type = "Electrochemical Impedance Spectroscopy"
    eis_technique.metadata.start = eis_start
    eis_technique.metadata.end = eis_end
    
    # Different potentiostat for EIS
    eis_technique.metadata.add_device(
        name="Solartron_1470E",
        type="potentiostat",
        manufacturer="Solartron Analytical",
        model="1470E",
        software_name="CorrWare",
        software_version="3.5c"
    )
    
    # EIS parameters
    eis_technique.metadata.add_setting("dc_potential", 1.5, "V")  # Open circuit
    eis_technique.metadata.add_setting("ac_amplitude", 10, "mV")
    eis_technique.metadata.add_setting("frequency_range_high", 100000, "Hz")
    eis_technique.metadata.add_setting("frequency_range_low", 0.01, "Hz")
    eis_technique.metadata.add_setting("points_per_decade", 10, None)
    eis_technique.metadata.add_setting("integration_time", 5, "cycles")
    eis_technique.metadata.add_setting("delay_before_measurement", 300, "s")
    
    eis_technique.metadata.add_note(
        name="measurement_purpose",
        value="Impedance characterization and equivalent circuit modeling"
    )
    
    eis_technique.metadata.add_note(
        name="measurement_mode",
        value="potentiostatic"
    )
    
    print(f"\n✅ EIS Technique created")
    print(f"   - Duration: {eis_start.strftime('%H:%M')} - {eis_end.strftime('%H:%M')}")
    print(f"   - Frequency range: 0.01 Hz - 100 kHz")
    
    # =================================================================
    # 9. TECHNIQUE 5: Slow Scan Rate CV for second cell
    # =================================================================
    cv_slow_start = eis_end + timedelta(minutes=15)  # Short rest after EIS
    cv_slow_end = cv_slow_start + timedelta(minutes=120)  # Very slow CV takes longer
    
    cv_slow_technique.metadata.id = 2
    cv_slow_technique.metadata.type = "Cyclic Voltammetry"
    cv_slow_technique.metadata.start = cv_slow_start
    cv_slow_technique.metadata.end = cv_slow_end
    
    # Same potentiostat as EIS
    cv_slow_technique.metadata.add_device(
        name="Solartron_1470E",
        type="potentiostat",
        manufacturer="Solartron Analytical", 
        model="1470E",
        software_name="CorrWare",
        software_version="3.5c"
    )
    
    # Very slow CV parameters for detailed analysis
    cv_slow_technique.metadata.add_setting("initial_potential", 1.0, "V")
    cv_slow_technique.metadata.add_setting("initial_potential_hold", 60, "s")
    cv_slow_technique.metadata.add_setting("vertex_potential_low", 0.5, "V")
    cv_slow_technique.metadata.add_setting("vertex_potential_high", 2.0, "V")
    cv_slow_technique.metadata.add_setting("scan_rate", 0.5, "mV/s")  # Very slow
    cv_slow_technique.metadata.add_setting("cycle_count", 2, None)
    cv_slow_technique.metadata.add_setting("current_range", 1, "mA")
    cv_slow_technique.metadata.add_setting("potential_range", [-1.0, 3.0], "V")
    
    cv_slow_technique.metadata.add_note(
        name="measurement_purpose",
        value="High-resolution redox peak analysis and mechanistic studies"
    )
    
    cv_slow_technique.metadata.add_note(
        name="data_sampling",
        value="high_resolution"
    )
    
    print(f"\n✅ Slow CV Technique created")
    print(f"   - Duration: {cv_slow_start.strftime('%H:%M')} - {cv_slow_end.strftime('%H:%M')}")
    print(f"   - Ultra-slow scan rate: 0.5 mV/s")
    
    # =================================================================
    # 10. AUXILIARY DATA: Pressure Monitoring for coin cell
    # =================================================================
    pressure_start = eis_start - timedelta(minutes=15)  # Start before EIS
    pressure_end = cv_slow_end + timedelta(minutes=15)   # End after slow CV
    
    pressure_aux.metadata.id = 1
    pressure_aux.metadata.type = "Pressure Monitoring"
    pressure_aux.metadata.start = pressure_start
    pressure_aux.metadata.end = pressure_end
    pressure_aux.metadata.parent_techniques = [1, 2]  # Monitor during EIS and slow CV
    # No group needed - single pressure auxiliary
    
    # Pressure monitoring equipment
    pressure_aux.metadata.add_device(
        name="Honeywell_26PC",
        type="pressure_sensor",
        manufacturer="Honeywell",
        model="26PCAFA6G",
        software_name="LabView_DAQ",
        software_version="2023"
    )
    
    pressure_aux.metadata.add_device(
        name="DAQ_USB6009",
        type="data_acquisition",
        manufacturer="National Instruments",
        model="USB-6009",
        software_name="LabVIEW",
        software_version="2023"
    )
    
    # Pressure monitoring settings
    pressure_aux.metadata.add_setting("sampling_rate", 0.1, "Hz")  # Slower than temperature
    pressure_aux.metadata.add_setting("pressure_range_min", 0.8, "bar")
    pressure_aux.metadata.add_setting("pressure_range_max", 1.2, "bar")
    pressure_aux.metadata.add_setting("sensor_accuracy", 0.25, "%")
    pressure_aux.metadata.add_setting("temperature_compensation", True, None)
    
    pressure_aux.metadata.add_setting("sensor_location", "environmental", None)
    pressure_aux.metadata.add_setting("measurement_type", "absolute_pressure", None)
    
    pressure_aux.metadata.add_note(
        name="measurement_purpose",
        value="Environmental pressure monitoring for coin cell volume change correlation"
    )
    
    print(f"\n✅ Pressure monitoring created") 
    print(f"   - Duration: {pressure_start.strftime('%H:%M')} - {pressure_end.strftime('%H:%M')}")
    print(f"   - Covers techniques: {pressure_aux.metadata.parent_techniques}")
    
    print(f"\n✅ Second cell added to study object")
    print(f"   - Study object now contains {len(my_first_study.cells)} cell(s)")
    print(f"   - Total techniques: {sum(len(cell.techniques) for cell in my_first_study.cells.values())}")
    print(f"   - Total auxiliaries: {sum(len(cell.auxiliary) for cell in my_first_study.cells.values())}")
    
    return my_first_study

def demonstrate_metadata_access(study_object):
    """Demonstrate find/modify functionality of the metadata system."""
    
    print("\n" + "="*60)
    print("🔍 DEMONSTRATING METADATA ACCESS & MODIFICATION")
    print("="*60)
    
    # Extract objects from study_object
    study = study_object.metadata
    cell = study_object.get_cell("cell_001")
    cell_2 = study_object.get_cell("cell_002")
    cv_tech = cell.get_technique("technique_001_CV")
    cv_tech_2 = cell.get_technique("technique_002_CV")
    gcd_tech = cell.get_technique("technique_003_GCD")
    temp_aux = cell.get_auxiliary("auxiliary_001_temperature")
    
                # Second cell objects
    eis_tech = cell_2.get_technique("technique_001_EIS")
    cv_slow_tech = cell_2.get_technique("technique_002_CV")
    pressure_aux = cell_2.get_auxiliary("auxiliary_001_pressure")
    
    # =================================================================
    # Study-level access and modification
    # =================================================================
    print("\n📋 Study-level operations:")
    
    # Find and modify contributor
    marcus = study.find_contributor("Marcus Weber")
    if marcus:
        original_email = marcus.email
        marcus.email = "m.weber.phd@uni-jena.de"  # Updated email
        marcus.add_additional_info("Thesis_Topic", "Polymer-Zinc Battery Systems")
        print(f"   ✅ Updated Marcus's email: {original_email} → {marcus.email}")
        print(f"   ✅ Added thesis topic: {marcus.additional_info[-1]['value']}")
    
    # Find funding and access details
    dfg = study.find_funding("Deutsche Forschungsgemeinschaft (DFG)")
    if dfg:
        print(f"   ✅ Found DFG funding: {dfg.grant_number}")
    
    # =================================================================
    # Cell-level nested access and modification  
    # =================================================================
    print("\n🔋 Cell-level nested operations:")
    
    # Find component and modify material
    cathode = cell.metadata.find_component("cathode")
    if cathode:
        mno2 = cathode.find_material("Manganese dioxide")
        if mno2:
            original_value = mno2.amount.value
            mno2.amount.value = 78.0  # Optimized composition
            print(f"   ✅ Updated MnO2 content: {original_value}% → {mno2.amount.value}%")
        
        # Modify mixing speed
        mixing_speed = cathode.find_procedure("mixing_speed")
        if mixing_speed:
            mixing_speed.value = 500  # Increased speed
            print(f"   ✅ Updated mixing speed: {mixing_speed.value} {mixing_speed.unit}")
        
        # Modify mixing time
        mixing_time = cathode.find_procedure("mixing_time") 
        if mixing_time:
            mixing_time.value = 3  # Extended time
            print(f"   ✅ Extended mixing time: {mixing_time.value} {mixing_time.unit}")
    
    # Modify electrolyte composition
    electrolyte = cell.metadata.find_component("electrolyte")
    if electrolyte:
        peo = electrolyte.find_material("Poly(ethylene oxide)")
        li_salt = electrolyte.find_material("LiTFSI")
        if peo and li_salt:
            # Rebalance composition
            peo.amount.value = 65.0
            li_salt.amount.value = 20.0  # Reduced for better mechanical properties
            print(f"   ✅ Rebalanced electrolyte: PEO {peo.amount.value}%, LiTFSI {li_salt.amount.value}%")
    
    # Update conditioning protocol
    conditioning = cell.metadata.find_note("conditioning_protocol")
    if conditioning:
        conditioning.value = "48h at 60°C for enhanced electrolyte penetration"
        print(f"   ✅ Extended conditioning time to 48h")
    
    # =================================================================
    # Technique-level access and modification
    # =================================================================
    print("\n⚡ Technique-level operations:")
    
    # Modify CV settings
    scan_rate = cv_tech.metadata.find_setting("scan_rate")
    if scan_rate:
        original_rate = scan_rate.value
        scan_rate.value = 0.05  # Slower for better resolution
        print(f"   ✅ CV scan rate: {original_rate} → {scan_rate.value} {scan_rate.unit}")
    
    # Modify cycle count
    cycles = cv_tech.metadata.find_setting("cycle_count")
    if cycles:
        cycles.value = 3  # Reduced for preliminary test
        print(f"   ✅ CV cycles reduced to: {cycles.value}")
    
    # Modify GCD parameters
    upper_limit = gcd_tech.metadata.find_setting("voltage_limit_high") 
    if upper_limit:
        upper_limit.value = 2.05  # Slightly lower for safety
        print(f"   ✅ GCD upper limit: {upper_limit.value} {upper_limit.unit}")
    
    # Update measurement purpose
    cv_purpose = cv_tech.metadata.find_note("measurement_purpose")
    if cv_purpose:
        cv_purpose.value = "Preliminary electrochemical stability assessment"
        print(f"   ✅ Updated CV measurement purpose")
    
    # =================================================================
    # Auxiliary data access and modification
    # =================================================================
    print("\n🌡️  Auxiliary data operations:")
    
    # Modify temperature sampling
    sampling_rate = temp_aux.metadata.find_setting("sampling_rate")
    if sampling_rate:
        sampling_rate.value = 0.5  # Reduce to save storage space
        print(f"   ✅ Temperature sampling: {sampling_rate.value} {sampling_rate.unit}")
    
    # Update measurement purpose
    temp_purpose = temp_aux.metadata.find_note("measurement_purpose")
    if temp_purpose:
        temp_purpose.value = "Cell thermal response monitoring during electrochemical testing"
        print(f"   ✅ Updated temperature measurement purpose")
    
    # Find and modify device info
    thermocouple = temp_aux.metadata.find_device("TC_Cell_Surface")
    if thermocouple and thermocouple.software_name:
        thermocouple.software_version = "2.2"  # Updated software
        print(f"   ✅ Updated thermocouple software to v{thermocouple.software_version}")
    
    # =================================================================
    # Second cell operations
    # =================================================================
    print("\n🔋 Second cell operations:")
    
    # Modify second cell electrolyte composition
    gel_electrolyte = cell_2.metadata.find_component("electrolyte")
    if gel_electrolyte:
        pmma = gel_electrolyte.find_material("PMMA")  
        if pmma:
            pmma.amount.value = 50.0  # Increase polymer content
            print(f"   ✅ Increased PMMA content to {pmma.amount.value}%")
    
    # Modify EIS settings
    ac_amplitude = eis_tech.metadata.find_setting("ac_amplitude")
    if ac_amplitude:
        ac_amplitude.value = 5  # Reduce amplitude for better linearity
        print(f"   ✅ EIS AC amplitude reduced to {ac_amplitude.value} {ac_amplitude.unit}")
    
    # Update slow CV purpose
    slow_cv_purpose = cv_slow_tech.metadata.find_note("measurement_purpose")
    if slow_cv_purpose:
        slow_cv_purpose.value = "Ultra-high resolution mechanistic analysis of redox processes"
        print(f"   ✅ Updated slow CV measurement purpose")
    
    # Modify pressure monitoring sampling
    pressure_sampling = pressure_aux.metadata.find_setting("sampling_rate")
    if pressure_sampling:
        pressure_sampling.value = 0.05  # Even slower sampling
        print(f"   ✅ Pressure sampling reduced to {pressure_sampling.value} {pressure_sampling.unit}")

def demonstrate_serialization(study_object):
    """Demonstrate serialization capabilities."""
    
    print("\n" + "="*60) 
    print("💾 DEMONSTRATING SERIALIZATION & DATA EXPORT")
    print("="*60)
    
    # Extract objects from study_object
    study = study_object.metadata
    cell = study_object.get_cell("cell_001")
    cell_2 = study_object.get_cell("cell_002")
    cv_tech = cell.get_technique("technique_001_CV")
    cv_tech_2 = cell.get_technique("technique_002_CV")
    gcd_tech = cell.get_technique("technique_003_GCD")
    temp_aux = cell.get_auxiliary("auxiliary_001_temperature")
    
    # Second cell objects
    eis_tech = cell_2.get_technique("technique_001_EIS")
    cv_slow_tech = cell_2.get_technique("technique_002_CV")
    pressure_aux = cell_2.get_auxiliary("auxiliary_001_pressure")
    
    # Study serialization
    print("\n📊 Study metadata serialization:")
    study_dict = study.to_dict()
    print(f"   ✅ Dictionary: {len(study_dict)} top-level keys")
    print(f"   ✅ Contributors: {len(study_dict['metadata']['contributors'])}")
    print(f"   ✅ Funding sources: {len(study_dict['metadata']['funding'])}")
    
    study_attrs = study.to_netcdf_attrs()
    print(f"   ✅ NetCDF attributes: {len(study_attrs)} attributes")
    
    # Cell serialization with nested structure
    print("\n🔋 Cell metadata serialization:")
    cell_dict = cell.metadata.to_dict()
    tiers = list(cell_dict.keys())
    print(f"   ✅ BDG tiers: {tiers}")
    print(f"   ✅ Components: {len(cell_dict['secondary']['components'])}")
    if 'tertiary' in cell_dict:
        print(f"   ✅ Notes: {len(cell_dict['tertiary']['additional_notes'])}")
    
    # Show component detail
    cathode_data = None
    for comp in cell_dict['secondary']['components']:
        if comp['name'] == 'cathode':
            cathode_data = comp
            break
    
    if cathode_data:
        print(f"   ✅ Cathode materials: {len(cathode_data['materials'])}")
        print(f"   ✅ Cathode procedures: {len(cathode_data['procedures'])}")
        print(f"   ✅ Cathode properties: {len(cathode_data['properties'])}")
    
    # Show electrolyte detail
    electrolyte_data = None
    for comp in cell_dict['secondary']['components']:
        if comp['name'] == 'electrolyte':
            electrolyte_data = comp
            break
    
    if electrolyte_data:
        print(f"   ✅ Electrolyte materials: {len(electrolyte_data['materials'])}")
        print(f"   ✅ Electrolyte procedures: {len(electrolyte_data['procedures'])}")
    
    # Technique serialization
    print("\n⚡ Technique metadata serialization:")
    cv_dict = cv_tech.metadata.to_dict()
    gcd_dict = gcd_tech.metadata.to_dict()
    
    print(f"   ✅ CV settings: {len(cv_dict['secondary']['settings'])}")
    print(f"   ✅ GCD settings: {len(gcd_dict['secondary']['settings'])}")
    
    # Auxiliary serialization  
    print("\n🌡️  Auxiliary metadata serialization:")
    temp_dict = temp_aux.metadata.to_dict()
    print(f"   ✅ Temperature devices: {len(temp_dict['secondary']['devices'])}")
    print(f"   ✅ Parent techniques: {temp_dict['primary']['parent_techniques']}")
    
    # Second cell serialization
    print(f"\n🔋 Second cell metadata serialization:")
    cell_2_dict = cell_2.metadata.to_dict()
    print(f"   ✅ Second cell components: {len(cell_2_dict['secondary']['components'])}")
    
    # Show gel electrolyte detail
    gel_electrolyte_data = None
    for comp in cell_2_dict['secondary']['components']:
        if comp['name'] == 'electrolyte':
            gel_electrolyte_data = comp
            break
    
    if gel_electrolyte_data:
        print(f"   ✅ Gel electrolyte materials: {len(gel_electrolyte_data['materials'])}")
        print(f"   ✅ Gel electrolyte procedures: {len(gel_electrolyte_data['procedures'])}")
    
    # EIS technique serialization
    print(f"\n⚡ EIS technique serialization:")
    eis_dict = eis_tech.metadata.to_dict()
    print(f"   ✅ EIS settings: {len(eis_dict['secondary']['settings'])}")
    
    # Pressure auxiliary serialization
    print(f"\n📊 Second auxiliary serialization:")
    pressure_dict = pressure_aux.metadata.to_dict()
    print(f"   ✅ Pressure devices: {len(pressure_dict['secondary']['devices'])}")
    
    # JSON export demonstration
    print(f"\n📄 JSON export samples:")
    print(f"   Study JSON: {len(study.to_json())} characters")
    print(f"   Cell 1 JSON: {len(cell.metadata.to_json())} characters")
    print(f"   Cell 2 JSON: {len(cell_2.metadata.to_json())} characters")
    
    # Show small sample of actual JSON structure
    print(f"\n   Study JSON structure preview:")
    study_json = json.loads(study.to_json())
    print(f"   {json.dumps(study_json['file_metadata'], indent=6)}")

def demonstrate_structure_visualization(study_object):
    """Demonstrate the new structure visualization capabilities."""
    
    print("\n" + "="*60)
    print("🎨 DEMONSTRATING STRUCTURE VISUALIZATION")
    print("="*60)
    
    # Simplified version
    print("\n📟 Simplified Structure Visualization:")
    print("-" * 40)
    study_object.print_structure(show_metadata=False, show_data=False)
    
    # Detailed version
    print("\n📟 Detailed Structure Visualization:")
    print("-" * 40)
    study_object.print_structure(show_metadata=True, show_data=False)
    
    # Try graphical visualization  
    print("\n🎨 Graphical Structure Visualization:")
    print("-" * 40)
    
    # Graphical visualization
    print("📊 Creating entity relationship diagrams...")
    try:
        study_object.plot_structure(
            filename="polymer_structure_detailed", 
            format="svg",
            show_metadata=True
        )

        study_object.plot_structure(
            filename="polymer_structure_simple",
            format="svg", 
            show_metadata=False
        )
        
    except Exception as e:
        print(f"⚠️  Visualization failed: {e}")





def main():
    """Main demonstration function."""
    
    print("🧬 COMPREHENSIVE POLYMER/ZINC BATTERY METADATA DEMONSTRATION")
    print("Using the new echem_data_tool")
    print("="*80)
    
    # Create complete study metadata
    my_first_study = create_polymer_zinc_study()
    
    # Demonstrate access and modification capabilities
    demonstrate_metadata_access(my_first_study)
    
    # Demonstrate serialization and export
    demonstrate_serialization(my_first_study)
    
    # Demonstrate structure visualization
    demonstrate_structure_visualization(my_first_study)
    
if __name__ == "__main__":
    main()