# Design: Elektrochemische Daten-Klassen

## Inhaltsverzeichnis

1. [Übersicht & Architektur](#übersicht--architektur)
2. [Design-Prinzipien](#design-prinzipien)
3. [Klassendefinitionen](#klassendefinitionen)
   - [BaseData](#basedata-abstrakt)
   - [TimeSeriesData](#timeseriesdata-abstrakt)
   - [CyclicVoltammetry](#cyclicvoltammetry)
   - [GalvanostaticCycling](#galvanostaticcycling)
   - [ConstantCurrentConstantVoltage](#constantcurrentconstantvoltage)
   - [ElectrochemicalImpedanceSpectroscopy](#electrochemicalimpedancespectroscopy)
4. [Parameter-Klassen](#parameter-klassen)
5. [Analyzer-Beispiele](#analyzer-beispiele)

---

## Übersicht & Architektur

**KERNKONZEPT: Trennung von Daten und Analyse!**

```
┌──────────────────┐
│ FileLoader       │  Liest Dateien (MPR, CSV, ...)
└────────┬─────────┘
         │ StudyObject (data + meta)
         ▼
┌──────────────────┐
│ Data Classes     │  Datencontainer + Validierung
│ (CV, EIS, GC)    │  • Definiert required_variables
│                  │  • Lädt und validiert Daten
└────────┬─────────┘  • Stellt Daten bereit
         │ .data (xarray)
         ▼
┌──────────────────┐
│ Analysis         │  Algorithmen & Berechnungen
│ Modules          │  • PeakAnalyzer
│ (extern!)        │  • CapacityAnalyzer
└──────────────────┘  • ImpedanceFitter
```

### Aufgaben der Daten-Klassen

**✅ Daten-Klassen sind zuständig für:**
- Struktur-Vorgabe für FileLoader (`required_variables`)
- Daten laden und validieren  
- Daten zugänglich machen (`.data` Property)
- Export-Funktionen (netCDF, pandas)
- Einfache Utility-Methoden (z.B. Zeit-Slicing)

**❌ Daten-Klassen sind NICHT zuständig für:**
- Daten analysieren
- Preprocessing/Smoothing
- Plotting
- Peak-Detektion, Fit-Algorithmen
- Zyklen-Erkennung
- Kapazitäts-Berechnung

→ Diese Funktionen werden in **separaten Analyzer-Modulen** implementiert!

---

## Design-Prinzipien

### 1. Trennung von Daten und Analyse

**Warum?**

1. **Modularität**: Neue Analysen ohne Core-Code zu ändern
2. **Entwickler-Freundlichkeit**: Andere können eigene Analyzer hinzufügen
3. **Wartbarkeit**: Analyse-Bugs betreffen keine Datenstrukturen
4. **Wiederverwendbarkeit**: Ein Analyzer für mehrere Techniken
5. **Klarheit**: Data Class = "Was sind die Daten?", Analyzer = "Wie analysiere ich sie?"

### 2. Nur Rohdaten in Daten-Klassen

**Was sind Rohdaten?**

✅ **Rohdaten (gehören in Daten-Klassen):**
- Direkt vom Instrument gemessene Werte
- Zeit, Spannung, Strom
- Instrument-gesetzte Flags (z.B. `phase` bei CCCV)
- Frequenz, Impedanz (Real/Imaginärteil)

❌ **KEINE berechneten Werte (gehören in Analyzer):**
- Capacity (aus Strom integriert)
- Cycle-Nummern (aus Daten erkannt)
- Spezifische Kapazität (normalisiert)
- Coulombic Efficiency (Verhältnis berechnet)
- Peak-Positionen, Fit-Parameter

**Warum nur Rohdaten?**

1. ✅ **Unabhängig**: Funktioniert mit Daten von allen Instrumenten
2. ✅ **Reproduzierbar**: Analyse-Methode ist dokumentiert und versioniert
3. ✅ **Flexibel**: Verschiedene Berechnungsmethoden möglich
4. ✅ **Transparent**: User versteht was passiert
5. ✅ **Validierbar**: Ergebnisse können verglichen werden

**Ausnahme: Simple Properties sind OK**

Einfache mathematische Formeln als Properties erlaubt:

```python
@property
def z_magnitude(self) -> np.ndarray:
    """Berechnet |Z| = sqrt(Re² + Im²)."""
    return np.sqrt(self._data["z_real"]**2 + self._data["z_imag"]**2).values
```

Warum OK? Triviale Formel, keine Interpretation, keine Parameter nötig.

### 3. Nur required_variables - Auxiliary Data separat

**Kern-Prinzip:** Daten-Klassen enthalten nur **essenzielle Messdaten**.

```python
# ✅ Nur Kerndaten vom Potentiostat
class CyclicVoltammetry:
    required_variables = ("time", "potential", "current")
    # KEINE optional_variables!
```

**Hilfsdaten (Temperatur, Druck, etc.) gehören in separates Auxiliary Data System:**

```
┌──────────────────┐
│ Data Classes     │  NUR Kerndaten (time, V, I, ...)
│ (CV, EIS, GC)    │  required_variables
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ AuxiliaryData    │  Externe Daten (T, p, RH, ...)
│ (optional!)      │  • Eigene Zeitachse
│                  │  • Verschiedene Quellen
└────────┬─────────┘  • Flexibles Format
         │
         ▼
┌──────────────────┐
│ Analyzer         │  Kombiniert bei Bedarf
│                  │  analyze(cv, auxiliary=temp_data)
└──────────────────┘
```

**Vorteile:**

1. ✅ **Klare Trennung**: Messdaten ≠ Hilfsdaten
2. ✅ **Flexibilität**: Verschiedene Quellen für Auxiliary
3. ✅ **Keine Warnungen**: Wenn Hilfsdaten fehlen
4. ✅ **Wiederverwendbarkeit**: Ein Auxiliary für mehrere Messungen
5. ✅ **Unabhängige Zeitachsen**: Analyzer interpoliert bei Bedarf

**Siehe [Auxiliary Data Beispiel](#auxiliary-data-system) für Details.**

### 4. Validierung nur für Struktur

**Daten-Klasse prüft nur Struktur:**
```python
# ✅ Sind die richtigen Spalten/Variablen da?
required_variables = ("time", "potential", "current")

# Daten-Klasse prüft NICHT:
# - Ob Werte sinnvoll sind (NaN, Ausreißer, ...)
# - Ob genug Datenpunkte vorhanden sind
# - Ob Zyklen vollständig sind
# → Das ist Aufgabe der Analyzer!
```

**Analyzer prüft Inhalt:**
```python
class CapacityAnalyzer:
    def analyze(self, gc):
        # Prüft Datenqualität
        if len(gc.data.time) < 10:
            raise ValueError("Zu wenig Datenpunkte")
        
        if np.any(np.isnan(gc.data.current)):
            warnings.warn("NaN-Werte gefunden")
```

---

## Klassendefinitionen

### BaseData (Abstrakt)

Abstrakte Basisklasse für alle elektrochemischen Daten-Klassen.

```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import xarray as xr
import pandas as pd
import numpy as np


class BaseData(ABC):
    """
    Abstrakte Basisklasse für elektrochemische Datencontainer.
    
    Vererbungshierarchie:
    BaseData (abstrakt)
    ├── TimeSeriesData (abstrakt) - für zeitbasierte Daten
    │   ├── CyclicVoltammetry
    │   ├── GalvanostaticCycling
    │   ├── ConstantCurrentConstantVoltage
    │   └── ...
    └── ElectrochemicalImpedanceSpectroscopy - frequenzbasiert
    """
    
    # Klassen-Attribute - MÜSSEN in Unterklassen gesetzt werden
    technique_type: str = "base"
    required_variables: tuple[str, ...] = ()
    
    def __init__(self, data: Optional[xr.Dataset] = None):
        """
        Args:
            data: Optional xarray Dataset mit Messdaten
        """
        self._data: Optional[xr.Dataset] = data
    
    # ========== Daten-Management ==========
    
    def load_from_study_object(self, study_object) -> None:
        """
        Lädt Daten aus StudyObject (von FileLoader erstellt).
        
        Args:
            study_object: StudyObject mit .data und .meta Attributen
        
        Raises:
            ValueError: Wenn required_variables fehlen
        """
        self._data = study_object.data
        self._validate_data()
    
    def _validate_data(self) -> None:
        """
        Validiert Datenstruktur: Sind alle required_variables vorhanden?
        
        WICHTIG: Prüft NUR Struktur, NICHT Inhalt!
        - ✅ Prüft: Sind Spalten/Variablen vorhanden?
        - ❌ Prüft NICHT: NaN-Werte, Ausreißer, Vollständigkeit
          → Das ist Aufgabe der Analyzer!
        """
        if self._data is None:
            return
        
        # Required variables MÜSSEN vorhanden sein
        missing = set(self.required_variables) - set(self._data.data_vars)
        if missing:
            raise ValueError(
                f"Fehlende PFLICHT-Variablen für {self.technique_type}: {missing}\n"
                f"FileLoader muss diese Variablen bereitstellen!"
            )
    
    # ========== Daten-Zugriff ==========
    
    @property
    def data(self) -> xr.Dataset:
        """
        Gibt Rohdaten zurück (für Analyzer-Zugriff).
        
        Returns:
            xarray Dataset mit Messdaten
        
        Raises:
            ValueError: Wenn keine Daten geladen
        """
        if self._data is None:
            raise ValueError("Keine Daten geladen")
        return self._data
    
    @property
    def shape(self) -> dict[str, int]:
        """Gibt Dimensionen zurück, z.B. {"time": 1000}"""
        return dict(self._data.dims) if self._data else {}
    
    @property
    def variables(self) -> list[str]:
        """Gibt Liste der Variablen zurück."""
        return list(self._data.data_vars) if self._data else []
    
    # ========== Export ==========
    
    def to_dataframe(self) -> pd.DataFrame:
        """Konvertiert zu pandas DataFrame."""
        if self._data is None:
            raise ValueError("Keine Daten verfügbar")
        return self._data.to_dataframe().reset_index()
    
    def to_netcdf(self, path: Path) -> None:
        """Speichert als netCDF."""
        if self._data is None:
            raise ValueError("Keine Daten zum Speichern")
        
        data_to_save = self._data.assign_attrs({"technique_type": self.technique_type})
        data_to_save.to_netcdf(path, engine="h5netcdf")
    
    # ========== Utility ==========
    
    def summary(self) -> str:
        """Gibt Daten-Zusammenfassung zurück."""
        if self._data is None:
            return f"{self.technique_type}: Keine Daten geladen"
        
        return (
            f"Technik: {self.technique_type}\n"
            f"Dimensionen: {self.shape}\n"
            f"Variablen: {self.variables}"
        )
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(has_data={self._data is not None})"
```

---

### TimeSeriesData (Abstrakt)

Basisklasse für zeitbasierte Techniken.

```python
class TimeSeriesData(BaseData):
    """
    Basisklasse für zeitbasierte Techniken (CV, GC, CA, CP, ...).
    
    Erweitert BaseData um Zeit-spezifische Utility-Methoden.
    """
    
    required_variables = ("time",)
    
    def get_time_slice(self, start_time: float, end_time: float) -> xr.Dataset:
        """
        Extrahiert Zeitausschnitt.
        
        Args:
            start_time: Startzeit (UTS oder relative Sekunden)
            end_time: Endzeit (UTS oder relative Sekunden)
        
        Returns:
            Dataset mit ausgeschnittenem Zeitbereich
        """
        return self._data.sel(time=slice(start_time, end_time))
    
    @property
    def time_range(self) -> tuple[float, float]:
        """Gibt (min_time, max_time) zurück."""
        if self._data is None:
            return (0.0, 0.0)
        times = self._data.time.values
        return (float(times[0]), float(times[-1]))
    
    @property
    def duration(self) -> float:
        """Gibt Gesamt-Messdauer in Sekunden zurück."""
        t_min, t_max = self.time_range
        return t_max - t_min
```

---

### CyclicVoltammetry

```python
class CyclicVoltammetry(TimeSeriesData):
    """
    Cyclic Voltammetry Datencontainer.
    
    Required Variables:
        - time (s)
        - potential (V)
        - current (A)
    
    Verwendung:
        >>> cv = CyclicVoltammetry()
        >>> cv.load_from_study_object(study_obj)
        >>> print(cv.summary())
    """
    
    technique_type = "cyclic_voltammetry"
    required_variables = ("time", "potential", "current")
    
    def __init__(
        self, 
        data: Optional[xr.Dataset] = None,
        cv_parameters: Optional["CVParameters"] = None
    ):
        super().__init__(data)
        self.cv_parameters = cv_parameters
```

---

### GalvanostaticCycling

```python
class GalvanostaticCycling(TimeSeriesData):
    """
    Galvanostatic Cycling Datencontainer.
    
    Required Variables:
        - time (s)
        - potential (V)
        - current (A)
    
    WICHTIG: Capacity ist NICHT in required_variables!
    → Wird von Analyzer berechnet (siehe Analyzer-Beispiele)
    
    Verwendung:
        >>> gc = GalvanostaticCycling()
        >>> gc.load_from_study_object(study_obj)
    """
    
    technique_type = "galvanostatic_cycling"
    required_variables = ("time", "potential", "current")
    
    def __init__(
        self,
        data: Optional[xr.Dataset] = None,
        gc_parameters: Optional["GCParameters"] = None
    ):
        super().__init__(data)
        self.gc_parameters = gc_parameters
```

---

### ConstantCurrentConstantVoltage

```python
class ConstantCurrentConstantVoltage(TimeSeriesData):
    """
    Constant Current Constant Voltage (CCCV) Datencontainer.
    
    Typisch für Lithium-Ionen Batterien:
    - CC-Phase: Konstanter Strom bis Spannungsgrenze
    - CV-Phase: Konstante Spannung bis Stromgrenze
    
    Required Variables:
        - time (s)
        - potential (V)
        - current (A)
    
    HINWEIS zu phase:
    - phase ist KEIN required_variables (optional)
    - Wenn vorhanden: vom Instrument gesetzt (Rohdaten)
    - Wenn nicht: CCCVPhaseDetector kann phase rekonstruieren
    
    WICHTIG: 
    - capacity ist NICHT in required_variables (wird von Analyzer berechnet)
    - Wenn phase fehlt: get_phase_data() wirft hilfreichen Fehler
    
    Verwendung:
        >>> cccv = ConstantCurrentConstantVoltage()
        >>> cccv.load_from_study_object(study_obj)
        >>> 
        >>> # Wenn phase vorhanden:
        >>> if cccv.has_phase_info:
        >>>     cc_data = cccv.get_phase_data("CC", direction="charge")
        >>> 
        >>> # Wenn phase fehlt - Analyzer nutzen:
        >>> from echem_data_tool.analysis.cccv import CCCVPhaseDetector
        >>> detector = CCCVPhaseDetector()
        >>> cccv_with_phase = detector.add_phase_variable(cccv)
    """
    
    technique_type = "cccv"
    required_variables = ("time", "potential", "current")
    
    def __init__(
        self,
        data: Optional[xr.Dataset] = None,
        cccv_parameters: Optional["CCCVParameters"] = None
    ):
        super().__init__(data)
        self.cccv_parameters = cccv_parameters
    
    # ========== Utility-Methoden ==========
    
    def get_phase_data(
        self, 
        phase: str, 
        direction: Optional[str] = None
    ) -> xr.Dataset:
        """
        Extrahiert Daten einer bestimmten Phase.
        
        Args:
            phase: "CC" oder "CV"
            direction: Optional "charge" oder "discharge"
        
        Returns:
            Dataset nur mit Daten dieser Phase
        
        Raises:
            ValueError: Wenn phase-Variable nicht vorhanden
        
        Beispiele:
            # Alle CC-Phasen:
            cc_all = cccv.get_phase_data("CC")
            
            # Nur CC beim Laden:
            cc_charge = cccv.get_phase_data("CC", direction="charge")
        """
        if self._data is None:
            raise ValueError("Keine Daten geladen")
        
        if "phase" not in self.variables:
            raise ValueError(
                "Variable 'phase' ist nicht vorhanden!\n\n"
                "Optionen:\n"
                "1. FileLoader konnte 'phase' nicht extrahieren (nicht in Rohdaten)\n"
                "2. Nutze CCCVPhaseDetector um Phasen zu erkennen:\n\n"
                "   from echem_data_tool.analysis.cccv import CCCVPhaseDetector\n"
                "   detector = CCCVPhaseDetector()\n"
                "   cccv_with_phase = detector.add_phase_variable(cccv)\n"
                "   cc_data = cccv_with_phase.get_phase_data('CC')"
            )
        
        phase_data = self._data["phase"]
        
        if direction is None:
            mask = phase_data.astype(str).str.contains(phase, case=False)
            return self._data.where(mask, drop=True)
        
        # Spezifische Phase + Richtung
        target = f"{phase}_{direction}"
        mask = phase_data.astype(str).str.contains(target, case=False)
        
        # Fallback: Stromrichtung nutzen
        if not mask.any():
            phase_mask = phase_data.astype(str).str.contains(phase, case=False)
            if direction == "charge":
                direction_mask = self._data["current"] > 0
            else:
                direction_mask = self._data["current"] < 0
            mask = phase_mask & direction_mask
        
        return self._data.where(mask, drop=True)
    
    @property
    def has_phase_info(self) -> bool:
        """Prüft ob phase-Variable vorhanden ist."""
        return "phase" in self.variables if self._data else False
    
    @property
    def has_cv_phase(self) -> bool:
        """
        Prüft ob CV-Phasen in Daten vorhanden sind.
        
        Raises:
            ValueError: Wenn phase-Variable nicht vorhanden
        """
        if not self.has_phase_info:
            raise ValueError("Keine phase-Variable. Nutze has_phase_info zum Prüfen.")
        
        phases = self._data["phase"].values
        return "cv" in str(phases).lower()
```

---

### ElectrochemicalImpedanceSpectroscopy

```python
class ElectrochemicalImpedanceSpectroscopy(BaseData):
    """
    Electrochemical Impedance Spectroscopy Datencontainer.
    
    NICHT von TimeSeriesData (frequenz-basiert)!
    
    Required Variables:
        - frequency (Hz)
        - z_real (Ω) - Realteil der Impedanz
        - z_imag (Ω) - Imaginärteil der Impedanz
    
    Verwendung:
        >>> eis = ElectrochemicalImpedanceSpectroscopy()
        >>> eis.load_from_study_object(study_obj)
        >>> 
        >>> # Simple Properties:
        >>> z_mag = eis.z_magnitude
        >>> z_phase = eis.z_phase
    """
    
    technique_type = "eis"
    required_variables = ("frequency", "z_real", "z_imag")
    
    def __init__(
        self,
        data: Optional[xr.Dataset] = None,
        eis_parameters: Optional["EISParameters"] = None
    ):
        super().__init__(data)
        self.eis_parameters = eis_parameters
    
    # ========== Simple Properties (OK!) ==========
    
    @property
    def z_magnitude(self) -> np.ndarray:
        """Berechnet |Z| = sqrt(Re² + Im²)."""
        if self._data is None:
            raise ValueError("Keine Daten")
        return np.sqrt(
            self._data["z_real"]**2 + self._data["z_imag"]**2
        ).values
    
    @property
    def z_phase(self) -> np.ndarray:
        """Berechnet Phase φ in Grad."""
        if self._data is None:
            raise ValueError("Keine Daten")
        return (
            np.arctan2(self._data["z_imag"], self._data["z_real"]) * 180 / np.pi
        ).values
    
    @property
    def frequency_range(self) -> tuple[float, float]:
        """Gibt (f_min, f_max) zurück."""
        if self._data is None:
            return (0.0, 0.0)
        freqs = self._data.frequency.values
        return (float(freqs.min()), float(freqs.max()))
```

---

## Parameter-Klassen

Experimentelle Parameter (Setup-Informationen, KEINE Analyse-Parameter).

```python
from dataclasses import dataclass
from typing import Optional


@dataclass
class CVParameters:
    """Experimentelle Parameter für Cyclic Voltammetry."""
    scan_rate: float  # V/s
    potential_min: float  # V
    potential_max: float  # V  
    num_cycles: int
    initial_potential: float  # V
    step_size: Optional[float] = None  # V


@dataclass
class GCParameters:
    """Experimentelle Parameter für Galvanostatic Cycling."""
    current_charge: float  # A
    current_discharge: float  # A
    voltage_min: float  # V
    voltage_max: float  # V
    num_cycles: int
    rest_time: float = 0.0  # s


@dataclass
class CCCVParameters:
    """Experimentelle Parameter für CCCV."""
    current_charge: float  # A (CC-Phase)
    current_discharge: float  # A (CC-Phase)
    voltage_charge_max: float  # V (Wechsel zu CV)
    voltage_discharge_min: float  # V (Wechsel zu CV)
    cutoff_current: float  # A (Ende CV-Phase)
    num_cycles: int
    rest_time: float = 0.0  # s


@dataclass
class EISParameters:
    """Experimentelle Parameter für EIS."""
    frequency_min: float  # Hz
    frequency_max: float  # Hz
    points_per_decade: int
    amplitude: float  # V oder A
    dc_potential: Optional[float] = None  # V
    dc_current: Optional[float] = None  # A
```

---

## Auxiliary Data System

Hilfsdaten (Temperatur, Druck, Luftfeuchtigkeit, etc.) werden **separat** von den Messdaten verwaltet.

### Warum separat?

1. ✅ **Verschiedene Quellen**: Temperatur von externem Logger, nicht vom Potentiostat
2. ✅ **Verschiedene Zeitachsen**: T-Logger mit 1 Hz, CV mit 1000 Hz
3. ✅ **Wiederverwendbarkeit**: Ein T-Datensatz für mehrere CV-Messungen
4. ✅ **Flexibilität**: Analyzer entscheidet ob/wie Auxiliary genutzt wird
5. ✅ **Keine Warnungen**: Messdaten laden ohne "temperature fehlt"-Warnung

### AuxiliaryData Klasse

```python
# ========== Auxiliary Data System ==========
# Datei: echem_data_tool/auxiliary.py

import xarray as xr
import numpy as np
from pathlib import Path
from typing import Optional


class AuxiliaryData:
    """
    Container für Hilfsdaten (Temperatur, Druck, etc.).
    
    Unabhängig von Daten-Klassen - kann mit beliebigen
    Messungen kombiniert werden.
    """
    
    def __init__(self, data: xr.Dataset):
        """
        Args:
            data: xarray Dataset mit Hilfsdaten
                  Muss mindestens 'time' Koordinate haben
        """
        if "time" not in data.coords:
            raise ValueError("AuxiliaryData benötigt 'time' Koordinate")
        
        self._data = data
    
    @classmethod
    def from_csv(
        cls, 
        path: Path, 
        time_column: str = "time"
    ) -> "AuxiliaryData":
        """Lädt Auxiliary Data aus CSV."""
        import pandas as pd
        df = pd.read_csv(path)
        
        # Konvertiere zu xarray
        ds = xr.Dataset.from_dataframe(df.set_index(time_column))
        return cls(ds)
    
    @classmethod
    def from_hdf5(
        cls, 
        path: Path, 
        group: Optional[str] = None
    ) -> "AuxiliaryData":
        """Lädt Auxiliary Data aus HDF5/netCDF."""
        ds = xr.load_dataset(path, group=group, engine="h5netcdf")
        return cls(ds)
    
    @property
    def data(self) -> xr.Dataset:
        """Gibt Rohdaten zurück."""
        return self._data
    
    @property
    def variables(self) -> list[str]:
        """Gibt verfügbare Variablen zurück."""
        return list(self._data.data_vars)
    
    @property
    def time_range(self) -> tuple[float, float]:
        """Gibt (min_time, max_time) zurück."""
        times = self._data.time.values
        return (float(times[0]), float(times[-1]))
    
    def interpolate_to(self, time: np.ndarray) -> xr.Dataset:
        """
        Interpoliert Auxiliary Data auf neue Zeitachse.
        
        Args:
            time: Ziel-Zeitachse (z.B. von CV-Messung)
        
        Returns:
            Dataset mit interpolierten Werten
        """
        return self._data.interp(time=time, method="linear")
    
    def __repr__(self):
        return f"AuxiliaryData(variables={self.variables}, time_range={self.time_range})"
```


