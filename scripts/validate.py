#!/usr/bin/env python3
"""Validate every marketplace file: schema, drift between files, and that each pinned ref, path and plugin name exist.

Set XBERG_MARKETPLACE_REMOTE_BASE (default https://github.com) to resolve repositories somewhere else, for tests.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import marketplace as mp

PLUGIN_MANIFESTS = (".claude-plugin/plugin.json", "plugin.json")


def remote_url(repo: str) -> str:
    base = os.environ.get("XBERG_MARKETPLACE_REMOTE_BASE", "https://github.com").rstrip("/")
    return f"{base}/{repo}"


def git(*args: str, cwd: str | None = None) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, env=env, check=False)


def check_schema(fmt: mp.Format, data: dict) -> list[str]:
    errs = []
    if not isinstance(data.get("name"), str) or not mp.NAME_RE.match(data["name"]):
        errs.append(f"{fmt.file}: name must be a valid identifier")
    if fmt.key != "codex" and not isinstance(data.get("owner", {}).get("name"), str):
        errs.append(f"{fmt.file}: owner.name is required")
    if fmt.key == "codex" and not isinstance(data.get("interface", {}).get("displayName"), str):
        errs.append(f"{fmt.file}: interface.displayName is required")
    seen = set()
    for i, plugin in enumerate(data.get("plugins", [])):
        where = f"{fmt.file} plugins[{i}]"
        name = plugin.get("name")
        if not isinstance(name, str) or not mp.NAME_RE.match(name):
            errs.append(f"{where}: name must be a valid identifier")
        if name in seen:
            errs.append(f"{where}: duplicate plugin name {name!r}")
        seen.add(name)
        if "version" in plugin:
            errs.append(f"{where}: version must not be set (plugin.json owns it)")
        if fmt.key == "codex":
            policy = plugin.get("policy", {})
            if policy.get("installation") not in {"AVAILABLE", "INSTALLED_BY_DEFAULT", "NOT_AVAILABLE"}:
                errs.append(f"{where}: policy.installation is invalid")
            if policy.get("authentication") not in {"ON_INSTALL", "ON_USE"}:
                errs.append(f"{where}: policy.authentication is invalid")
            if not isinstance(plugin.get("category"), str):
                errs.append(f"{where}: category is required")
    if not data.get("plugins"):
        errs.append(f"{fmt.file}: plugins is empty")
    return errs


def check_drift(by_format: dict[str, list[mp.Entry]]) -> list[str]:
    errs = []
    keys = list(by_format)
    base_key = keys[0]
    base = {e.name: e for e in by_format[base_key]}
    for key in keys[1:]:
        other = {e.name: e for e in by_format[key]}
        for name in sorted(base.keys() - other.keys()):
            errs.append(f"drift: plugin {name!r} is in {base_key} but not in {key}")
        for name in sorted(other.keys() - base.keys()):
            errs.append(f"drift: plugin {name!r} is in {key} but not in {base_key}")
        for name in sorted(base.keys() & other.keys()):
            if base[name] != other[name]:
                a, b = base[name], other[name]
                errs.append(
                    f"drift: {name!r} differs: {base_key}={a.repo}@{a.ref}:{a.path} {key}={b.repo}@{b.ref}:{b.path}"
                )
    return errs


def check_remote(entries: list[mp.Entry]) -> tuple[list[str], set[tuple[str, str]]]:
    errs = []
    bad: set[tuple[str, str]] = set()
    for repo, ref in sorted({(e.repo, e.ref) for e in entries}):
        url = remote_url(repo)
        res = git("ls-remote", "--tags", url, f"refs/tags/{ref}")
        if res.returncode != 0:
            errs.append(f"{repo}: cannot list tags at {url}: {res.stderr.strip()}")
            bad.add((repo, ref))
        elif not res.stdout.strip():
            errs.append(f"{repo}: ref {ref!r} is not an existing tag")
            bad.add((repo, ref))
    return errs, bad


def check_paths(entries: list[mp.Entry], skip: set[tuple[str, str]]) -> list[str]:
    errs = []
    for entry in sorted({(e.name, e.repo, e.path, e.ref) for e in entries}):
        name, repo, path, ref = entry
        if (repo, ref) in skip:
            continue
        with tempfile.TemporaryDirectory() as tmp:
            res = git("clone", "--quiet", "--depth", "1", "--branch", ref, "--no-checkout", remote_url(repo), tmp)
            if res.returncode != 0:
                errs.append(f"{repo}@{ref}: clone failed: {res.stderr.strip()}")
                continue
            tree = git("ls-tree", "-d", "HEAD", path, cwd=tmp)
            if tree.returncode != 0 or not tree.stdout.strip():
                errs.append(f"{repo}@{ref}: path {path!r} does not exist")
                continue
            manifest = None
            for candidate in PLUGIN_MANIFESTS:
                shown = git("show", f"HEAD:{path}/{candidate}", cwd=tmp)
                if shown.returncode == 0:
                    manifest = shown.stdout
                    break
            if manifest is None:
                errs.append(f"{repo}@{ref}: {path!r} has no plugin manifest")
                continue
            try:
                declared = json.loads(manifest).get("name")
            except json.JSONDecodeError:
                errs.append(f"{repo}@{ref}: plugin manifest in {path!r} is not valid JSON")
                continue
            if declared != name:
                errs.append(f"{repo}@{ref}: entry name {name!r} differs from plugin.json name {declared!r}")
    return errs


def validate(root: Path = mp.ROOT, offline: bool = False) -> list[str]:
    errs: list[str] = []
    by_format: dict[str, list[mp.Entry]] = {}
    for fmt in mp.FORMATS:
        try:
            data = mp.load(fmt, root)
            errs += check_schema(fmt, data)
            by_format[fmt.key] = mp.entries(fmt, data)
        except mp.MarketplaceError as exc:
            errs.append(str(exc))
    if len(by_format) > 1:
        errs += check_drift(by_format)
    if not offline and by_format:
        first = next(iter(by_format.values()))
        remote_errs, bad_refs = check_remote(first)
        errs += remote_errs + check_paths(first, bad_refs)
    return errs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=mp.ROOT)
    parser.add_argument("--offline", action="store_true", help="skip the checks that contact the product repositories")
    args = parser.parse_args()
    errs = validate(args.root, args.offline)
    for err in errs:
        print(f"error: {err}", file=sys.stderr)
    count = len(mp.entries(mp.FORMATS[0], mp.load(mp.FORMATS[0], args.root))) if not errs else 0
    print(f"{len(errs)} error(s)" if errs else f"ok: {len(mp.FORMATS)} marketplace files, {count} plugins")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
