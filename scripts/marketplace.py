"""Shared model of the marketplace files: where they live, how each encodes an entry, and how to read and write them."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
GITHUB = "https://github.com/"
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


@dataclass(frozen=True)
class Entry:
    name: str
    repo: str
    path: str
    ref: str


@dataclass(frozen=True)
class Format:
    key: str
    file: str
    source_type: str


FORMATS = [
    Format("claude", ".claude-plugin/marketplace.json", "git-subdir"),
    Format("codex", ".agents/plugins/marketplace.json", "git-subdir"),
    Format("copilot", ".github/plugin/marketplace.json", "github"),
    Format("factory", ".factory-plugin/marketplace.json", "git-subdir"),
]


class MarketplaceError(Exception):
    pass


def say(message: str, *, error: bool = False) -> None:
    """Write one line to stdout, or to stderr for an error."""
    (sys.stderr if error else sys.stdout).write(message + "\n")


def repo_from_url(url: str) -> str:
    if not url.startswith(GITHUB):
        raise MarketplaceError(f"url {url!r} is not a {GITHUB} URL")
    repo = url[len(GITHUB) :].removesuffix(".git").strip("/")
    if repo.count("/") != 1:
        raise MarketplaceError(f"url {url!r} is not owner/repo")
    return repo


def parse_source(fmt: Format, source: object, where: str) -> tuple[str, str, str]:
    if not isinstance(source, dict):
        raise MarketplaceError(f"{where}: source must be an object, got {type(source).__name__}")
    if source.get("source") != fmt.source_type:
        raise MarketplaceError(f"{where}: source.source must be {fmt.source_type!r}, got {source.get('source')!r}")
    if fmt.source_type == "github":
        repo = source.get("repo")
        if not isinstance(repo, str) or repo.count("/") != 1:
            raise MarketplaceError(f"{where}: source.repo must be owner/repo")
    else:
        url = source.get("url")
        if not isinstance(url, str):
            raise MarketplaceError(f"{where}: source.url is required")
        repo = repo_from_url(url)
    path, ref = source.get("path"), source.get("ref")
    if not isinstance(path, str) or not path:
        raise MarketplaceError(f"{where}: source.path is required")
    if not isinstance(ref, str) or not ref:
        raise MarketplaceError(f"{where}: source.ref is required")
    if "sha" in source:
        raise MarketplaceError(f"{where}: source.sha is not used; pin with ref")
    return repo, path.removeprefix("./"), ref


def make_source(fmt: Format, repo: str, path: str, ref: str) -> dict[str, Any]:
    if fmt.source_type == "github":
        return {"source": "github", "repo": repo, "path": path, "ref": ref}
    path = f"./{path}" if fmt.key == "codex" else path
    return {"source": "git-subdir", "url": f"{GITHUB}{repo}.git", "path": path, "ref": ref}


def load(fmt: Format, root: Path = ROOT) -> dict[str, Any]:
    p = root / fmt.file
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise MarketplaceError(f"{fmt.file}: file is missing") from None
    except json.JSONDecodeError as exc:
        raise MarketplaceError(f"{fmt.file}: invalid JSON: {exc}") from None
    if not isinstance(data, dict):
        raise MarketplaceError(f"{fmt.file}: top level must be an object")
    return data


def entries(fmt: Format, data: dict[str, Any]) -> list[Entry]:
    plugins = data.get("plugins")
    if not isinstance(plugins, list):
        raise MarketplaceError(f"{fmt.file}: plugins must be an array")
    out = []
    for i, plugin in enumerate(plugins):
        where = f"{fmt.file} plugins[{i}]"
        if not isinstance(plugin, dict) or not isinstance(plugin.get("name"), str):
            raise MarketplaceError(f"{where}: name is required")
        repo, path, ref = parse_source(fmt, plugin.get("source"), where)
        out.append(Entry(plugin["name"], repo, path, ref))
    return out


def dump(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"
