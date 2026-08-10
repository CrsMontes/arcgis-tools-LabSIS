# Generate Validation Sample

## Purpose

`Generate Validation Sample` is an ArcGIS Pro tool for designing
probability-based validation samples for categorical maps and continuous
variables.

The tool is intended to support statistically defensible validation workflows
based on stratified probability sampling.

## Scientific basis

The categorical validation workflow is intended to follow the good-practice
principles described by Olofsson et al. (2014), including:

- Probability-based sample selection
- Explicit sampling strata
- Adequate representation of rare classes
- Sample allocation based on validation objectives
- Reproducible sample generation
- Analysis consistent with the sampling design

The tool addresses the sampling-design component. Reference labeling, response
design, accuracy estimation, area-adjusted estimates, and uncertainty analysis
must remain consistent with the resulting sample design.

## Implementation status

### Implemented

- ArcGIS Pro parameter interface
- Categorical and continuous validation modes
- Raster and vector strata inputs
- Dynamic class-field selection
- Dynamic class-value discovery
- Expected user's accuracy table
- Manual allocation table
- Parameter validation
- Spatial sampling method selection
- Minimum sample distance parameter
- Reproducible random seed parameter
- Output path definitions
- Configuration messages

### Under development

- Statistical total sample-size calculation
- Optimized sample allocation
- Proportional sample allocation
- Equal sample allocation
- Manual allocation execution
- Spatially balanced point generation
- Stratified random point generation
- Minimum-distance enforcement
- Sampling-design output table
- Region-aware sampling and assignment
- Validation-point feature class generation

The current version does not yet generate validation points.

## Parameters

| Parameter | Required | Default | Description |
|---|---:|---:|---|
| Validation Target | Yes | `Categorical` | Selects categorical-map or continuous-variable validation. |
| Sampling Strata / Classified Map | Yes | - | Raster or polygon feature layer defining the sampling strata. |
| Continuous Variable Raster | Conditional | - | Original continuous raster evaluated when the validation target is continuous. |
| Stratum / Class Field | Yes | - | Integer or text field containing the stratum or map-class identifier. |
| Strata / Classes to Validate | Yes | All discovered values | Classes included in the sampling design. |
| Confidence Level (%) | Yes | `95` | Confidence level used by the planned sample-size calculation. |
| Target Margin of Error (%) | Yes | `3` | Target uncertainty expressed in percentage points. |
| Expected User's Accuracy by Class | Categorical mode | `0.85` | Expected user's accuracy entered as a proportion from `0.01` to `0.99`. |
| Minimum Samples per Stratum | Yes | `30` | Lower allocation bound to be applied to every selected stratum. |
| Allocation Method | Yes | `Optimized` | Available options: Optimized, Proportional, Equal, and Manual. |
| Manual Sample Allocation | Manual mode | - | Number of samples explicitly assigned to each selected class. |
| Spatial Sampling Method | Yes | `Spatially Balanced` | Available options: Spatially Balanced and Stratified Random. |
| Minimum Sample Distance | No | `100 Meters` | Planned minimum separation between generated validation points. |
| Random Seed | No | `42` | Seed used to reproduce randomized sampling results. |
| Output Validation Points | Yes | - | Output point feature class. |
| Output Sampling Design Table | No | - | Optional table containing the final sampling design. |

## Validation modes

### Categorical

Use this mode when validating a classified raster or polygon dataset.

The map classes define the sampling strata. Expected user's accuracy can be
specified independently for every selected class.

### Continuous

Use this mode when validating a continuous raster using predefined strata.

The strata dataset defines the sampling design, while the continuous raster
provides the values that will later be evaluated at the selected locations.

## Allocation methods

### Optimized

Intended to distribute samples according to stratum area, expected accuracy,
target uncertainty, and the minimum allocation constraint.

### Proportional

Intended to allocate samples in proportion to the mapped area of each stratum.

### Equal

Intended to assign the same number of samples to every selected stratum.

### Manual

Uses the sample counts entered by the user for each selected stratum.

## Spatial sampling methods

### Spatially Balanced

Intended to distribute the validation points across the spatial extent of each
stratum while reducing clustering.

### Stratified Random

Intended to select random locations independently within every stratum.

## Region-aware sampling

Region-aware sampling is planned but is not implemented in the current
interface.

The planned design will allow a region field to be combined with the map-class
field. This will support:

- Separate allocations by region and class
- Region-specific validation subsets
- Assignment of all samples from one region to a specific interpreter
- Preservation of both region and class attributes in the output

## Outputs

### Validation points

The planned output feature class will contain the generated sample locations
and their design attributes.

Expected fields include:

- Unique sample identifier
- Map class
- Sampling stratum
- Region, when enabled
- Inclusion or design information needed by subsequent analysis

The final field schema will be defined before spatial generation is
implemented.

### Sampling design table

The optional design table is intended to document:

- Stratum identifiers
- Stratum area or weight
- Expected user's accuracy
- Allocation method
- Number of allocated samples
- Confidence level
- Target margin of error
- Random seed

## Limitations

The current development version:

- Does not calculate the final sample size
- Does not execute the selected allocation method
- Does not generate spatial sample points
- Does not enforce the minimum sample distance
- Does not create the output sampling-design table
- Does not yet support separate allocations by region

The interface and validation logic may change while the statistical and spatial
components are implemented.

## Reference

Olofsson, P., Foody, G. M., Herold, M., Stehman, S. V., Woodcock, C. E., and
Wulder, M. A. (2014). Good practices for estimating area and assessing
accuracy of land change. *Remote Sensing of Environment*, 148, 42-57.
https://doi.org/10.1016/j.rse.2014.02.015
