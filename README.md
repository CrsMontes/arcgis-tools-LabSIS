# LabSIS ArcGIS Tools

A modular collection of ArcGIS Pro tools developed by the LabSIS team.

This repository is designed to host multiple Python tools for geospatial
analysis, remote sensing, environmental monitoring, validation, and other
LabSIS workflows.

## Available tools

| Tool | Package | Status |
|---|---|---|
| [Generate Validation Sample](docs/tools/validation-sampling.md) | `validation_sampling` | Interface implemented; statistical calculation and spatial generation under development |

## Project status

Early development version.

The repository structure supports adding new tools without placing their full
implementation inside the main Python toolbox file.

`ArcGISTools.pyt` acts as the toolbox registry. Each tool is implemented in its
own package under `src/labsis_arcgis_tools/`.

## Requirements

- Windows 10 or 11
- ArcGIS Pro 3.6 or a compatible release
- ArcPy supplied with ArcGIS Pro
- Git for version control
- VS Code is recommended for development

## Installation

1. Install ArcGIS Pro.
2. Clone this repository:

   ```powershell
   git clone https://github.com/CrsMontes/arcgis-tools-LabSIS.git
   ```

3. Open ArcGIS Pro.
4. Open the **Catalog** pane.
5. Add the cloned repository as a folder connection.
6. Locate `ArcGISTools.pyt`.
7. Select **Add To Project**.

The tools registered in the Python toolbox will then be available from the
ArcGIS Pro Catalog and Geoprocessing panes.

## Python environment

The toolbox currently uses ArcPy and the Python standard library.

A collaborator does not need to use the same environment name as the original
developer. The environment only needs to belong to a compatible ArcGIS Pro
installation and contain the required dependencies.

The default `arcgispro-py3` environment is sufficient while the project has no
additional third-party dependencies.

For development, cloning the default ArcGIS Pro environment is recommended:

1. Open the ArcGIS Pro Package Manager.
2. Clone `arcgispro-py3`.
3. Assign any descriptive local name.
4. Select the cloned environment as the VS Code Python interpreter.

Confirm that ArcPy is available:

```powershell
python -c "import arcpy; print(arcpy.GetInstallInfo()['Version'])"
```

## Project structure

```text
arcgis-tools/
├── ArcGISTools.pyt
├── src/
│   └── labsis_arcgis_tools/
│       ├── __init__.py
│       └── validation_sampling/
│           ├── __init__.py
│           └── tool.py
├── scripts/
│   └── export_project_report.py
├── docs/
│   └── tools/
│       └── validation-sampling.md
├── examples/
├── tests/
├── .gitignore
└── README.md
```

### Toolbox registry

`ArcGISTools.pyt` contains the ArcGIS Pro toolbox definition and registers the
available tool classes.

Future tools must be imported and added to the `self.tools` list in this file.

### Source package

`src/labsis_arcgis_tools/` contains the implementation packages.

Each major tool should have its own subpackage. Tool-specific calculations,
data processing, output generation, and supporting functions should remain
inside that package.

Shared modules should only be created when functionality is reused by more
than one tool.

### Documentation

`docs/` contains detailed documentation for individual tools and project-level
technical documentation.

### Tests

`tests/` will contain automated tests for calculations that can run
independently from the ArcGIS Pro interface whenever possible.

### Scripts

`scripts/` contains development and maintenance utilities, including the
project report generator.

## Development workflow

1. Pull the latest changes from `main`.
2. Activate a compatible ArcGIS Pro Python environment.
3. Implement or update a tool inside its package under
   `src/labsis_arcgis_tools/`.
4. Register new tool classes in `ArcGISTools.pyt`.
5. Validate Python syntax and imports.
6. Refresh the toolbox in ArcGIS Pro.
7. Test the interface and geoprocessing behavior.
8. Generate and review the local project report.
9. Commit focused changes with descriptive messages.
10. Push the commits to GitHub.

## Basic validation

Compile the current Python files:

```powershell
python -m py_compile `
  .\ArcGISTools.pyt `
  .\scripts\export_project_report.py `
  .\src\labsis_arcgis_tools\validation_sampling\tool.py
```

Validate the toolbox registry:

```powershell
python -c "import runpy; toolbox=runpy.run_path('ArcGISTools.pyt')['Toolbox'](); print(toolbox.label, [tool.__name__ for tool in toolbox.tools])"
```

Expected output:

```text
LabSIS ArcGIS Tools ['GenerateValidationSample']
```

Generate the local project report:

```powershell
python .\scripts\export_project_report.py
```

## Generated and local files

Local GIS datasets, generated outputs, Python caches, ArcGIS metadata files,
environment-variable files, and development environments are excluded through
`.gitignore`.

Source data and large output datasets should not be committed directly to this
repository.

## License

No open-source license has been selected for this repository yet. Reuse and
redistribution terms will be defined according to the LabSIS project policy.