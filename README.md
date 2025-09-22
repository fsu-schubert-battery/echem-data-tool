# Data evaluation tool for electrochemical experiments

This repository is a work-in-progress tool for the management, evaluation, and visualisation of measurement data from electrochemical experiments. In particular, it relates to battery characterization and selected standard electrochemical experiments (e.g., electrochemical impedance spectroscopy, rotating disk electrodes, etc.).

## Installation

For development:
```bash
git clone https://github.com/fsu-schubert-battery/echem-data-tool
cd echem-data-tool
poetry install
```

For end users:
```bash
pip install echem-data-tool
```

## Documentation

This project uses `pdoc` to generate the documentation. Execute the following command to compile the documentation:

```bash

# Or directly with pdoc
poetry run pdoc --output-dir docs --docformat google echem_data_tool
```

Then open `docs/index.html` in your browser.

## Development

Run tests:
```bash
poetry run pytest
```

## License

This project is licensed under the AGPL-3.0 license. See [LICENSE](LICENSE) for details.