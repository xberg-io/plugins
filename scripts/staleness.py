#!/usr/bin/env python3
"""Compare every pinned ref with the product's latest published release; exit 1 and print a report when behind.

With --apply, also move every stale ref to its latest release in all marketplace files (the report then serves as the
bump pull request's description). Needs the gh CLI and a token (GH_TOKEN) for the API calls.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import marketplace as mp

if TYPE_CHECKING:
    from collections.abc import Callable


def latest_release(repo: str) -> str:
    res = subprocess.run(
        ["gh", "api", f"repos/{repo}/releases/latest", "--jq", ".tag_name"], capture_output=True, text=True, check=False
    )
    tag = res.stdout.strip()
    if res.returncode != 0 or not tag:
        raise mp.MarketplaceError(f"{repo}: cannot read the latest release: {res.stderr.strip() or 'empty tag'}")
    return tag


def find_stale(root: Path = mp.ROOT, fetch: Callable[[str], str] = latest_release) -> list[dict[str, str]]:
    fmt = mp.FORMATS[0]
    stale = []
    for entry in mp.entries(fmt, mp.load(fmt, root)):
        latest = fetch(entry.repo)
        if latest != entry.ref:
            stale.append({"name": entry.name, "repo": entry.repo, "pinned": entry.ref, "latest": latest})
    return stale


def _bump_module():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("bump_ref", Path(__file__).with_name("bump-ref.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def apply(stale: list[dict[str, str]], root: Path = mp.ROOT) -> None:
    bump = _bump_module().bump
    for entry in stale:
        bump(entry["repo"], entry["latest"], root)


def report(stale: list[dict[str, str]], *, applied: bool = False) -> str:
    lines = ["| Plugin | Pinned | Latest release |", "| --- | --- | --- |"]
    lines += [f"| {s['name']} (`{s['repo']}`) | `{s['pinned']}` | `{s['latest']}` |" for s in stale]
    if applied:
        lines += ["", "Moves each ref above to the product's latest release in every marketplace file."]
    else:
        lines += ["", "Update with `python3 scripts/bump-ref.py <name> <tag>`, then `python3 scripts/validate.py`."]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=mp.ROOT)
    parser.add_argument("--json", action="store_true", help="print the stale entries as JSON")
    parser.add_argument("--apply", action="store_true", help="move every stale ref to its latest release")
    args = parser.parse_args()
    try:
        stale = find_stale(args.root)
        if args.apply:
            apply(stale, args.root)
    except mp.MarketplaceError as exc:
        mp.say(f"error: {exc}", error=True)
        return 2
    if args.json:
        mp.say(json.dumps(stale, indent=2))
    elif stale:
        mp.say(report(stale, applied=args.apply))
    else:
        mp.say("all pinned refs match the latest release")
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
