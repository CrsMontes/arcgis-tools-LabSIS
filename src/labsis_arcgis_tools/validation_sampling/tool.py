import arcpy


class GenerateValidationSample:
    def __init__(self):
        self.label = "Generate Validation Sample"

        self.description = (
            "Designs a probability-based validation sample for categorical "
            "maps or continuous variables. Categorical validation follows a "
            "stratified accuracy-assessment framework, while continuous "
            "validation uses predefined strata and an auxiliary continuous raster."
        )

        self.canRunInBackground = False

        # Used to detect changes in the input dataset or stratum field.
        self._last_source_key = None
        self._last_selected_strata = None

    # -------------------------------------------------------------------------
    # Parameter definitions
    # -------------------------------------------------------------------------

    def getParameterInfo(self):

        # ---------------------------------------------------------------------
        # 0. Validation target
        # ---------------------------------------------------------------------

        validation_target = arcpy.Parameter(
            displayName="Validation Target",
            name="validation_target",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        validation_target.filter.type = "ValueList"
        validation_target.filter.list = [
            "Categorical",
            "Continuous"
        ]

        validation_target.value = "Categorical"

        # ---------------------------------------------------------------------
        # 1. Sampling strata / classified map
        # ---------------------------------------------------------------------

        classified_map = arcpy.Parameter(
            displayName="Sampling Strata / Classified Map",
            name="classified_map",
            datatype=[
                "GPRasterLayer",
                "GPFeatureLayer"
            ],
            parameterType="Required",
            direction="Input"
        )

        # ---------------------------------------------------------------------
        # 2. Continuous variable raster
        # ---------------------------------------------------------------------

        continuous_raster = arcpy.Parameter(
            displayName="Continuous Variable Raster",
            name="continuous_raster",
            datatype="GPRasterLayer",
            parameterType="Optional",
            direction="Input"
        )

        continuous_raster.enabled = False

        # ---------------------------------------------------------------------
        # 3. Stratum / class field
        # ---------------------------------------------------------------------

        stratum_field = arcpy.Parameter(
            displayName="Stratum / Class Field",
            name="stratum_field",
            datatype="Field",
            parameterType="Required",
            direction="Input"
        )

        stratum_field.parameterDependencies = [
            classified_map.name
        ]

        # Allow common categorical field types.
        stratum_field.filter.list = [
            "Short",
            "Long",
            "BigInteger",
            "Text"
        ]

        # ---------------------------------------------------------------------
        # 4. Strata / classes to validate
        # ---------------------------------------------------------------------

        strata = arcpy.Parameter(
            displayName="Strata / Classes to Validate",
            name="strata",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
            multiValue=True
        )

        strata.filter.type = "ValueList"

        # ArcGIS multivalue control with checkboxes and Select All.
        strata.controlCLSID = "{38C34610-C7F7-11D5-A693-0008C711C8C1}"

        # ---------------------------------------------------------------------
        # 5. Confidence level
        # ---------------------------------------------------------------------

        confidence_level = arcpy.Parameter(
            displayName="Confidence Level (%)",
            name="confidence_level",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input"
        )

        confidence_level.filter.type = "ValueList"
        confidence_level.filter.list = [
            90,
            95,
            99
        ]

        confidence_level.value = 95

        # ---------------------------------------------------------------------
        # 6. Target margin of error
        # ---------------------------------------------------------------------

        target_margin = arcpy.Parameter(
            displayName="Target Margin of Error (%)",
            name="target_margin",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input"
        )

        target_margin.filter.type = "Range"
        target_margin.filter.list = [
            0.1,
            25.0
        ]

        target_margin.value = 3.0

        # ---------------------------------------------------------------------
        # 7. Expected User's Accuracy
        # ---------------------------------------------------------------------

        expected_accuracy = arcpy.Parameter(
            displayName="Expected User's Accuracy by Class",
            name="expected_accuracy",
            datatype="GPValueTable",
            parameterType="Optional",
            direction="Input"
        )

        expected_accuracy.columns = [
            [
                "GPString",
                "Map Class",
                "ReadOnly"
            ],
            [
                "GPDouble",
                "Expected User's Accuracy"
            ]
        ]

        expected_accuracy.filters[1].type = "Range"
        expected_accuracy.filters[1].list = [
            0.01,
            0.99
        ]

        # ---------------------------------------------------------------------
        # 8. Minimum samples per stratum
        # ---------------------------------------------------------------------

        minimum_samples = arcpy.Parameter(
            displayName="Minimum Samples per Stratum",
            name="minimum_samples",
            datatype="GPLong",
            parameterType="Required",
            direction="Input"
        )

        minimum_samples.filter.type = "Range"
        minimum_samples.filter.list = [
            1,
            100000
        ]

        minimum_samples.value = 30

        # ---------------------------------------------------------------------
        # 9. Allocation method
        # ---------------------------------------------------------------------

        allocation_method = arcpy.Parameter(
            displayName="Allocation Method",
            name="allocation_method",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        allocation_method.filter.type = "ValueList"
        allocation_method.filter.list = [
            "Optimized",
            "Proportional",
            "Equal",
            "Manual"
        ]

        allocation_method.value = "Optimized"

        # ---------------------------------------------------------------------
        # 10. Manual sample allocation
        # ---------------------------------------------------------------------

        manual_allocation = arcpy.Parameter(
            displayName="Manual Sample Allocation",
            name="manual_allocation",
            datatype="GPValueTable",
            parameterType="Optional",
            direction="Input"
        )

        manual_allocation.columns = [
            [
                "GPString",
                "Map Class",
                "ReadOnly"
            ],
            [
                "GPLong",
                "Number of Samples"
            ]
        ]

        manual_allocation.filters[1].type = "Range"
        manual_allocation.filters[1].list = [
            1,
            1000000
        ]

        manual_allocation.enabled = False

        # ---------------------------------------------------------------------
        # 11. Spatial sampling method
        # ---------------------------------------------------------------------

        spatial_method = arcpy.Parameter(
            displayName="Spatial Sampling Method",
            name="spatial_method",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        spatial_method.filter.type = "ValueList"
        spatial_method.filter.list = [
            "Spatially Balanced",
            "Stratified Random"
        ]

        spatial_method.value = "Spatially Balanced"

        # ---------------------------------------------------------------------
        # 12. Minimum sample distance
        # ---------------------------------------------------------------------

        minimum_distance = arcpy.Parameter(
            displayName="Minimum Sample Distance",
            name="minimum_distance",
            datatype="GPLinearUnit",
            parameterType="Optional",
            direction="Input"
        )

        minimum_distance.value = "0 Meters"

        minimum_distance.category = "Advanced Spatial Parameters"

        # ---------------------------------------------------------------------
        # 13. Random seed
        # ---------------------------------------------------------------------

        random_seed = arcpy.Parameter(
            displayName="Random Seed",
            name="random_seed",
            datatype="GPLong",
            parameterType="Optional",
            direction="Input"
        )

        random_seed.value = 42

        random_seed.category = "Advanced Spatial Parameters"

        # ---------------------------------------------------------------------
        # 14. Output validation points
        # ---------------------------------------------------------------------

        output_points = arcpy.Parameter(
            displayName="Output Validation Points",
            name="output_points",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output"
        )

        # ---------------------------------------------------------------------
        # 15. Output sampling design
        # ---------------------------------------------------------------------

        output_design = arcpy.Parameter(
            displayName="Output Sampling Design Table",
            name="output_design",
            datatype="DETable",
            parameterType="Optional",
            direction="Output"
        )

        return [
            validation_target,      # 0
            classified_map,         # 1
            continuous_raster,      # 2
            stratum_field,          # 3
            strata,                 # 4
            confidence_level,       # 5
            target_margin,          # 6
            expected_accuracy,      # 7
            minimum_samples,        # 8
            allocation_method,      # 9
            manual_allocation,      # 10
            spatial_method,         # 11
            minimum_distance,       # 12
            random_seed,            # 13
            output_points,          # 14
            output_design           # 15
        ]

    # -------------------------------------------------------------------------
    # Helper functions
    # -------------------------------------------------------------------------

    @staticmethod
    def _sort_values(values):
        """
        Sort values numerically when possible and alphabetically otherwise.
        """

        try:
            return sorted(
                values,
                key=lambda value: float(value)
            )
        except (ValueError, TypeError):
            return sorted(
                values,
                key=lambda value: str(value).lower()
            )

    @staticmethod
    def _get_unique_values(dataset, field_name):
        """
        Read unique non-null values from a field.
        """

        unique_values = set()

        with arcpy.da.SearchCursor(
            dataset,
            [field_name]
        ) as cursor:

            for row in cursor:

                value = row[0]

                if value is not None:
                    unique_values.add(str(value))

        return GenerateValidationSample._sort_values(
            unique_values
        )

    @staticmethod
    def _get_multivalue_items(parameter):
        """
        Convert an ArcGIS multivalue parameter to a Python list.
        """

        text = parameter.valueAsText

        if not text:
            return []

        values = []

        for item in text.split(";"):

            clean_item = (
                item
                .strip()
                .strip("'")
                .strip('"')
            )

            if clean_item:
                values.append(clean_item)

        return values

    @staticmethod
    def _preserve_accuracy_values(parameter):
        """
        Return existing Expected UA values as a dictionary.
        """

        existing = {}

        if not parameter.values:
            return existing

        for row in parameter.values:

            if not row:
                continue

            class_name = str(row[0])

            try:
                accuracy = float(row[1])
            except (TypeError, ValueError):
                accuracy = 0.85

            existing[class_name] = accuracy

        return existing

    @staticmethod
    def _preserve_manual_values(parameter):
        """
        Return existing manual sample counts as a dictionary.
        """

        existing = {}

        if not parameter.values:
            return existing

        for row in parameter.values:

            if not row:
                continue

            class_name = str(row[0])

            try:
                sample_count = int(row[1])
            except (TypeError, ValueError):
                sample_count = 30

            existing[class_name] = sample_count

        return existing

    # -------------------------------------------------------------------------
    # Dynamic interface
    # -------------------------------------------------------------------------

    def updateParameters(self, parameters):

        validation_target = parameters[0]
        classified_map = parameters[1]
        continuous_raster = parameters[2]
        stratum_field = parameters[3]
        strata = parameters[4]

        expected_accuracy = parameters[7]
        minimum_samples = parameters[8]
        allocation_method = parameters[9]
        manual_allocation = parameters[10]

        # ---------------------------------------------------------------------
        # Validation target
        # ---------------------------------------------------------------------

        target = validation_target.valueAsText

        if target == "Continuous":

            continuous_raster.enabled = True

            # Expected User's Accuracy is only meaningful for categorical maps.
            expected_accuracy.enabled = False

            allocation_method.filter.list = [
                "Optimized",
                "Proportional",
                "Equal",
                "Manual"
            ]

        else:

            continuous_raster.enabled = False
            expected_accuracy.enabled = True

            allocation_method.filter.list = [
                "Optimized",
                "Proportional",
                "Equal",
                "Manual"
            ]

        # ---------------------------------------------------------------------
        # Automatically choose Value for categorical rasters when possible
        # ---------------------------------------------------------------------

        if classified_map.value:

            dataset = classified_map.valueAsText

            try:

                description = arcpy.Describe(dataset)

                if hasattr(description, "dataType"):

                    if description.dataType in [
                        "RasterLayer",
                        "RasterDataset"
                    ]:

                        field_names = [
                            field.name
                            for field in arcpy.ListFields(dataset)
                        ]

                        if (
                            "Value" in field_names
                            and not stratum_field.altered
                        ):
                            stratum_field.value = "Value"

            except Exception:
                pass

        # ---------------------------------------------------------------------
        # Populate strata when dataset or field changes
        # ---------------------------------------------------------------------

        if (
            classified_map.value
            and stratum_field.value
        ):

            dataset = classified_map.valueAsText
            field_name = stratum_field.valueAsText

            source_key = (
                dataset,
                field_name
            )

            if source_key != self._last_source_key:

                try:

                    unique_values = self._get_unique_values(
                        dataset,
                        field_name
                    )

                    strata.filter.list = unique_values

                    # Select all strata by default.
                    if unique_values:

                        formatted_values = []

                        for value in unique_values:

                            if " " in value:
                                formatted_values.append(
                                    f"'{value}'"
                                )
                            else:
                                formatted_values.append(value)

                        strata.value = ";".join(
                            formatted_values
                        )

                        expected_accuracy.values = [
                            [
                                value,
                                0.85
                            ]
                            for value in unique_values
                        ]

                        manual_allocation.values = [
                            [
                                value,
                                int(minimum_samples.value or 30)
                            ]
                            for value in unique_values
                        ]

                    self._last_source_key = source_key
                    self._last_selected_strata = tuple(
                        unique_values
                    )

                except Exception:

                    strata.filter.list = []

        # ---------------------------------------------------------------------
        # Update tables when selected strata change
        # ---------------------------------------------------------------------

        selected_strata = self._get_multivalue_items(
            strata
        )

        selected_key = tuple(
            selected_strata
        )

        if (
            selected_strata
            and selected_key != self._last_selected_strata
        ):

            # Preserve user-entered values when possible.
            old_accuracy = self._preserve_accuracy_values(
                expected_accuracy
            )

            old_manual = self._preserve_manual_values(
                manual_allocation
            )

            expected_accuracy.values = [
                [
                    class_name,
                    old_accuracy.get(
                        class_name,
                        0.85
                    )
                ]
                for class_name in selected_strata
            ]

            default_minimum = int(
                minimum_samples.value or 30
            )

            manual_allocation.values = [
                [
                    class_name,
                    old_manual.get(
                        class_name,
                        default_minimum
                    )
                ]
                for class_name in selected_strata
            ]

            self._last_selected_strata = selected_key

        # ---------------------------------------------------------------------
        # Manual allocation
        # ---------------------------------------------------------------------

        if allocation_method.valueAsText == "Manual":
            manual_allocation.enabled = True
        else:
            manual_allocation.enabled = False

        return

    # -------------------------------------------------------------------------
    # Validation messages
    # -------------------------------------------------------------------------

    def updateMessages(self, parameters):

        validation_target = parameters[0]
        classified_map = parameters[1]
        continuous_raster = parameters[2]
        stratum_field = parameters[3]
        strata = parameters[4]

        confidence_level = parameters[5]
        target_margin = parameters[6]
        expected_accuracy = parameters[7]
        minimum_samples = parameters[8]
        allocation_method = parameters[9]
        manual_allocation = parameters[10]

        minimum_distance = parameters[12]

        # ---------------------------------------------------------------------
        # Input geometry/type checks
        # ---------------------------------------------------------------------

        if classified_map.value:

            try:

                description = arcpy.Describe(
                    classified_map.valueAsText
                )

                data_type = description.dataType

                if data_type in [
                    "FeatureLayer",
                    "FeatureClass",
                    "ShapeFile"
                ]:

                    shape_type = description.shapeType

                    if shape_type != "Polygon":

                        classified_map.setErrorMessage(
                            "Vector sampling strata must be polygon features."
                        )

                elif data_type not in [
                    "RasterLayer",
                    "RasterDataset"
                ]:

                    classified_map.setErrorMessage(
                        "Input must be a categorical raster or polygon layer."
                    )

            except Exception:
                pass

        # ---------------------------------------------------------------------
        # Continuous workflow
        # ---------------------------------------------------------------------

        if validation_target.valueAsText == "Continuous":

            if not continuous_raster.value:

                continuous_raster.setErrorMessage(
                    "A continuous variable raster is required when "
                    "Validation Target is Continuous."
                )

        # ---------------------------------------------------------------------
        # Selected strata
        # ---------------------------------------------------------------------

        if not self._get_multivalue_items(strata):

            strata.setErrorMessage(
                "Select at least one sampling stratum."
            )

        # ---------------------------------------------------------------------
        # Confidence level
        # ---------------------------------------------------------------------

        if confidence_level.value:

            value = float(
                confidence_level.value
            )

            if value not in [
                90.0,
                95.0,
                99.0
            ]:

                confidence_level.setErrorMessage(
                    "Confidence level must be 90, 95, or 99 percent."
                )

        # ---------------------------------------------------------------------
        # Margin of error
        # ---------------------------------------------------------------------

        if target_margin.value:

            value = float(
                target_margin.value
            )

            if value <= 0:

                target_margin.setErrorMessage(
                    "Target margin of error must be greater than zero."
                )

        # ---------------------------------------------------------------------
        # Expected User's Accuracy
        # ---------------------------------------------------------------------

        if (
            validation_target.valueAsText == "Categorical"
            and expected_accuracy.values
        ):

            for row in expected_accuracy.values:

                try:

                    accuracy = float(
                        row[1]
                    )

                    if not 0 < accuracy < 1:

                        expected_accuracy.setErrorMessage(
                            "Expected User's Accuracy values must be "
                            "greater than 0 and less than 1."
                        )

                        break

                except (TypeError, ValueError):

                    expected_accuracy.setErrorMessage(
                        "Expected User's Accuracy must contain a valid "
                        "decimal value for every selected class."
                    )

                    break

        # ---------------------------------------------------------------------
        # Minimum samples
        # ---------------------------------------------------------------------

        if minimum_samples.value:

            if int(minimum_samples.value) < 1:

                minimum_samples.setErrorMessage(
                    "Minimum Samples per Stratum must be at least 1."
                )

        # ---------------------------------------------------------------------
        # Manual allocation
        # ---------------------------------------------------------------------

        if allocation_method.valueAsText == "Manual":

            if not manual_allocation.values:

                manual_allocation.setErrorMessage(
                    "Provide a sample count for every selected stratum."
                )

        # ---------------------------------------------------------------------
        # Minimum distance
        # ---------------------------------------------------------------------

        if minimum_distance.value:

            try:

                if minimum_distance.value.value < 0:

                    minimum_distance.setErrorMessage(
                        "Minimum Sample Distance cannot be negative."
                    )

            except Exception:
                pass

        return

    # -------------------------------------------------------------------------
    # Execute
    # -------------------------------------------------------------------------

    def execute(self, parameters, messages):

        validation_target = parameters[0].valueAsText
        classified_map = parameters[1].valueAsText
        continuous_raster = parameters[2].valueAsText
        stratum_field = parameters[3].valueAsText

        selected_strata = self._get_multivalue_items(
            parameters[4]
        )

        confidence_level = float(
            parameters[5].value
        )

        target_margin = float(
            parameters[6].value
        )

        minimum_samples = int(
            parameters[8].value
        )

        allocation_method = parameters[9].valueAsText
        spatial_method = parameters[11].valueAsText

        minimum_distance = parameters[12].valueAsText
        random_seed = parameters[13].value

        output_points = parameters[14].valueAsText
        output_design = parameters[15].valueAsText

        arcpy.AddMessage("")
        arcpy.AddMessage(
            "VALIDATION SAMPLE CONFIGURATION"
        )
        arcpy.AddMessage(
            "----------------------------------------"
        )

        arcpy.AddMessage(
            f"Validation target: {validation_target}"
        )

        arcpy.AddMessage(
            f"Sampling strata: {classified_map}"
        )

        if validation_target == "Continuous":

            arcpy.AddMessage(
                f"Continuous raster: {continuous_raster}"
            )

        arcpy.AddMessage(
            f"Stratum field: {stratum_field}"
        )

        arcpy.AddMessage(
            f"Selected strata: {len(selected_strata)}"
        )

        for class_name in selected_strata:

            arcpy.AddMessage(
                f"  - {class_name}"
            )

        arcpy.AddMessage("")
        arcpy.AddMessage(
            f"Confidence level: {confidence_level:.0f}%"
        )

        arcpy.AddMessage(
            f"Target margin of error: ±{target_margin:.2f}%"
        )

        arcpy.AddMessage(
            f"Minimum samples per stratum: {minimum_samples}"
        )

        arcpy.AddMessage(
            f"Allocation method: {allocation_method}"
        )

        arcpy.AddMessage(
            f"Spatial sampling method: {spatial_method}"
        )

        arcpy.AddMessage(
            f"Minimum sample distance: {minimum_distance}"
        )

        arcpy.AddMessage(
            f"Random seed: {random_seed}"
        )

        arcpy.AddMessage("")
        arcpy.AddMessage(
            f"Output validation points: {output_points}"
        )

        if output_design:

            arcpy.AddMessage(
                f"Output sampling design: {output_design}"
            )

        arcpy.AddMessage("")
        arcpy.AddWarning(
            "The statistical sample-size calculation and spatial point "
            "generation will be connected after the parameter interface "
            "has been validated."
        )

        return