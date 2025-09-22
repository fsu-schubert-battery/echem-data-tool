

# Data evaluation tool for electrochemical experiments

[![Development Status](https://img.shields.io/badge/Status-Under%20Development-orange.svg)](https://github.com/fsu-schubert-battery/echem-data-tool)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.13+-brightgreen.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/Poetry-Package%20Manager-blue.svg)](https://python-poetry.org/)
[![Documentation](https://img.shields.io/badge/Documentation-GitHub%20Pages-green.svg)](https://fsu-schubert-battery.github.io/echem-data-tool/)
[![CODATA](https://img.shields.io/badge/Constants-CODATA%202022-purple.svg)](https://physics.nist.gov/cuu/Constants/)

This repository is a work-in-progress tool for the management, evaluation, and visualisation of measurement data from electrochemical experiments. In particular, it relates to battery characterization and selected standard electrochemical experiments (e.g., electrochemical impedance spectroscopy, rotating disk electrodes, etc.).

## Installation

For development:
```bash
git clone https://github.com/fsu-schubert-battery/echem-data-tool
cd echem-data-tool
poetry install
```

For end users (not yet possible, since this project is under development):
```bash
pip install echem-data-tool
```

## Documentation

This project uses `pdoc` to generate the documentation. 

### Generate Locally
```bash
# Generate documentation
PYTHONPATH=src poetry run pdoc --output-dir docs --docformat google echem_data_tool
```

Then open `docs/index.html` in your browser.

### Online Documentation
Documentation is automatically deployed to GitHub Pages on every push to the main branch:
- **GitHub Pages**: [https://fsu-schubert-battery.github.io/echem-data-tool/](https://fsu-schubert-battery.github.io/echem-data-tool/)

## Development

Run tests:
```bash
poetry run pytest
```

## License

This project is licensed under the AGPL-3.0 license. See [LICENSE](LICENSE) for details.