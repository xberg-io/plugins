#!/usr/bin/env python3
"""Validate generated Codex marketplace and plugin artifacts."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGINS_ROOT = REPO_ROOT / "plugins"
MARKETPLACE_PATH = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ALLOWED_INSTALLATION = {"NOT_AVAILABLE", "AVAILABLE", "INSTALLED_BY_DEFAULT"}
ALLOWED_AUTHENTICATION = {"ON_INSTALL", "ON_USE"}
ALLOWED_MANIFEST_FIELDS = {
    "id",
    "name",
    "version",
    "description",
    "skills",
    "apps",
    "mcpServers",
    "interface",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
}
REQUIRED_INTERFACE_FIELDS = {
    "displayName",
    "shortDescription",
    "longDescription",
    "developerName",
    "category",
    "capabilities",
}
PROVENANCE_FILE = ".ai-rulez-generated.json"
HASH = re.compile(r"^blake3:[0-9a-f]{64}$")
JS_HEADER = re.compile(
    rb"\A// AI-RULEZ :: GENERATED FILE \xe2\x80\x94 DO NOT EDIT\n"
    rb"// Content-Hash: (blake3:[0-9a-f]{64})\n"
    rb"// Source-Hash: (blake3:[0-9a-f]{64})\n"
    rb"// Schema-Version: v1\n\n"
)
PYTHON_HEADER = re.compile(
    rb"\A# AI-RULEZ :: GENERATED FILE \xe2\x80\x94 DO NOT EDIT\n"
    rb"# Content-Hash: (blake3:[0-9a-f]{64})\n"
    rb"# Source-Hash: (blake3:[0-9a-f]{64})\n"
    rb"# Schema-Version: v1\n\n"
)
MARKDOWN_HEADER = re.compile(
    rb"\n?<!--\nAI-RULEZ :: GENERATED FILE \xe2\x80\x94 DO NOT EDIT\n"
    rb"Content-Hash: (blake3:[0-9a-f]{64})\n"
    rb"Source-Hash: (blake3:[0-9a-f]{64})\n"
    rb"Schema-Version: v1\n-->\n\n"
)


def load_json(path: Path, errors: list[str]) -> dict[str, Any] | None:
    if not path.is_file():
        errors.append(f"missing {path.relative_to(REPO_ROOT)}")
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"invalid JSON in {path.relative_to(REPO_ROOT)}: {error}")
        return None
    if not isinstance(payload, dict):
        errors.append(f"{path.relative_to(REPO_ROOT)} must contain a JSON object")
        return None
    return payload


def blake3_hash(content: bytes, errors: list[str]) -> str | None:
    executable = shutil.which("b3sum")
    if executable is None:
        errors.append("b3sum is required to validate generated provenance hashes")
        return None
    result = subprocess.run([executable, "--no-names"], input=content, capture_output=True, check=False)
    if result.returncode != 0:
        errors.append(f"b3sum failed: {result.stderr.decode(errors='replace').strip()}")
        return None
    return f"blake3:{result.stdout.decode().strip()}"


def strip_generated_header(path: Path, content: bytes, errors: list[str]) -> tuple[bytes, str | None, str | None]:
    extension = path.suffix.lower()
    if extension in {".js", ".jsx", ".ts", ".tsx"}:
        match = JS_HEADER.match(content)
        if match is None:
            errors.append(f"{path.relative_to(REPO_ROOT)}: missing or invalid generated-file header")
            return content, None, None
        return content[match.end() :], match.group(1).decode(), match.group(2).decode()
    if extension == ".py":
        match = PYTHON_HEADER.match(content)
        if match is None:
            errors.append(f"{path.relative_to(REPO_ROOT)}: missing or invalid generated-file header")
            return content, None, None
        return content[match.end() :], match.group(1).decode(), match.group(2).decode()
    if extension not in {".md", ".mdx", ".markdown"}:
        return content, None, None

    offset = 0
    if content.startswith(b"---\n"):
        closing = content.find(b"\n---\n", 4)
        if closing >= 0:
            offset = closing + len(b"\n---\n")
    match = MARKDOWN_HEADER.match(content, offset)
    if match is None:
        errors.append(f"{path.relative_to(REPO_ROOT)}: missing or invalid generated-file header")
        return content, None, None
    separator = b"\n" if offset > 0 else b""
    return content[:offset] + separator + content[match.end() :], match.group(1).decode(), match.group(2).decode()


def validate_provenance(bundle_root: Path, errors: list[str]) -> None:
    sidecar_path = bundle_root / PROVENANCE_FILE
    sidecar = load_json(sidecar_path, errors)
    if sidecar is None:
        return
    if set(sidecar) != {"schema_version", "source_hash", "outputs"}:
        errors.append(f"{sidecar_path.relative_to(REPO_ROOT)}: unexpected provenance fields")
        return
    source_hash = sidecar.get("source_hash")
    outputs = sidecar.get("outputs")
    if sidecar.get("schema_version") != "v1" or not isinstance(source_hash, str) or HASH.fullmatch(source_hash) is None:
        errors.append(f"{sidecar_path.relative_to(REPO_ROOT)}: invalid schema or source hash")
        return
    if not isinstance(outputs, dict) or not outputs:
        errors.append(f"{sidecar_path.relative_to(REPO_ROOT)}: outputs must be a non-empty object")
        return

    computed: dict[str, str] = {}
    for relative_path, entry in outputs.items():
        if (
            not isinstance(relative_path, str)
            or PurePosixPath(relative_path).is_absolute()
            or ".." in PurePosixPath(relative_path).parts
        ):
            errors.append(f"{sidecar_path.relative_to(REPO_ROOT)}: invalid output path {relative_path!r}")
            continue
        if relative_path == PROVENANCE_FILE or not isinstance(entry, dict) or set(entry) != {"content_hash"}:
            errors.append(f"{sidecar_path.relative_to(REPO_ROOT)}: invalid output entry {relative_path!r}")
            continue
        expected_hash = entry.get("content_hash")
        if not isinstance(expected_hash, str) or HASH.fullmatch(expected_hash) is None:
            errors.append(f"{sidecar_path.relative_to(REPO_ROOT)}: invalid content hash for {relative_path}")
            continue
        output_path = bundle_root.joinpath(*PurePosixPath(relative_path).parts)
        if not output_path.is_file():
            errors.append(f"{sidecar_path.relative_to(REPO_ROOT)}: missing output {relative_path}")
            continue
        body, header_hash, header_source_hash = strip_generated_header(output_path, output_path.read_bytes(), errors)
        actual_hash = blake3_hash(body, errors)
        if actual_hash is None:
            return
        computed[relative_path] = actual_hash
        if actual_hash != expected_hash:
            errors.append(f"{output_path.relative_to(REPO_ROOT)}: content hash does not match provenance sidecar")
        if header_hash is not None and (header_hash != expected_hash or header_source_hash != source_hash):
            errors.append(f"{output_path.relative_to(REPO_ROOT)}: generated header does not match provenance sidecar")

    source_input = "schema=v1\n" + "".join(f"{path}={computed[path]}\n" for path in sorted(computed))
    actual_source_hash = blake3_hash(source_input.encode(), errors)
    if actual_source_hash is not None and actual_source_hash != source_hash:
        errors.append(f"{sidecar_path.relative_to(REPO_ROOT)}: source hash does not match outputs")


def validate_relative_path(plugin_root: Path, raw_path: Any, field: str, errors: list[str]) -> Path | None:
    if not isinstance(raw_path, str) or not raw_path.startswith("./"):
        errors.append(f"{plugin_root.name}: {field} must be a relative path starting with ./")
        return None
    relative = PurePosixPath(raw_path[2:])
    if not relative.parts or any(part in {"", ".", ".."} for part in relative.parts):
        errors.append(f"{plugin_root.name}: {field} must stay inside the plugin directory")
        return None
    path = plugin_root.joinpath(*relative.parts)
    if not path.exists():
        errors.append(f"{plugin_root.name}: {field} points to missing {raw_path}")
        return None
    return path


def validate_skill(skill_path: Path, errors: list[str]) -> None:
    relative = skill_path.relative_to(REPO_ROOT)
    content = skill_path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---(?:\n|\Z)", content, re.DOTALL)
    if match is None:
        errors.append(f"{relative}: missing closed YAML frontmatter")
        return
    frontmatter = match.group(1)
    name_match = re.search(r"^name:\s*['\"]?([^'\"\n]+)", frontmatter, re.MULTILINE)
    description_match = re.search(
        r"^description:\s*(?:(?:>-?|\|-?)\s*\n((?:[ \t]+.*\n?)*)|['\"]?([^'\"\n]+))",
        frontmatter,
        re.MULTILINE,
    )
    if name_match is None or not name_match.group(1).strip():
        errors.append(f"{relative}: frontmatter name must be non-empty")
    elif name_match.group(1).strip() != skill_path.parent.name:
        errors.append(f"{relative}: frontmatter name must match directory {skill_path.parent.name}")
    if description_match is None:
        errors.append(f"{relative}: frontmatter description must be non-empty")
        return
    description = (description_match.group(1) or description_match.group(2) or "").strip()
    if not description:
        errors.append(f"{relative}: frontmatter description must be non-empty")
    if "<" in description or ">" in description:
        errors.append(f"{relative}: frontmatter description cannot contain angle brackets")


def validate_mcp(plugin_root: Path, manifest: dict[str, Any], errors: list[str]) -> None:
    value = manifest.get("mcpServers")
    if value != "./.mcp.json":
        errors.append(f"{plugin_root.name}: mcpServers must be ./.mcp.json")
        return
    mcp_path = validate_relative_path(plugin_root, value, "mcpServers", errors)
    if mcp_path is None:
        return
    payload = load_json(mcp_path, errors)
    if payload is None:
        return
    servers = payload.get("mcpServers")
    if not isinstance(servers, dict) or not servers:
        errors.append(f"{plugin_root.name}: .mcp.json mcpServers must be a non-empty object")
        return
    for server_name, server in servers.items():
        if not isinstance(server_name, str) or not server_name or not isinstance(server, dict):
            errors.append(f"{plugin_root.name}: invalid MCP server entry")
            continue
        command = server.get("command")
        command_path = validate_relative_path(plugin_root, command, f"MCP server {server_name} command", errors)
        if command_path is not None and not command_path.is_file():
            errors.append(f"{plugin_root.name}: MCP command must be a file")
        if command_path is not None and command_path.stat().st_mode & 0o111 == 0:
            errors.append(f"{plugin_root.name}: MCP command {command} is not executable")


def validate_plugin(plugin_root: Path, errors: list[str]) -> None:
    manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
    manifest = load_json(manifest_path, errors)
    if manifest is None:
        return
    unknown_fields = set(manifest) - ALLOWED_MANIFEST_FIELDS
    if unknown_fields:
        errors.append(f"{plugin_root.name}: unsupported manifest fields: {', '.join(sorted(unknown_fields))}")
    name = manifest.get("name")
    if name != plugin_root.name or not isinstance(name, str) or NAME.fullmatch(name) is None:
        errors.append(f"{plugin_root.name}: manifest name must match its kebab-case directory name")
    version = manifest.get("version")
    if not isinstance(version, str) or SEMVER.fullmatch(version) is None:
        errors.append(f"{plugin_root.name}: version must be strict semver")
    for field in ("description", "author", "interface"):
        if not manifest.get(field):
            errors.append(f"{plugin_root.name}: missing required manifest field {field}")
    author = manifest.get("author")
    if isinstance(author, dict) and not isinstance(author.get("name"), str):
        errors.append(f"{plugin_root.name}: author.name must be a string")
    interface = manifest.get("interface")
    if isinstance(interface, dict):
        missing_interface = {field for field in REQUIRED_INTERFACE_FIELDS if not interface.get(field)}
        if "defaultPrompt" not in interface and "default_prompt" not in interface:
            missing_interface.add("defaultPrompt")
        if missing_interface:
            errors.append(
                f"{plugin_root.name}: missing required interface fields: {', '.join(sorted(missing_interface))}"
            )
        capabilities = interface.get("capabilities")
        if capabilities is not None and (
            not isinstance(capabilities, list) or not all(isinstance(item, str) and item for item in capabilities)
        ):
            errors.append(f"{plugin_root.name}: interface.capabilities must be an array of strings")
        for field in ("composerIcon", "logo", "logoDark"):
            if field in interface:
                validate_relative_path(plugin_root, interface[field], f"interface.{field}", errors)
    skills = validate_relative_path(plugin_root, manifest.get("skills"), "skills", errors)
    if skills is not None and skills.is_dir():
        skill_files = sorted(skills.glob("*/SKILL.md"))
        if not skill_files:
            errors.append(f"{plugin_root.name}: skills directory contains no skills")
        for skill_file in skill_files:
            validate_skill(skill_file, errors)
    validate_mcp(plugin_root, manifest, errors)
    for json_path in sorted(plugin_root.rglob("*.json")):
        load_json(json_path, errors)
    for shell_path in sorted(plugin_root.rglob("*.sh")):
        if shell_path.stat().st_mode & 0o111 == 0:
            errors.append(f"{shell_path.relative_to(REPO_ROOT)}: shell launcher is not executable")
        result = subprocess.run(["bash", "-n", str(shell_path)], capture_output=True, text=True, check=False)
        if result.returncode != 0:
            errors.append(f"{shell_path.relative_to(REPO_ROOT)}: invalid shell syntax: {result.stderr.strip()}")


def validate_marketplace(plugin_names: set[str], errors: list[str]) -> None:
    marketplace = load_json(MARKETPLACE_PATH, errors)
    if marketplace is None:
        return
    if not isinstance(marketplace.get("name"), str) or not marketplace["name"].strip():
        errors.append(".agents/plugins/marketplace.json: name must be non-empty")
    entries = marketplace.get("plugins")
    if not isinstance(entries, list):
        errors.append(".agents/plugins/marketplace.json: plugins must be an array")
        return
    seen: set[str] = set()
    for index, entry in enumerate(entries):
        label = f"marketplace plugin[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label}: must be an object")
            continue
        name = entry.get("name")
        if not isinstance(name, str) or name not in plugin_names:
            errors.append(f"{label}: name must match a plugin directory")
            continue
        seen.add(name)
        source = entry.get("source")
        expected_path = f"./plugins/{name}"
        if not isinstance(source, dict) or source.get("source") != "local" or source.get("path") != expected_path:
            errors.append(f"{label}: source must be local path {expected_path}")
        policy = entry.get("policy")
        if not isinstance(policy, dict):
            errors.append(f"{label}: policy must be an object")
        else:
            if policy.get("installation") not in ALLOWED_INSTALLATION:
                errors.append(f"{label}: invalid policy.installation")
            if policy.get("authentication") not in ALLOWED_AUTHENTICATION:
                errors.append(f"{label}: invalid policy.authentication")
        if not isinstance(entry.get("category"), str) or not entry["category"].strip():
            errors.append(f"{label}: category must be non-empty")
    missing = plugin_names - seen
    extra = seen - plugin_names
    if missing:
        errors.append(f"marketplace is missing plugins: {', '.join(sorted(missing))}")
    if extra:
        errors.append(f"marketplace contains unknown plugins: {', '.join(sorted(extra))}")


def main() -> int:
    errors: list[str] = []
    plugin_roots = sorted(path for path in PLUGINS_ROOT.iterdir() if path.is_dir() and not path.name.startswith("."))
    if not plugin_roots:
        errors.append("plugins directory contains no plugins")
    for plugin_root in plugin_roots:
        validate_plugin(plugin_root, errors)
        validate_provenance(plugin_root, errors)
    validate_marketplace({path.name for path in plugin_roots}, errors)
    validate_provenance(REPO_ROOT, errors)
    if errors:
        print("Codex validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Codex validation passed for {len(plugin_roots)} plugins")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
