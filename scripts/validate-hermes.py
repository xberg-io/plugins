#!/usr/bin/env python3
"""Validate generated Hermes project-plugin bundles."""

from __future__ import annotations

import ast
import re
from pathlib import Path

import tomllib

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
PLUGINS_ROOT = REPOSITORY_ROOT / "plugins"
PLUGIN_NAMES = (
    "xberg",
    "crawlberg",
    "html-to-markdown",
    "liter-llm",
    "tree-sitter-language-pack",
)


def parse_manifest(path: Path) -> dict[str, str]:
    """Parse the scalar fields emitted in a Hermes plugin manifest."""
    fields: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([a-z_]+):\s*(.*)", line)
        if match:
            fields[match.group(1)] = match.group(2).strip().strip("\"'")
    return fields


def validate_plugin(name: str) -> None:
    """Validate one generated Hermes plugin without importing Hermes itself."""
    source_root = PLUGINS_ROOT / name / ".ai-rulez"
    plugin_root = PLUGINS_ROOT / name / ".hermes" / "plugins" / name
    entrypoint = plugin_root / "__init__.py"
    manifest_path = plugin_root / "plugin.yaml"
    package_root = PLUGINS_ROOT / name / ".hermes" / "package"
    module_name = name.replace("-", "_") + "_hermes_plugin"
    package_module_root = package_root / "src" / module_name
    package_entrypoint = package_module_root / "__init__.py"

    if not entrypoint.is_file() or not manifest_path.is_file():
        raise AssertionError(f"{name}: missing generated Hermes entrypoint or manifest")
    ast.parse(entrypoint.read_text(encoding="utf-8"), filename=str(entrypoint))

    manifest = parse_manifest(manifest_path)
    if manifest.get("name") != name:
        raise AssertionError(f"{name}: Hermes manifest name is {manifest.get('name')!r}")
    if manifest.get("kind") != "standalone":
        raise AssertionError(f"{name}: Hermes manifest kind must be 'standalone'")

    pyproject = tomllib.loads((package_root / "pyproject.toml").read_text(encoding="utf-8"))
    if pyproject["project"]["name"] != f"{name}-hermes-plugin":
        raise AssertionError(f"{name}: unexpected Hermes distribution name")
    entry_points = pyproject["project"]["entry-points"]["hermes_agent.plugins"]
    if entry_points != {name: module_name}:
        raise AssertionError(f"{name}: invalid Hermes package entry point")
    ast.parse(package_entrypoint.read_text(encoding="utf-8"), filename=str(package_entrypoint))

    source_skills_root = source_root / "skills"
    generated_skills_root = plugin_root / "skills"
    source_skills = sorted(path.relative_to(source_skills_root) for path in source_skills_root.rglob("*"))
    generated_skills = sorted(path.relative_to(generated_skills_root) for path in generated_skills_root.rglob("*"))
    if source_skills != generated_skills:
        raise AssertionError(f"{name}: generated Hermes skills do not match canonical sources")
    package_skills_root = package_module_root / "skills"
    package_skills = sorted(path.relative_to(package_skills_root) for path in package_skills_root.rglob("*"))
    if source_skills != package_skills:
        raise AssertionError(f"{name}: packaged Hermes skills do not match canonical sources")


def main() -> None:
    """Validate every marketplace member."""
    for plugin_name in PLUGIN_NAMES:
        validate_plugin(plugin_name)
    print(f"validate-hermes: {len(PLUGIN_NAMES)} project plugins are valid")


if __name__ == "__main__":
    main()
