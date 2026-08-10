# ArcGIS Validation Sampling Tool

Python toolbox for generating statistically sound validation samples for
classified geospatial datasets in ArcGIS Pro.

## Project status

Early development version.

The ArcGIS Pro interface and parameter validation are implemented. Statistical
sample-size calculation, allocation, and spatial point generation are still
under development.

## Planned capabilities

- Categorical and continuous validation objectives
- Raster and vector classified datasets
- Stratified probability sampling
- Olofsson-based accuracy assessment design
- Optimized sample allocation
- Minimum samples per stratum
- Region-aware sampling
- Spatially balanced sample generation
- Minimum distance between validation points
- Reproducible random seed
- Output compatible with ArcGIS Pro and Collect Earth Online

## Current default parameters

- Confidence level: 95%
- Target margin of error: 3%
- Expected user's accuracy: 0.75–0.95
- Minimum samples per stratum: 30
- Allocation method: Optimized
- Minimum point distance: 100 m
- Random seed: 42

## Requirements

- Windows 10 or 11
- ArcGIS Pro 3.6 or a compatible release
- ArcPy supplied with ArcGIS Pro

## Python environment

The toolbox can run with the default `arcgispro-py3` environment when no
additional packages are required.

For development, cloning `arcgispro-py3` is recommended before adding or
modifying packages. The cloned environment can have any name.

In VS Code, select the Python interpreter belonging to the local ArcGIS Pro
environment.

## Installation

1. Install ArcGIS Pro.
2. Clone this repository.
3. Open ArcGIS Pro.
4. In the Catalog pane, select **Toolboxes > Add Toolbox**.
5. Select `ArcGISTools.pyt`.

## Development setup

1. Clone the default `arcgispro-py3` environment if package modification is
   required.
2. Open the repository folder in VS Code.
3. Select the ArcGIS Pro Python interpreter.
4. Confirm that ArcPy is available:

   ```powershell
   python -c "import arcpy; print(arcpy.GetInstallInfo()['Version'])"