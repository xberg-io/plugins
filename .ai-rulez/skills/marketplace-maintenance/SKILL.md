---
type: Playbook
title: Marketplace Maintenance
description: "Plugin marketplace upkeep: refs are release tags, every harness file stays identical, bump with bump-ref.py and validate before pushing. Use when editing a marketplace.json or moving a plugin ref."
paths:
  - ".claude-plugin/**"
  - ".agents/plugins/**"
  - ".github/plugin/**"
  - ".factory-plugin/**"
  - "scripts/**"
x-ai-rulez:
  kind: skill
  id: marketplace-maintenance
  metadata:
    name: marketplace-maintenance
---

## Marketplace maintenance

Each product repository owns its plugin in `plugin/`. This repository only pins which release of it each marketplace serves.

- Move a ref with `python3 scripts/bump-ref.py <name-or-owner/repo> <tag>`; it rewrites every marketplace file. Never edit one file by hand: the files must agree on plugin set, repository, path and ref.
- A ref is an existing release tag, never a branch. `scripts/validate.py` checks the tag exists and that `plugin/` at that tag carries a `plugin.json` with the entry's name.
- Entries never set `version`; the plugin's own `plugin.json` is the source of the version.
- Before pushing: `python3 -m unittest discover -s tests` and `python3 scripts/validate.py`.
- Cursor is not served from here: its marketplace format cannot point at another repository.
- `scripts/staleness.py` (daily workflow) finds refs behind the latest release; with `--apply` it bumps them, and the workflow keeps one bot PR (`bot/bump-plugin-refs`) open with the bump.
