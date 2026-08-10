"""LabSIS ArcGIS Pro Python toolbox."""

from __future__ import annotations

import sys
from pathlib import Path


TOOLBOX_DIRECTORY = Path(__file__).resolve().parent
SOURCE_DIRECTORY = TOOLBOX_DIRECTORY / "src"

if str(SOURCE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIRECTORY))

from labsis_arcgis_tools.validation_sampling import GenerateValidationSample


class Toolbox:
    """Register the ArcGIS Pro tools included in this toolbox."""

    def __init__(self):
        self.label = "LabSIS ArcGIS Tools"
        self.alias = "labsis_arcgis_tools"

        self.tools = [
            GenerateValidationSample,
        ]