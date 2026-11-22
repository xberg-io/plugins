---
type: Concept
title: Area Map
x-ai-rulez:
  kind: context
  id: area-map
  metadata:
    priority: high
---

## Area Map

Thin marketplace for the xberg-io agent plugins. No plugin content lives here: every entry points at a product repository's `plugin/` directory at a release tag.

- `.claude-plugin/`, `.agents/plugins/`, `.github/plugin/`, `.factory-plugin/` — one `marketplace.json` per harness, kept identical in plugin set and refs (`marketplace-maintenance` skill)
- `scripts/` — `marketplace.py` (shared model), `validate.py`, `bump-ref.py`, `staleness.py`
- `tests/` — unit tests for the scripts
- `.github/workflows/` — validation on PRs and a daily staleness check
