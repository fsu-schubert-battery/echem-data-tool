## Motivation & Goals

In order to avoid multiple people in the battery group to go through the same process of writing own scripts for evaluating the same kind of experiments, we aim to create a versatile python package for the evaluation of electrochemical data.

If the whole framework works nicely, this could be published as a small publication as well. 

### User Stories

- As a user, I want a python package that is capable of digesting and processing different file formats from various potentiostats/galvanostats to evaluate my data in a consistent manner
- As a user, I want to be able to install this python package via `pip` to easily use it in my own scripts
- As a user, I want to be able to process data recorded by other instruments in parallel to my potentiostat together with my electrochemical data (e.g., temperature sensors, SOC sensors, etc.)
- As a user, I want to have both the experimental data and the metadata for my experiments in one file using an open file format so that I have a single-source of truth 
- As a user, I want to be able to easily generate plots from my data and customize those plots for publications and discussions
- As a user, I want other scientists to be able to download my data and my data processing setup at once so that they can easily reproduce my graphs and run their own evaluation on my data
- As a user, I want a web-app which allows management and evaluation of my experimental data in a dashboard so that I can use the package even if I cannot code
- As a user, want to save my data evaluation progress in the web-app so that I can pause and continue working on it at any time
- As a developer, I want to be able to implement my own file formats and techniques in this package so that I can use it with my devices and experimental procedures

## Code Structure

### Ideas / Goals

- Use `poetry` for package management to establish a simple package management
- Create a `pip` package for easy installation and usage by third-party scripts
- For all classes and methods use `docstring` right from the start to make later documentation easier
- Support various file types and enable straight-forward implementation of new file formats
- Use a Modular code structure to enable subsequent implementation of new instruments/techniques over time
- Create a web-/Browser-based UI for users who cannot or don't want to code
### Python Library 

- Object-oriented code, which implements experiments/batteries/samples/setups (requires discussion) as objects 
- Objects have methods for file loading, data processing, and plotting
#### A) File Loader

- Define a `FileObject` as a representation of a measurement/experiment that contains all relevant data and metadata
- A **base class** `BaseFile` defines how the final file format is structured internally and what common methods each file requires (e.g., `load()`, `delete()`, `save()`, `from_xarray()`, `to_xarray()`, `from_pandas()`, `to_pandas()`, ... ?)
- Each file format is implemented as a child class of `BaseFile`,  (e.g., `MprStandardTechniqueFile`, `MprModuloBatFile`, etc.) and each child class processes the specific type into a common data format
- Common data format should be `netCDF4` and we should rely on the `h5netcdf` and/or `xarray` packages, which are also used by `yadg`
- Since `xarray`usually requires equidistant axis data, it might make sense to load files with `pandas`, prepare data for `xarray` and then store as netCDF


```python

# ========== Common file format representation ==========

@dataclass
class FileObject:
    data: xr.Dataset
    meta: dict[str, t.Any] = field(default_factory=dict)
    uri: Path | None = None

    # serialize to netCDF format
    def to_netcdf(self, path: str | Path, *, engine: str = "h5netcdf") -> None:
        ds = self.data.assign_attrs(self.meta)
        ds.to_netcdf(Path(path), engine=engine)

    # direct access to underlying xarray
    def to_xarray(self) -> xr.Dataset:
        return self.data

	# access underlying data as pandas dataframe
    def to_pandas(self) -> pd.DataFrame:
        # einfache Konvention: alle Variablen -> Spalten, Koordinaten -> Index
        return self.data.to_dataframe().reset_index()



# ========== Abstract base class for file formats ==========
class BaseFile(ABC):
    format_name: str = "base"
    suffixes: tuple[str, ...] = ()
    _registry: list[type["BaseFile"]] = []

    def __init_subclass__(cls) -> None:

        if cls is not BaseFile:
            BaseFile._registry.append(cls)

    # ---- Factory / Auto-Erkennung ----

    @classmethod
    def open(cls, path: str | Path) -> FileObject:
	    # load file
	    pass

    # ---- Process data: From file format -> common data format ----

    @classmethod
    @abstractmethod
    def load(cls, path: Path) -> FileObject:
	    # actual implementation in each child classes
	    pass

	# etc.
	
# ========== File format implementations ==========
class MprStandardFile(BaseFile):
    format_name = "mpr"
    suffixes = (".mpr",)

    @classmethod
    def open(cls, path: str | Path) -> None:
	    # ...
	    return 

    # ---- Process data: From file format -> common data format ----

    @classmethod
    @abstractmethod
    def load(cls, path: Path) -> FileObject:
	    # ...
	    return FileObject

	# etc.
```

#### B) Techniques

- Each measurement file can contain data from one or more techniques
- A **base class** `BaseTechnique` will be used to represent measurement data for a specific technique and will define common methods of techniques (e.g., `load_file(Path)`, `add_file(FileObject)`, `remove_file()`, `preprocess()`, `analyze()`, etc. )
- Specific techniques will be **child classes** of `BaseTechnique` (e.g., `EIS`, `GCPL`, `RDE` etc.) and may contain further technique specific methods

#### C) Cells

- A cell object can represent any electrochemical cell (coin cell, swagelok cell, flow battery, two-electrode setup in beaker, three-electrode setup in beaker, etc.)
- A **base class** `BaseCell` will be used to represent physical cells and will define common methods (e.g., `set_metadata()`, `get_metadata()`, `add_technique(FileObject)`, `get_technique(FileObject)`, `remove_technique()`)
- **Child classes** may be defined to represent the different cell types and add additional methods specific to the cell type (e.g., `set_reference_electrode(name, ref_potential)`, `get_reference_electrode()`, etc. )

#### D) Experiments

- An experiment will be the place to manage different cells and measurements, which will be mainly useful in the later UI
- It can contain one or multiple cells
- Define a `Experiment` class which defines a common set of methods (e.g., `new_cell()`, `add_cell()`, `remove_cell()`,  `add_figure()`, `add_subplot(figure, label="a")`, `add_figure_trace(figure, subplot, cells=[1, 2, 3, ...], x=data_var_name, y=data_var_name)`, etc.)

#### Visualization

![[figures/mermaid-diagram-2025-09-18-135458.png]]