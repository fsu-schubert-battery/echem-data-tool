# Design: Elektrochemische Daten-Klassen (xarray-zentriert)

Diese Spezifikation beschreibt xarray-basierte Daten-Container-Klassen für elektrochemische Messungen. Ziel ist eine klare Trennung zwischen Datenhaltung/Validierung und Analyse, sowie eine einheitliche, robuste Schnittstelle für Analysemodule.

## Übersicht & Architektur

Kernkonzept: Trennung von Daten und Analyse.

```
┌───────────────────┐
│ FileLoader        │  Liest Rohdateien (MPR, CSV, …) und erstellt StudyObject
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ StudyObject       │  Hierarchie: Study > Cells > Groups > Techniques/Aux
│ (study/core.py)   │  Organisiert Messdaten + Metadaten; exportiert als xarray/netCDF
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Data Classes      │  xarray-zentrierte Container mit
│ (CV, EIS, GC, …)  │  • required_variables
│                   │  • Strukturvalidierung
│                   │  • .data: xr.Dataset
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Analyzer Modules  │  Reine Algorithmen/Modelle, konsumieren xr.Dataset
│ (analyzer/*)      │  • Peak-/Capacity-Analyzer, Impedanz-Fitter, …
└───────────────────┘
```

Aufgaben der Daten-Klassen
- Strukturvorgabe für Loader/Study (required_variables)
- Daten aufnehmen und auf Struktur prüfen (nur Pflichtvariablen, keine Physik)
- Rohdaten bereitstellen (.data: xr.Dataset), einfache Utilities (z. B. Zeit-Slicing)
- Bequemer Export (to_dataframe), optional Convenience-Export (to_netcdf)

Nicht Aufgabe der Daten-Klassen
- Analyse, Feature-Engineering, Fit-Algorithmen, Peak-Detektion, Zyklen-Parsing, Plotting

Hinweis zur Integration mit StudyObject
- StudyObject (in `echem_data_tool/study/core.py`) ist die hierarchische Quelle der Wahrheit (Study → Cells → Groups → Techniques/Auxiliary) und übernimmt I/O nach netCDF/xarray.
- Techniken und Auxiliaries halten ihre Messdaten in `DataGroup`/`DataVariable`. Für Analyse-Workflows kann pro Technik ein kompaktes `xr.Dataset` via `Technique.to_xarray_group()` erzeugt werden.
- Daten-Klassen arbeiten mit solchen Technik-Datasets; Convenience-Exporte (to_netcdf) sind möglich, für persistente I/O sollte `StudyObject.save()` genutzt werden.

## Design-Prinzipien

1) Nur Rohdaten in Daten-Klassen

Rohdaten (gehören in Daten-Klassen): direkt gemessene Größen wie time, potential, current, instrument flags (z. B. phase), frequency, z_real, z_imag.

Berechnete Größen (in Analyzer): capacity, cycle_number, spezifische Kapazität, coulombic efficiency, Peak-Positionen, Fit-Parameter.

Ausnahme: simple Properties mit trivialer, parameterfreier Mathematik sind ok (z. B. |Z|, Phase aus z_real/z_imag).

2) Struktur- statt Inhaltsvalidierung

- Data-Klassen prüfen ausschließlich, ob alle required_variables vorhanden sind.
- Inhaltsqualität (NaN, Ausreißer, Mindestlängen, Monotonie) prüfen Analyzer.

3) Auxiliary-Daten separat denken, bei Bedarf zusammenführen

- Messdaten-Kerndatensatz bleibt schlank (required_variables).
- Externe Hilfsdaten (Temperatur, Druck, RH, …) können separat verwaltet und in Analyzer-Schritten via Interpolation/Alignment zusammengeführt werden.
- Aktueller Stand: Auxiliary wird über `StudyObject`/`Auxiliary` geführt; ein separates `AuxiliaryData` kann später ergänzt werden.

## Klassendefinitionen

### BaseData (abstrakt)

Abstrakte Basisklasse für xarray-basierte Container.

Contract (Kurzfassung)
- Input: xr.Dataset mit allen required_variables als Datenvariablen (data_vars)
- Output: Bereitstellung des Datasets über .data und bequeme Exporte/Utilities
- Validation: Nur Strukturprüfung (required_variables vorhanden); keine Inhalts-/Qualitätsprüfung
- Errors: ValueError, wenn Daten fehlen oder required_variables fehlen

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import xarray as xr
import pandas as pd
import numpy as np


class BaseData(ABC):
    """
    Abstrakte Basisklasse für elektrochemische Datencontainer.

    Vererbung:
    BaseData (abstrakt)
    ├── TimeSeriesData (abstrakt) – zeitbasiert (CV, GC, CCCV, …)
    └── EISData – frequenzbasiert
    """

    technique_type: str = "base"
    required_variables: tuple[str, ...] = ()

    def __init__(self, data: Optional[xr.Dataset] = None):
        """
        Initialize the container.

        Args:
            data: Optional xarray Dataset. Muss alle `required_variables` als
                  Datenvariablen (data_vars) enthalten, nicht nur als Koordinaten.

        Note:
            Diese Klasse führt nur Strukturvalidierung durch. Inhalts-/Qualitätsprüfungen
            (NaN, Wertebereiche, Längen) sind Aufgabe der Analyzer.
        """
        self._data: Optional[xr.Dataset] = data

    # ---------- Daten-Management ----------
    def load_from_technique_dataset(self, technique_dataset: xr.Dataset) -> None:
        """
        Lade Daten aus einem Technik-Dataset (z. B. via `Technique.to_xarray_group()`).

        Args:
            technique_dataset: xr.Dataset eines einzelnen Technique-Objekts.
                Erwartet wird, dass alle `required_variables` als data_vars vorhanden sind.

        Raises:
            ValueError: Wenn eine der `required_variables` fehlt.

        Postconditions:
            - self._data verweist auf das übergebene Dataset
            - Strukturvalidierung wurde ausgeführt
        """
        self._data = technique_dataset
        self._validate_data()

    def _validate_data(self) -> None:
        """
        Strukturvalidierung: Prüft, ob alle `required_variables` vorhanden sind.

        Details:
            - Es wird ausschließlich geprüft, ob alle geforderten Variablennamen
              in `self._data.data_vars` enthalten sind.
            - Koordinaten (coords) werden hier nicht als Ersatz akzeptiert.
              Falls Zeit als Koordinate statt data_var vorliegt, sollte der Loader
              diese als data_var bereitstellen oder `required_variables` angepasst werden.

        Silent return, wenn keine Daten geladen sind (None).

        Raises:
            ValueError: Falls eine Pflichtvariable fehlt.
        """
        if self._data is None:
            return
        missing = set(self.required_variables) - set(self._data.data_vars)
        if missing:
            raise ValueError(
                f"Fehlende Pflicht-Variablen für {self.technique_type}: {sorted(missing)}"
            )

    # ---------- Zugriff ----------
    @property
    def data(self) -> xr.Dataset:
        """
        Zugriff auf das Rohdaten-Dataset.

        Returns:
            xr.Dataset: Das gespeicherte Messdaten-Set.

        Raises:
            ValueError: Wenn noch keine Daten geladen wurden.
        """
        if self._data is None:
            raise ValueError("Keine Daten geladen")
        return self._data

    @property
    def variables(self) -> list[str]:
        return list(self._data.data_vars) if self._data is not None else []

    # ---------- Export ----------
    def to_dataframe(self) -> pd.DataFrame:
        """
        Export in ein pandas DataFrame.

        Returns:
            pd.DataFrame: Tabellarische Darstellung aller Variablen; Indizes werden zu Spalten.

        Raises:
            ValueError: Wenn keine Daten verfügbar sind.
        """
        if self._data is None:
            raise ValueError("Keine Daten verfügbar")
        return self._data.to_dataframe().reset_index()

    def to_netcdf(self, path: Path) -> None:
        """
        Convenience-Export nach netCDF.

        Args:
            path: Zielpfad für die Datei.

        Notes:
            - Für konsistente Datei-I/O wird `StudyObject` empfohlen.
            - Es wird ein Attribut `technique_type` gesetzt.

        Raises:
            ValueError: Wenn keine Daten vorliegen.
        """
        if self._data is None:
            raise ValueError("Keine Daten zum Speichern")
        self._data.assign_attrs({"technique_type": self.technique_type}).to_netcdf(path, engine="h5netcdf")

    # ---------- Utility ----------
    def summary(self) -> str:
        """
        Textzusammenfassung der geladenen Daten.

        Returns:
            str: Techniktyp, Dimensionen und Variablennamen oder Hinweis, falls leer.
        """
        if self._data is None:
            return f"{self.technique_type}: Keine Daten geladen"
        return (
            f"Technik: {self.technique_type}\n"
            f"Dims: {dict(self._data.dims)}\n"
            f"Variablen: {self.variables}"
        )

    def __repr__(self) -> str:
        ''' Kurze, robuste Objekt-Repräsentation für Debugging/Logging.
        Zeigt nur den Klassennamen und ob Daten geladen sind; vermeidet große Ausgabe
        (kein Dump des gesamten xarray Datasets). So kann man in Logs schnell prüfen,
        ob ein Container bereits initialisiert/befüllt wurde.
        Format: ClassName(has_data=True|False)
        '''
        return f"{self.__class__.__name__}(has_data={self._data is not None})"
```

### Integration mit StudyObject: Beispiel

So kommen Technik-Daten aus dem hierarchischen `StudyObject` in eine Daten-Klasse:

```python
from echem_data_tool.study.core import StudyObject
from echem_data_tool.data.data_classes_fn import CyclicVoltammetry

# 1) Hierarchie aufbauen und Rohdaten ablegen
study = StudyObject()
cell = study.add_cell("cell_001")
tech = cell.add_technique("technique_001_CV")
tech.data.add_variable("time", [0.0, 1.0, 2.0], attributes={"units": "s"})
tech.data.add_variable("potential", [3.0, 3.5, 3.2], attributes={"units": "V"})
tech.data.add_variable("current", [0.0, 0.1, -0.05], attributes={"units": "A"})

# 2) Technik-Dataset erzeugen (kompakt, ohne Flattening über Zellen/Groups)
ds_cv = tech.to_xarray_group()

# 3) In Daten-Klasse laden
cv = CyclicVoltammetry()
cv.load_from_technique_dataset(ds_cv)

# cv.data ist nun ein xr.Dataset mit den required_variables
```

### TimeSeriesData (abstrakt)

Basisklasse für zeitbasierte Techniken.

Contract (Kurzfassung)
- Erwartet mindestens eine Variable `time` (als data_var)
- Bietet Utilities für Zeitausschnitte und Zeitmetriken

```python
class TimeSeriesData(BaseData):
    required_variables = ("time",)

    def get_time_slice(self, start_time: float, end_time: float) -> xr.Dataset:
        """
        Liefert einen Zeitausschnitt des Datasets.

        Args:
            start_time: Startzeit (gleiche Einheit/Skala wie `time` im Dataset, typ. Sekunden)
            end_time: Endzeit

        Returns:
            xr.Dataset: Subset mit `time` im Intervall [start_time, end_time].

        Raises:
            ValueError: Wenn keine Daten geladen sind (vom .data-Property).
        """
        return self.data.sel(time=slice(start_time, end_time))

    @property
    def time_range(self) -> tuple[float, float]:
        """
        Minimale und maximale Zeit.

        Returns:
            tuple[float, float]: (t_min, t_max). Bei fehlenden Daten: (0.0, 0.0).

        Note:
            Erwartet, dass `time` indexierbar und sortiert ist (nicht erzwungen).
        """
        if self._data is None:
            return (0.0, 0.0)
        times = self._data["time"].values
        return (float(times[0]), float(times[-1]))

    @property
    def duration(self) -> float:
        """
        Gesamtdauer der Messung in Zeiteinheiten des Datasets (typ. Sekunden).

        Returns:
            float: t_max - t_min (nicht negativ, falls Zeit monoton).
        """
        t0, t1 = self.time_range
        return t1 - t0
```

### CyclicVoltammetry

```python
class CyclicVoltammetry(TimeSeriesData):
    """Container für CV-Rohdaten: time [s], potential [V], current [A]."""

    technique_type = "cyclic_voltammetry"
    required_variables = ("time", "potential", "current")

    def __init__(self, data: Optional[xr.Dataset] = None, cv_parameters: Optional["CVParameters"] = None):
        """Optionaler Parameter-Input `cv_parameters` beschreibt Geräte-Setup.

        Args:
            data: Rohdaten-Dataset (time, potential, current).
            cv_parameters: Optionales Objekt mit Mess-/Akquiseparametern (Scanrate, Spannungsgrenzen, usw.).
        """
        super().__init__(data)
        self.cv_parameters = cv_parameters  # kann None sein wenn Loader Parameter nicht extrahiert
```

#### Empfohlene Parameter und Variablen

- required_variables (Dataset):
    - time [s], potential [V], current [A]
- Minimal-Parameter (CVParameters):
    - scan_rate_v_s, potential_min_v, potential_max_v, num_cycles
- Optionale Parameter:
    - initial_potential_v, step_size_v, scan_mode, sampling_mode, sampling_interval_s, vertex_hold_time_s
- Gehört NICHT in CVParameters (sondern in Cell-/Elektroden-Metadaten):
    - electrode_area_cm2, active_mass_mg, loading_mg_cm2, nominal_capacity_mAh

### GalvanostaticCycling

```python
class GalvanostaticCycling(TimeSeriesData):
    """Container für GC-Rohdaten: time [s], potential [V], current [A]."""

    technique_type = "galvanostatic_cycling"
    required_variables = ("time", "potential", "current")

    def __init__(self, data: Optional[xr.Dataset] = None, gc_parameters: Optional["GCParameters"] = None):
        """Optionaler Parameter-Input `gc_parameters` beschreibt Strom-/Spannungs-Setup.

        Args:
            data: Rohdaten-Dataset (time, potential, current).
            gc_parameters: Optionales Objekt mit Lade/Entlade-Strom, Spannungsfenster, Zyklenzahl, usw.
        """
        super().__init__(data)
        self.gc_parameters = gc_parameters  # None erlaubt (z. B. manuell nachreichbar)
```

#### Empfohlene Parameter und Variablen

- required_variables (Dataset):
    - time [s], potential [V], current [A]
- Minimal-Parameter (GCParameters):
    - current_charge_a, current_discharge_a, voltage_min_v, voltage_max_v, num_cycles
- Optionale Parameter:
    - rest_time_s, sampling_interval_s, sampling_mode
- Gehört NICHT in GCParameters:
    - electrode_area_cm2, active_mass_mg, loading_mg_cm2 (→ Cell-/Elektroden-Metadaten)

### ConstantCurrentConstantVoltage (CCCV)

```python
class ConstantCurrentConstantVoltage(TimeSeriesData):
    """CCCV: CC bis Spannungsgrenze, dann CV bis Stromgrenze."""

    technique_type = "cccv"
    required_variables = ("time", "potential", "current")

    def __init__(self, data: Optional[xr.Dataset] = None, cccv_parameters: Optional["CCCVParameters"] = None):
        """Optionaler Parameter-Input `cccv_parameters` für CC/CV-Konfiguration.

        Args:
            data: Rohdaten-Dataset (time, potential, current).
            cccv_parameters: Optionales Objekt (CC-Strom, CV-Grenzstrom, Spannungsgrenzen, usw.).
        """
        super().__init__(data)
        self.cccv_parameters = cccv_parameters  # None erlaubt

    def get_phase_data(self, phase: str, direction: Optional[str] = None) -> xr.Dataset:
        """
        Filtert Daten für eine bestimmte CCCV-Phase.

        Args:
            phase: "CC" oder "CV" (Groß-/Kleinschreibung wird ignoriert)
            direction: Optional "charge" oder "discharge". Wenn None, werden beide Richtungen gewählt.

        Returns:
            xr.Dataset: Subset mit Zeilen/Zeiten, die zur gewünschten Phase (und ggf. Richtung) gehören.

        Preconditions:
            - `self.data` ist gesetzt
            - Variable `phase` ist im Dataset als data_var vorhanden (z. B. "CC_charge", "CV_discharge").

        Behavior:
            - Ohne direction: filtert alle Zeilen, deren `phase` den gewünschten Phasenstring enthält.
            - Mit direction: versucht exakten Match (z. B. "CC_charge"); wenn keiner vorhanden,
              fällt auf Vorzeichen des Stroms zurück (>0 Laden, <0 Entladen) unter Beachtung der Phase.

        Raises:
            ValueError: Wenn keine Daten geladen wurden oder die Variable `phase` fehlt.
        """
        if self._data is None:
            raise ValueError("Keine Daten geladen")
        if "phase" not in self.variables:
            raise ValueError("'phase' nicht vorhanden – per Instrument/Loader bereitstellen oder via Analyzer ableiten")

        phase_da = self._data["phase"].astype(str)
        if direction is None:
            mask = phase_da.str.contains(phase, case=False)
            return self._data.where(mask, drop=True)

        target = f"{phase}_{direction}"
        mask = phase_da.str.contains(target, case=False)
        if not bool(mask.any()):
            # Fallback: Richtung über Stromvorzeichen
            phase_mask = phase_da.str.contains(phase, case=False)
            dir_mask = (self._data["current"] > 0) if direction == "charge" else (self._data["current"] < 0)
            mask = phase_mask & dir_mask
        return self._data.where(mask, drop=True)

    @property
    def has_phase_info(self) -> bool:
        return "phase" in self.variables if self._data else False
```

#### Empfohlene Parameter und Variablen

- required_variables (Dataset):
    - time [s], potential [V], current [A] (+ optional phase als data_var)
- Minimal-Parameter (CCCVParameters):
    - current_charge_a, current_discharge_a, voltage_charge_max_v, voltage_discharge_min_v, cutoff_current_a, num_cycles
- Optionale Parameter:
    - rest_time_s, hold_time_s, sampling_interval_s, sampling_mode, phase_flag_source
- Hinweise:
    - Wenn das Instrument keine Phase liefert, kann `phase` in Analyzern abgeleitet werden; `phase_flag_source` dokumentiert die Herkunft.

### ElectrochemicalImpedanceSpectroscopy (EIS)

```python
class ElectrochemicalImpedanceSpectroscopy(BaseData):
    technique_type = "eis"
    required_variables = ("frequency", "z_real", "z_imag")

    def __init__(self, data: Optional[xr.Dataset] = None, eis_parameters: Optional["EISParameters"] = None):
        """Optionaler Parameter-Input `eis_parameters` für AC-Sweep-Setup.

        Args:
            data: Rohdaten-Dataset (frequency, z_real, z_imag).
            eis_parameters: Optionales Objekt mit Frequenzbereich, Punkte/Decade, Amplitude, Bias.
        """
        super().__init__(data)
        self.eis_parameters = eis_parameters  # None erlaubt

    @property
    def z_magnitude(self) -> np.ndarray:
        """
        Betrag der Impedanz |Z| = sqrt(Re(Z)^2 + Im(Z)^2).

        Returns:
            np.ndarray: Array gleicher Länge wie z_real/z_imag.

        Raises:
            ValueError: Wenn keine Daten geladen sind.
        """
        if self._data is None:
            raise ValueError("Keine Daten")
        return np.sqrt(self._data["z_real"] ** 2 + self._data["z_imag"] ** 2).values

    @property
    def z_phase(self) -> np.ndarray:
        """
        Phase der Impedanz φ in Grad.

        Returns:
            np.ndarray: Winkel in Grad, gleiche Länge wie z_real/z_imag.

        Raises:
            ValueError: Wenn keine Daten geladen sind.
        """
        if self._data is None:
            raise ValueError("Keine Daten")
        return (np.arctan2(self._data["z_imag"], self._data["z_real"]) * 180 / np.pi).values

    @property
    def frequency_range(self) -> tuple[float, float]:
        """
        Frequenzbereich.

        Returns:
            tuple[float, float]: (f_min, f_max). Bei fehlenden Daten (0.0, 0.0).
        """
        if self._data is None:
            return (0.0, 0.0)
        f = self._data["frequency"].values
        return (float(f.min()), float(f.max()))
```

#### Empfohlene Parameter und Variablen

- required_variables (Dataset):
    - frequency [Hz], z_real [Ohm], z_imag [Ohm]
- Minimal-Parameter (EISParameters):
    - frequency_min_hz, frequency_max_hz, points_per_decade, sweep_type, amplitude, amplitude_unit
- Optionale Parameter:
    - dc_bias_type, dc_potential_v, dc_current_a, temperature_c
- Gehört NICHT in EISParameters:
    - electrode_area_cm2 (→ zur Flächen-normalisierten Impedanz im Analyzer, Metadaten-Ebene)

## Parameter-Klassen (experimentell)

Parameter spiegeln Geräteeinstellungen/Setups wider (keine Analyse-Parameter) und sind optional. Alternativ können Parameter in `TechniqueMetadata.settings` abgelegt werden. Zell-/Elektroden-Metadaten (z. B. Fläche, Masse) gehören nicht in diese Parameter-Klassen.

```python
from dataclasses import dataclass
from typing import Optional


@dataclass
class CVParameters:
        # Minimal
        scan_rate_v_s: float        # V/s
        potential_min_v: float      # V
        potential_max_v: float      # V
        num_cycles: int
        # Optional
        initial_potential_v: Optional[float] = None  # V
        step_size_v: Optional[float] = None          # V (bei staircase)
        scan_mode: Optional[str] = None              # "linear" | "staircase"
        sampling_mode: Optional[str] = None          # "time" | "potential"
        sampling_interval_s: Optional[float] = None  # s (bei sampling_mode="time")
        vertex_hold_time_s: Optional[float] = None   # s


@dataclass
class GCParameters:
        # Minimal
        current_charge_a: float   # A
        current_discharge_a: float  # A
        voltage_min_v: float      # V
        voltage_max_v: float      # V
        num_cycles: int
        # Optional
        rest_time_s: float = 0.0                 # s
        sampling_mode: Optional[str] = None      # "time" | "event"
        sampling_interval_s: Optional[float] = None  # s


@dataclass
class CCCVParameters:
        # Minimal
        current_charge_a: float         # A
        current_discharge_a: float      # A
        voltage_charge_max_v: float     # V
        voltage_discharge_min_v: float  # V
        cutoff_current_a: float         # A (CV-Abbruch)
        num_cycles: int
        # Optional
        rest_time_s: float = 0.0
        hold_time_s: Optional[float] = None            # s (max. CV-Haltedauer)
        sampling_mode: Optional[str] = None            # "time" | "event"
        sampling_interval_s: Optional[float] = None    # s
        phase_flag_source: Optional[str] = None        # "instrument" | "derived"


@dataclass
class EISParameters:
        # Minimal
        frequency_min_hz: float
        frequency_max_hz: float
        points_per_decade: int
        sweep_type: str                 # "log" | "linear"
        amplitude: float
        amplitude_unit: str             # "V" | "A"
        # Optional
        dc_bias_type: Optional[str] = None  # "potential" | "current"
        dc_potential_v: Optional[float] = None
        dc_current_a: Optional[float] = None
        temperature_c: Optional[float] = None
```

## Platzierung von Parametern und Metadaten

- Dataset (Data-Klassen, required_variables):
    - Rohmessgrößen: time, potential, current, phase, frequency, z_real, z_imag, …
- Technique Parameters (oben definierte Parameter-Klassen oder TechniqueMetadata.settings):
    - Geräteeinstellungen der Messung: Scanrate, Spannungsgrenzen, Strom, Frequenzbereich, Amplitude, Sampling, …
- Cell-/Elektroden-Metadaten (StudyObject/CellMetadata):
    - electrode_area_cm2, active_mass_mg, loading_mg_cm2, nominal_capacity_mAh, temperature_c_environment, separator, electrolyte, …
- Analyzer-Ausgaben (nicht in Dataset/Parametern fest verdrahten):
    - z. B. Kapazitäten, Coulombic Efficiency, Peak-Positionen, Fit-Parameter, Zyklen-Labels

## Auxiliary-Daten (Hinweis)

Hilfsdaten (z. B. Temperatur, Druck) werden separat verwaltet und bei Bedarf mit Messdaten kombiniert:

- Heute: `StudyObject` bietet `Auxiliary`-Gruppen mit xarray-Variablen.
- Später optional: separates `AuxiliaryData` mit `.interpolate_to(time)` als Komfortschicht.

Beispiel für Interpolation in einem Analyzer:

```python
def align_auxiliary_to_measurement(meas: BaseData, aux_ds: xr.Dataset) -> xr.Dataset:
    return aux_ds.interp(time=meas.data["time"], method="linear")
```

## Analyzer-Interaktion (Kurz)

- Analyzer konsumieren die `.data`-Datasets der Data-Klassen (xarray-first).
- Inhaltliche Prüfungen (NaN/Inf, Mindestlängen, physikalische Plausibilität) sind Aufgabe der Analyzer.
- Beispiel-Skizze:

```python
class CapacityAnalyzer:
    def analyze(self, gc: GalvanostaticCycling) -> dict:
        ds = gc.data
        if ds.sizes.get("time", 0) < 10:
            raise ValueError("Zu wenig Datenpunkte")
        if np.any(np.isnan(ds["current"])):
            # Hinweis statt Abbruch, je nach Policy
            pass
        # … Berechnung hier …
        return {"n": int(ds.sizes.get("time", 0))}
```

## Migrationsnotizen

- Kurzfristig kann StudyObject weiterhin das primäre I/O bleiben; Data-Klassen dienen als klar definierte, xarray-basierte Fassade für Analyzer.
- Bei Bedarf Adapter-Funktionen vorsehen, um Daten aus `StudyObject`/`DataGroup` in `xr.Dataset` zu extrahieren und an Data-Klassen zu übergeben.



