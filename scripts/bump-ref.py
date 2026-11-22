#!/usr/bin/env python3
"""Rewrite the pinned ref of one product in every marketplace file: bump-ref.py <repo> <tag>.

<repo> is the entry name (xberg), or owner/repo. Run scripts/validate.py afterwards.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import marketplace as mp


def matches(plugin: dict[str, Any], fmt: mp.Format, target: str) -> bool:
    if "/" in target:
        repo, _, _ = mp.parse_source(fmt, plugin["source"], plugin.get("name", "?"))
        return repo == target
    return plugin.get("name") == target


def bump(target: str, tag: str, root: Path = mp.ROOT) -> list[str]:
    changed = []
    pending = []
    for fmt in mp.FORMATS:
        data = mp.load(fmt, root)
        hits = [p for p in data.get("plugins", []) if matches(p, fmt, target)]
        if not hits:
            raise mp.MarketplaceError(f"{fmt.file}: no plugin matches {target!r}")
        for plugin in hits:
            if plugin["source"].get("ref") != tag:
                plugin["source"]["ref"] = tag
                if fmt.file not in changed:
                    changed.append(fmt.file)
        pending.append((fmt, data))
    for fmt, data in pending:
        if fmt.file in changed:
            (root / fmt.file).write_text(mp.dump(data), encoding="utf-8")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("repo", help="plugin name or owner/repo")
    parser.add_argument("tag", help="release tag, for example v1.4.3")
    parser.add_argument("--root", type=Path, default=mp.ROOT)
    args = parser.parse_args()
    try:
        changed = bump(args.repo, args.tag, args.root)
    except mp.MarketplaceError as exc:
        mp.say(f"error: {exc}", error=True)
        return 1
    mp.say(
        f"{args.repo} -> {args.tag}: updated {len(changed)} file(s)"
        if changed
        else f"{args.repo} already at {args.tag}"
    )
    for name in changed:
        mp.say(f"  {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
