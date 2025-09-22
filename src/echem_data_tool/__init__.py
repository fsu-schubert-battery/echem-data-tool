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
**Data evaluation tool for electrochemical experiments**

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

## What this is for?

The **Echem Data Tool** is a comprehensive Python package designed for the management, 
evaluation, and visualization of measurement data from electrochemical experiments. 

### Key Features

- **📊 Data Management**: Import, organize, and manage electrochemical measurement data
- **⚡ Analysis Tools**: Built-in analysis functions for common electrochemical techniques
- **📈 Visualization**: Create publication-ready plots and charts
- **🧪 Electrochemical Focus**: Specialized tools for battery research and electroanalysis

### Supported Techniques

- Galvanostatic/Potentiostatic measurements
- Electrochemical Impedance Spectroscopy (EIS)
- Rotating Disk Electrode (RDE) experiments
- Battery cycling data
- And more...

# Installation

### For End Users

Install directly from PyPI:

```bash
pip install echem-data-tool
```

### Requirements

- **Python**: 3.13 or higher
- **Dependencies**: pandas, xarray, yadg, pycodata
- **Development**: pytest, pdoc (for documentation)

# Quick Start

```python
from echem_data_tool import main
from pycodata import constants_2022 as pc

### Run the main application
main()

# Access physical constants
faraday = pc.FARADAY_CONSTANT['value']  # 96485.33212 C/mol
print(f"Faraday constant: {faraday} C/mol")
```

# Documentation Structure

This documentation is organized into the following modules:

- **`main`**: Main application entry point and demonstration
- Additional modules will be added as the project develops

# Development Status

🚧 **Work in Progress**: This project is actively under development. 
The API may change between versions until v1.0.0 is released.

# License

This project is licensed under the **GNU Affero General Public License v3.0 or later (AGPL-3.0+)**.

This means:
- ✅ You can use, modify, and distribute this software
- ✅ Commercial use is allowed
- ⚠️ Any modifications must also be licensed under AGPL-3.0+
- ⚠️ Network use is considered distribution (copyleft applies)

See the [LICENSE](https://github.com/fsu-schubert-battery/echem-data-tool/blob/main/LICENSE) 
file for the complete license text.

# Authors & Affiliations

### Friedrich-Schiller-Universität Jena

- Christian Stolze (christian.stolze@uni-jena.de)
- Sebastian Witt (sebastian.witt@uni-jena.de)  

### HIPOLE Jena

- Felix Nagler (felix.nagler@helmholtz-berlin.de)

# Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, 
or pull requests on [GitHub](https://github.com/fsu-schubert-battery/echem-data-tool).

---

*Generated with [pdoc](https://pdoc.dev).*
"""

try:
    from importlib.metadata import version
    __version__ = version("echem-data-tool")
except ImportError:
    # Fallback for older Python versions or if package is not installed
    __version__ = "development"
except Exception:
    __version__ = "development"
