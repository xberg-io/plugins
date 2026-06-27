# Gemini CLI Gallery

## Status

Auto-indexed. No active submission required.

## How it works

The Gemini CLI gallery (`geminicli.com/extensions`) crawls public GitHub repos
that ship a `gemini-extension.json` at the repo root. Our marketplace publishes
**three** `gemini-extension.json` files (one per plugin) at
`plugins/<name>/gemini-extension.json`.

**Open question**: does the gallery index a monorepo with three nested
manifests as three entries, or does it require repo-per-plugin? Confirm by
checking the gallery within 7-10 days of publication.

## Repo URL

<https://github.com/xberg-io/plugins> — published `2026-06-08`.

## Action items if not indexed by 2026-06-22

1. Open an issue at <https://github.com/google-gemini/extensions> asking for
   monorepo support, or
2. Split the three `gemini-extension.json` files into three sibling repos
   (`xberg-io/plugin-xberg`, etc.) and have the marketplace
   register them all.
