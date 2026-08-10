from __future__ import annotations

import datetime
import platform
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FILE = PROJECT_ROOT / "project_report.md"

EXCLUDED_DIRECTORIES = {
    ".git",
    ".vscode",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "data",
    "outputs",
    "scratch",
    "temp",
    "logs",
}

INCLUDED_NAMES = {".gitignore"}

INCLUDED_SUFFIXES = {
    ".py",
    ".pyt",
    ".md",
    ".toml",
    ".yml",
    ".yaml",
    ".json",
    ".txt",
}


def is_excluded(path: Path) -> bool:
    relative_path = path.relative_to(PROJECT_ROOT)

    if any(part in EXCLUDED_DIRECTORIES for part in relative_path.parts):
        return True

    if path.name == OUTPUT_FILE.name:
        return True

    if path.name.endswith(".pyt.xml"):
        return True

    return False


def get_project_paths() -> list[Path]:
    return sorted(
        [
            path
            for path in PROJECT_ROOT.rglob("*")
            if not is_excluded(path)
        ],
        key=lambda path: str(path.relative_to(PROJECT_ROOT)).lower(),
    )


def build_tree(paths: list[Path]) -> str:
    lines = [f"{PROJECT_ROOT.name}/"]

    for path in paths:
        relative_path = path.relative_to(PROJECT_ROOT)
        indentation = "    " * (len(relative_path.parts) - 1)
        ending = "/" if path.is_dir() else ""
        lines.append(f"{indentation}├── {path.name}{ending}")

    return "\n".join(lines)


def should_include_content(path: Path) -> bool:
    if not path.is_file():
        return False

    if path.name in INCLUDED_NAMES:
        return True

    return path.suffix.lower() in INCLUDED_SUFFIXES


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


def run_git(command: list[str]) -> str:
    try:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return "Not available"


def get_arcpy_version() -> str:
    try:
        import arcpy

        return arcpy.GetInstallInfo().get("Version", "Unknown")
    except ImportError:
        return "ArcPy unavailable"


def get_language(path: Path) -> str:
    languages = {
        ".py": "python",
        ".pyt": "python",
        ".md": "markdown",
        ".json": "json",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".toml": "toml",
    }

    if path.name == ".gitignore":
        return "gitignore"

    return languages.get(path.suffix.lower(), "text")


def build_report() -> str:
    paths = get_project_paths()

    report = [
        "# ArcGIS Tools LabSIS — Project Report",
        "",
        "## Environment",
        "",
        f"- Generated: {datetime.datetime.now().isoformat(timespec='seconds')}",
        f"- Operating system: {platform.platform()}",
        f"- Python version: {platform.python_version()}",
        f"- Python executable: `{sys.executable}`",
        f"- ArcPy version: {get_arcpy_version()}",
        f"- Git branch: {run_git(['git', 'branch', '--show-current'])}",
        f"- Latest commit: {run_git(['git', 'log', '-1', '--oneline'])}",
        "",
        "## Project tree",
        "",
        "```text",
        build_tree(paths),
        "```",
        "",
        "## Project files",
        "",
    ]

    for path in paths:
        if not should_include_content(path):
            continue

        relative_path = path.relative_to(PROJECT_ROOT).as_posix()

        report.extend(
            [
                f"### `{relative_path}`",
                "",
                f"```{get_language(path)}",
                read_text(path).rstrip(),
                "```",
                "",
            ]
        )

    return "\n".join(report)


def main() -> None:
    OUTPUT_FILE.write_text(build_report(), encoding="utf-8")
    print(f"Project report generated: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()