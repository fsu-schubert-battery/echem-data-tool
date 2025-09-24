# Metadata for discribing an electrochemical cells

## Introduction 
Based on [Principles of the Battery Data Genome](https://doi.org/10.1016/j.joule.2022.08.008) battery metadata could be organized in three or more tiers depending on the detail level:
 
Standardizing metadata while maximizing value, flexibility, and impact is a significant challenge. Establishing what information is needed and its format will require not only extensive community discussion, but also innovations to enable broadest possible participation. The BDG will manage trade-offs by organizing into layers of detail: primary, secondary, and tertiary:    
- Primary metadata are the minimal mandatory information that must be reported to cover the basic concepts will be structured as a table of contents. It will include data owners and generators, a unique identifier for each cell, experimental objective, the nature of the device/s that were tested including chemistry, and specific tests. Examples are shown in Table S1.
- Secondary metadata are more comprehensive, with significant experimental details including cell and electrode design, commercial-cell identification codes, the manner of attachments to test equipment, etc. The journals Joule and Advanced Energy Materials already have battery experimental reporting requirements that provide initial concepts.83
- Tertiary metadata refers to highly specialized, nonroutine information that likely vary substantially between subfields and should be defined by stakeholder’s consensus—for example, material synthesis protocols and simulation model parameters.

With this approach and the more specfic Battery Checklist from [Joule](https://doi.org/10.1016/j.joule.2020.12.026) the first draft was designed.

## Metadata example json

```json
{
  "metadata": {
    "tier_one": {
      "Experiment name": "20250715_SW-EC35-2_1_PFPMAm-co-TEGDMA1,0_Zn_2MZnClO4_RC_data",
      "Date of Experiment": "2025-07-15",
      "Operator": "Sebastian Witt",
      "Operator Affiliation": "Friedrich Schiller University Jena: Jena, Thuringia, DE",
      "Operator ORCID": "https://orcid.org/0009-0002-3574-5339",
      "Supervisor": "Dr. Martin D. Hager",
      "Supervisor Affiliation": "Friedrich Schiller University Jena: Jena, Thuringia, DE",
      "Supervisor ORCID": "https://orcid.org/0000-0002-6373-6600",
      "UIDs": {
        "Cell ID": "SW-EC35-2",
        "Electrode ID": "SW-E14-2",
        "Active Material ID": "SW-R110-A",
        "Reaction ID": "SW-R110"
      },
      "Objective of Test": "Rate capability test",
      "Cathode chemistry": "Ferrocene",
      "Anode chemistry": "Zinc",
      "Nominal Capacity (Ah)": 0.000127,
      "Potentiostat/Galvanostat": "Biologic VMP3",
      "details": "Basic information about the experiment, cell and electrode materials"
    },
    "tier_two": {
      "Electrode Composition": {
        "Active Material": "PFPMAm-co-TEGDMA (1%)",
        "Active Material (w.-%)": 65,
        "Conductive Additive": "Super P",
        "Conductive Additive (w.-%)": 30,
        "Binder": "High viscosity CMC (Sigma Aldrich)",
        "Binder (w.-%)": 5
      },
      "Electrode Area (cm2)": 1.13,
      "Electrode Thickness (mm)": 0.33,
      "Active Material Mass (g)": 0.0014700000286102296,
      "Current collector": "stainless stell foil",
      "Electrolyte": {
        "Amount (mL)": 0.15,
        "Electrolyte": "2.0M Zn(ClO4)2 in water",
        "Concentration (mol/L)": 2.0,
        "Additives": "",
        "Solvent": "water"
      },
      "Separator:"{
        "Material": "Whatman glass microfiber grade GF/D",
        "Diameter (cm)": "1.2"
      },
      "Total Battery Mass (g)": "",
      "Areal Mass (g/cm2)": 1.299765393880809,
      "Cell Format": "Three-electrode Swagelok-type",
      "Cell Type": "Half-cell",
      "Reference electrode": "Ag wire",
      "Specific capacity (Ah/kg)": 86.39
    },
    "tier_three":{
    "converter_version": "1.1.0"
    }
  }
}
```

## Metadata explanation

The following explains every field from the example JSON above. It maps the JSON keys to clear human-readable meanings so readers and downstream tools can understand what to record and why.

### `metadata`
Top-level object containing all experiment metadata, organized by tiers (`tier_one`, `tier_two`, etc.).

### `tier_one` (Primary metadata)
Primary metadata are the minimum essential details required to identify and understand the experiment at a glance.

- `Experiment name`: A unique, human- and machine-readable experiment identifier (often encodes date, cell ID and test type).
- `Date of Experiment`: Date when the experiment was performed (ISO YYYY-MM-DD recommended).
- `Operator`: Full name of the person who ran the experiment.
- `Operator Affiliation`: Institution and location of the operator.
- `Operator ORCID`: ORCID or other persistent researcher identifier for the operator (URL recommended).
- `Supervisor`: Name of the supervisor/PI responsible for the experiment.
- `Supervisor Affiliation`: Institution and location of the supervisor.
- `Supervisor ORCID`: ORCID or other persistent identifier for the supervisor.
- `UIDs`: A small object for stable unique identifiers used in your lab or project; helps cross-referencing across datasets.
  - `Cell ID`: Identifier for the physical assembled cell.
  - `Electrode ID`: Identifier for the electrode or batch.
  - `Active Material ID`: Identifier for the active material (e.g., batch or sample ID).
  - `Reaction ID`: Identifier for the ative material reaction
- `Objective of Test`: Short description of the experiment goal (e.g., rate capability test, cycling stability).
- `Cathode chemistry`: Cathode active material or chemistry name (e.g. LFP, NMC or Redox active species Ferrocene, Tempo)
- `Anode chemistry`: Anode active material or chemistry name. (e.g. Li metall, Zinc metall, Graphite, Redox active spiecies etc.)
- `Nominal Capacity (Ah)`: Nominal or theoretical capacity in ampere-hours (used for normalization and sanity checks).
- `Potentiostat/Galvanostat`: Make/model of the measurement instrument (helps document measurement limits and settings).
- `details`: Short free-text field for other top-level notes about the experiment or dataset.

### `tier_two` (Secondary metadata)
Secondary metadata capture device and material details required for reproducing, interpreting, and normalizing results.

- `Electrode Composition`: Object describing electrode formulation and target weight fractions.
  - `Active Material`: Name of the active material used.
  - `Active Material (w.-%)`: Weight fraction (percent) of active material in the electrode.
  - `Conductive Additive`: Name of conductive additive used (e.g., Super P, carbon black).
  - `Conductive Additive (w.-%)`: Weight fraction (%) of the conductive additive.
  - `Binder`: Binder material used to bind the electrode components.
  - `Binder (w.-%)`: Weight fraction (%) of the binder.
- `Electrode Area (cm2)`: Geometric projected area of the electrode in square centimeters (used when converting areal to gravimetric metrics).
- `Electrode Thickness (mm)`: Thickness of the coated electrode in millimeters.
- `Active Material Mass (g)`: Mass of active material used on the electrode (in grams); useful for gravimetric capacity calculations.
- `Current collector`: Name of current collector used (e.g. stainless steel, aluminium, copper). 
- `Electrolyte`: Object describing the electrolyte composition and volume.
  - `Amount (mL)`: Volume of electrolyte added to the cell in milliliters.
  - `Electrolyte`: Short chemical description (e.g., "2.0M Zn(ClO4)2 in water").
  - `Concentration (mol/L)`: Molar concentration (moles per liter) of the primary salt.
  - `Additives`: Any additional electrolyte additives (leave empty string if none).
  - `Solvent`: Solvent used (e.g., water, propylene carbonate).
- `Separator`: Object descriping the separator material and dimensions.
    -`Material`: Material/Discription of used separator.
    -`Diameter (cm)`: Diameter of Separator used.
- `Total Battery Mass (g)`: Optional total assembled cell mass in grams (may be empty if not measured).
- `Areal Mass (g/cm2)`: Areal loading (mass per unit electrode area) in g/cm^2; useful for scaling and normalization.
- `Cell Format`: Physical format of the cell (e.g., coin cell, Swagelok-type, pouch).
- `Cell Type`: Functional type of the measurement (e.g., half-cell, full cell, three-electrode).
- `Reference electrode`: Type of reference electrode used in three-electrode setups (e.g., Ag wire, Ag/AgCl).
- `Specific capacity (Ah/kg)`: Gravimetric capacity (ampere-hours per kilogram of active material) as measured or calculated.

### `tier_three` (Tertionary metadata)
Tertionary metadata like provences for converter version to generate the file

- `converter_version`: Version string for the tool or schema used to produce or convert this metadata. Use semantic versioning so downstream tools can detect compatibility.

## What needs to be implemeted
- Ability to describe Working Electrode and Counter Electrode
- Flow cell metadata 

## Notes and best practices
- Use ISO formats for dates and SI units for numeric fields.
- Prefer persistent identifiers (ORCID, DOIs, lab UID patterns) for people, materials and samples.
- For empty or unknown numeric fields, prefer an explicit null in JSON rather than an empty string; in human-readable docs you may show an empty string but machine-readable exports should use null.
- Keep `tier_one` small and required; expand `tier_two` and `tier_three` for supplementary experimental details.

This section provides a concise, field-by-field explanation so technicians, curators, and automated pipelines can record consistent metadata for electrochemical cells.
