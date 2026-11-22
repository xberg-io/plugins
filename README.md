<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://cdn.jsdelivr.net/gh/xberg-io/assets@v1/banner/readme-banner-dark.svg">
    <img alt="Xberg" width="420" src="https://cdn.jsdelivr.net/gh/xberg-io/assets@v1/banner/readme-banner-light.svg">
  </picture>
</p>

# Xberg Plugins Marketplace

A thin aggregator. This repository holds no plugin content: each marketplace entry points at the `plugin/` directory of a product repository, pinned to that product's latest published release tag. Plugins are authored, versioned and released in the product repositories.

| Plugin | Source | Pinned release |
|--------|--------|----------------|
| xberg | [xberg-io/xberg](https://github.com/xberg-io/xberg/tree/main/plugin) | see `.claude-plugin/marketplace.json` |
| crawlberg | [xberg-io/crawlberg](https://github.com/xberg-io/crawlberg/tree/main/plugin) | |
| html-to-markdown | [xberg-io/html-to-markdown](https://github.com/xberg-io/html-to-markdown/tree/main/plugin) | |
| liter-llm | [xberg-io/liter-llm](https://github.com/xberg-io/liter-llm/tree/main/plugin) | |
| tree-sitter-language-pack | [xberg-io/tree-sitter-language-pack](https://github.com/xberg-io/tree-sitter-language-pack/tree/main/plugin) | |
| poly | [Goldziher/poly](https://github.com/Goldziher/poly/tree/main/plugin) | |
| sceptre | [xberg-io/sceptre](https://github.com/xberg-io/sceptre/tree/main/plugin) | |

Each plugin bundles an MCP server launcher and skills; the tool's binary is installed on first use or via `brew install xberg-io/tap/<tool>`.

## Install

Claude Code:

```text
/plugin marketplace add xberg-io/plugins
/plugin install xberg@xberg
```

Codex CLI (then install from the plugin directory in Codex, `/plugins`):

```text
codex plugin marketplace add xberg-io/plugins
```

GitHub Copilot CLI:

```text
copilot plugin marketplace add xberg-io/plugins
copilot plugin install xberg@xberg
```

Factory Droid:

```text
droid plugin marketplace add xberg-io/plugins
droid plugin install xberg@xberg --scope user
```

Replace `xberg` before `@` with any plugin name from the table.

Not served from this marketplace:

- Cursor: its marketplace manifest only documents relative `source` paths inside the same repository, so it cannot point at a product repo. Install from the product repository's `plugin/` directory.
- Antigravity (the Gemini CLI successor): `agy plugin install` documents the official marketplace, a GitHub repository URL and a local directory, and no custom marketplaces. Our plugins live in `plugin/` of each product repository, so see each product repo's `plugin/` directory.
- opencode and Hermes packages are published by each product's own release.

## Updates

Each entry is pinned with `ref` to a release tag, and the plugin's own `plugin.json` carries the version (entries never set `version`). A user gets a new plugin version when this repository moves a ref and the client refreshes the marketplace.

- Claude Code: background auto-update is off for third-party marketplaces. Enable it under **Marketplaces** in `/plugin`, or run `/plugin marketplace update xberg`.
- Codex: `codex plugin marketplace upgrade xberg`.
- Copilot and Droid: `copilot plugin marketplace browse xberg`, `droid plugin marketplace update xberg`.

Refs are bumped with `python3 scripts/bump-ref.py <plugin> <tag>`, which rewrites every marketplace file; product release automation is intended to call it from a bot PR. A daily workflow (`staleness.yaml`) compares each ref with the product's latest release and keeps one issue open while any is behind.

## Marketplace files

| File | Harness | Source form |
|------|---------|-------------|
| `.claude-plugin/marketplace.json` | Claude Code | `git-subdir` |
| `.agents/plugins/marketplace.json` | Codex | `git-subdir` |
| `.github/plugin/marketplace.json` | GitHub Copilot | `github` with `path` (no `git-subdir` support) |
| `.factory-plugin/marketplace.json` | Factory Droid | `git-subdir` |

CI (`validate.yaml`) runs `scripts/validate.py`: JSON and schema checks, identical plugin set and refs across files, every `ref` an existing tag, every `path` present at that tag with a matching `plugin.json` name. Run `python3 -m unittest discover -s tests` for the script tests.

## Submissions

| Directory | Status |
|-----------|--------|
| Claude plugin directory | not submitted |
| MCP Registry | not submitted |
| Codex | not submitted |
| Cursor marketplace | not submitted |
| GitHub awesome-copilot | not submitted |
| Antigravity | not submitted |
| Factory | not submitted |
| OpenCode | not submitted |
| Agent Skills | not submitted |

## License

MIT. See [LICENSE](LICENSE). Report vulnerabilities per [SECURITY.md](SECURITY.md).
