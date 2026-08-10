from __future__ import annotations

import datetime
import platform
import re
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

EXCLUDED_NAMES = {
    ".env",
    "project_report.md",
}

INCLUDED_NAMES = {
    ".gitignore",
    "LICENSE",
    "LICENSE.md",
}

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

    if path.name in EXCLUDED_NAMES:
        return True

    if path.name.startswith(".env.") and path.name != ".env.example":
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
    children_by_parent: dict[Path, list[Path]] = {}

    for path in paths:
        children_by_parent.setdefault(path.parent, []).append(path)

    def add_children(parent: Path, prefix: str) -> None:
        children = sorted(
            children_by_parent.get(parent, []),
            key=lambda path: (not path.is_dir(), path.name.lower()),
        )

        for index, child in enumerate(children):
            is_last = index == len(children) - 1
            connector = "└──" if is_last else "├──"
            suffix = "/" if child.is_dir() else ""
            lines.append(f"{prefix}{connector} {child.name}{suffix}")

            if child.is_dir():
                child_prefix = prefix + ("    " if is_last else "│   ")
                add_children(child, child_prefix)

    add_children(PROJECT_ROOT, "")
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


def get_code_fence(content: str) -> str:
    backtick_runs = re.findall(r"`+", content)
    longest_run = max((len(run) for run in backtick_runs), default=0)
    return "`" * max(3, longest_run + 1)


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
        "# LabSIS ArcGIS Tools — Project Report",
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
        content = read_text(path).rstrip()
        fence = get_code_fence(content)

        report.extend(
            [
                f"### `{relative_path}`",
                "",
                f"{fence}{get_language(path)}",
                content,
                fence,
                "",
            ]
        )

    return "\n".join(report)


def main() -> None:
    OUTPUT_FILE.write_text(build_report(), encoding="utf-8")
    print(f"Project report generated: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()