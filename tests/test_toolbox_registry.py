from __future__ import annotations

import importlib.util
import runpy
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TOOLBOX_PATH = PROJECT_ROOT / "ArcGISTools.pyt"
TOOL_PATH = (
    PROJECT_ROOT
    / "src"
    / "labsis_arcgis_tools"
    / "validation_sampling"
    / "tool.py"
)

ARCPY_AVAILABLE = importlib.util.find_spec("arcpy") is not None


class SourceFileTests(unittest.TestCase):
    def test_validation_tool_compiles(self):
        source = TOOL_PATH.read_text(encoding="utf-8")
        compile(source, str(TOOL_PATH), "exec")

    def test_minimum_distance_default(self):
        source = TOOL_PATH.read_text(encoding="utf-8")
        self.assertIn(
            'minimum_distance.value = "100 Meters"',
            source,
        )


@unittest.skipUnless(
    ARCPY_AVAILABLE,
    "ArcPy is required to load the ArcGIS Pro toolbox.",
)
class ToolboxRegistryTests(unittest.TestCase):
    def test_toolbox_registration(self):
        namespace = runpy.run_path(str(TOOLBOX_PATH))
        toolbox = namespace["Toolbox"]()

        self.assertEqual(
            toolbox.label,
            "LabSIS ArcGIS Tools",
        )
        self.assertEqual(
            toolbox.alias,
            "labsis_arcgis_tools",
        )
        self.assertEqual(
            [tool.__name__ for tool in toolbox.tools],
            ["GenerateValidationSample"],
        )


if __name__ == "__main__":
    unittest.main()