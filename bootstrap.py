"""Configures a new project created from modele."""

from __future__ import annotations

import argparse
import json
import keyword
import re
from dataclasses import dataclass
from pathlib import Path

TEMPLATE_DESCRIPTION = "An opinionated Python project template."
TEMPLATE_NAME = "modele"


@dataclass(frozen=True)
class ProjectInfo:
    """Identifying metadata for the project being configured."""

    project_name: str
    module_name: str
    description: str


def main() -> None:
    """Configures the project from command-line arguments or prompts."""
    arguments = _parse_arguments()
    root = Path.cwd()
    project_name = (arguments.name or root.name).lower()
    module_name = re.sub(r"[-.]+", "_", project_name)
    description = arguments.description or input("Project description: ").strip()
    package = arguments.package
    if package is None:
        package = _confirm("Build a distributable package?")
    docs = arguments.docs
    if docs is None:
        docs = "mkdocs" if _confirm("Add MkDocs?") else "none"

    info = ProjectInfo(project_name, module_name, description)
    _validate_inputs(root, info)
    _configure_pyproject(root, info, package, docs)
    _configure_python(root, module_name)
    _configure_readme(root, project_name)
    _configure_makefile(root, module_name, package, docs)
    if docs == "mkdocs":
        _create_docs(root, project_name)

    Path(__file__).unlink()
    print(f"Configured {project_name}.")


def _parse_arguments() -> argparse.Namespace:
    """Returns setup arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--name")
    parser.add_argument("--description")
    parser.add_argument(
        "--package",
        action=argparse.BooleanOptionalAction,
        default=None,
    )
    parser.add_argument("--docs", choices=("none", "mkdocs"))
    return parser.parse_args()


def _confirm(prompt: str) -> bool:
    """Returns whether the user confirmed a setup choice."""
    return input(f"{prompt} [y/N] ").strip().lower() in {"y", "yes"}


def _validate_inputs(
    root: Path,
    info: ProjectInfo,
) -> None:
    """Raises SystemExit when setup inputs or template state are invalid."""
    if not re.fullmatch(r"[a-z0-9]+(?:[-._][a-z0-9]+)*", info.project_name):
        raise SystemExit(f"Invalid project name: {info.project_name!r}.")
    if not info.module_name.isidentifier() or keyword.iskeyword(info.module_name):
        raise SystemExit(f"Invalid Python module name: {info.module_name!r}.")
    if not info.description:
        raise SystemExit("Project description cannot be empty.")
    required = (
        root / "pyproject.toml",
        root / TEMPLATE_NAME,
        root / "tests/test_modele.py",
    )
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit(f"Template files are missing: {', '.join(missing)}.")


def _configure_pyproject(
    root: Path,
    info: ProjectInfo,
    package: bool,
    docs: str,
) -> None:
    """Updates project metadata and optional tool configuration."""
    path = root / "pyproject.toml"
    text = path.read_text()
    description_key = f'description = "{TEMPLATE_DESCRIPTION}"'
    replacements = {
        'name = "modele"': f"name = {json.dumps(info.project_name)}",
        description_key: f"description = {json.dumps(info.description)}",
        'source = ["modele"]': f'source = ["{info.module_name}"]',
        'root_packages = ["modele"]': f'root_packages = ["{info.module_name}"]',
        'ancestors = ["modele"]': f'ancestors = ["{info.module_name}"]',
    }
    for old, new in replacements.items():
        if text.count(old) != 1:
            raise SystemExit(f"Expected one {old!r} entry in pyproject.toml.")
        text = text.replace(old, new)

    if not package:
        build_system = (
            "\n[build-system]\n"
            'requires = ["hatchling"]\n'
            'build-backend = "hatchling.build"\n'
        )
        if text.count(build_system) != 1:
            raise SystemExit(
                "Expected the default build-system block in pyproject.toml."
            )
        text = text.replace(build_system, "\n")

    if docs == "mkdocs":
        dependency_groups = "[dependency-groups]\n"
        if text.count(dependency_groups) != 1:
            raise SystemExit("Expected one dependency-groups table in pyproject.toml.")
        text = text.replace(
            dependency_groups,
            '[dependency-groups]\ndocs = ["mkdocs-material>=9"]\n',
        )

    path.write_text(text)


def _configure_python(root: Path, module_name: str) -> None:
    """Renames the import package and its seed test."""
    source = root / TEMPLATE_NAME
    destination = root / module_name
    if destination.exists():
        raise SystemExit(f"Destination already exists: {destination}.")
    source.rename(destination)

    package_init = destination / "__init__.py"
    package_init.write_text(
        package_init.read_text().replace(
            '"""The modele package."""',
            f'"""The {module_name} package."""',
        )
    )

    tests_init = root / "tests/__init__.py"
    tests_init.write_text(
        tests_init.read_text().replace(
            '"""The modele tests."""',
            f'"""The {module_name} tests."""',
        )
    )

    old_test = root / "tests/test_modele.py"
    new_test = root / f"tests/test_{module_name}.py"
    test_text = (
        old_test.read_text()
        .replace(
            '"""Tests for modele."""',
            f'"""Tests for {module_name}."""',
        )
        .replace("from modele", f"from {module_name}")
    )
    new_test.write_text(test_text)
    old_test.unlink()


def _configure_readme(root: Path, project_name: str) -> None:
    """Updates the README title and removes template-only prose."""
    path = root / "README.md"
    text = path.read_text()
    text = re.sub(
        r"^# modele.*$", f"# {project_name}", text, count=1, flags=re.MULTILINE
    )
    text = text.replace("The modele Python project template.\n", "")
    path.write_text(text)


def _configure_makefile(
    root: Path,
    module_name: str,
    package: bool,
    docs: str,
) -> None:
    """Adds targets selected during setup."""
    path = root / "Makefile"
    text = path.read_text()
    targets: list[str] = []
    phony: list[str] = []

    if package:
        targets.append(
            "dist:\n"
            "\trm -rf dist\n"
            "\tuv build --wheel\n"
            "\tuv run --isolated --with $$(find dist -type f -name '*.whl') "
            f'python -c "import {module_name}"\n'
        )
        phony.append("dist")

    if docs == "mkdocs":
        targets.append("docs:\n\tuv run --group docs mkdocs build --strict\n")
        phony.append("docs")

    if targets:
        marker = "#" * 80 + "\n\n.PHONY:"
        if text.count(marker) != 1:
            raise SystemExit("Expected one Makefile target marker.")
        text = text.replace(marker, "\n".join(targets) + "\n" + marker)
        text = text.replace(
            ".PHONY: \\\n", ".PHONY: \\\n" + "".join(f"\t{name} \\\n" for name in phony)
        )
        path.write_text(text)


def _create_docs(root: Path, project_name: str) -> None:
    """Creates local MkDocs configuration without choosing a host."""
    docs = root / "docs"
    docs.mkdir()
    (docs / "index.md").write_text(f"# {project_name}\n")
    (root / "mkdocs.yml").write_text(
        f"site_name: {project_name}\n"
        "theme:\n"
        "  name: material\n"
        "nav:\n"
        "  - Home: index.md\n"
    )


if __name__ == "__main__":
    main()
