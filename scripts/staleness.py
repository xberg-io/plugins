#!/usr/bin/env python3
"""Compare every pinned ref with the product's latest published release; exit 1 and print a report when behind.

Needs the gh CLI and a token (GH_TOKEN) for the API calls.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import marketplace as mp


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


def report(stale: list[dict[str, str]]) -> str:
    lines = ["| Plugin | Pinned | Latest release |", "| --- | --- | --- |"]
    lines += [f"| {s['name']} (`{s['repo']}`) | `{s['pinned']}` | `{s['latest']}` |" for s in stale]
    lines += ["", "Update with `python3 scripts/bump-ref.py <name> <tag>`, then `python3 scripts/validate.py`."]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=mp.ROOT)
    parser.add_argument("--json", action="store_true", help="print the stale entries as JSON")
    args = parser.parse_args()
    try:
        stale = find_stale(args.root)
    except mp.MarketplaceError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(stale, indent=2))
    elif stale:
        print(report(stale))
    else:
        print("all pinned refs match the latest release")
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
