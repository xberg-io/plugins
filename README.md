# Kreuzberg Plugins Marketplace

Document-intelligence plugins for coding agents. Install one, two, or all three into Claude Code, Codex CLI, Cursor, Gemini CLI, Factory Droid, GitHub Copilot CLI, or opencode.

## Badges

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/kreuzberg-dev/plugins/blob/main/LICENSE)
[![Version: 0.1.0](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/kreuzberg-dev/plugins/releases)
[![GitHub stars](https://img.shields.io/github/stars/kreuzberg-dev/plugins?style=social)](https://github.com/kreuzberg-dev/plugins)
[![Discord](https://img.shields.io/badge/Discord-Chat-007ec6?logo=discord&logoColor=white)](https://discord.gg/xt9WY3GnKR)

## What You Get

| Plugin | Value Proposition | Status |
|--------|-------------------|--------|
| **kreuzberg** | Local document extraction from 91+ formats (PDF, Office, images with OCR, HTML, email, archives, academic) | Stable — v0.1.0 |
| **kreuzcrawl** | Web crawling and scraping with HTML→Markdown and headless-Chrome fallback | Stable — v0.1.0 |
| **kreuzberg-cloud** | Managed extraction via `api.kreuzberg.dev` | Skills-only — MCP server lands in v0.2.0 |

## Install

### Claude Code

Once approved by the marketplace:

```text
/plugin install kreuzberg@claude-community
/plugin install kreuzcrawl@claude-community
/plugin install kreuzberg-cloud@claude-community
```

Self-host (works today):

```text
/plugin marketplace add kreuzberg-dev/plugins
/plugin install kreuzberg@kreuzberg
/plugin install kreuzcrawl@kreuzberg
/plugin install kreuzberg-cloud@kreuzberg
```

Pending review for official Claude marketplace.

### Codex CLI

Codex CLI marketplace is not yet open for third-party submissions. Use self-hosted install:

```text
/plugins add https://github.com/kreuzberg-dev/plugins
```

Then search for `kreuzberg`, `kreuzcrawl`, or `kreuzberg-cloud` and select "Install Plugin".

### Cursor

Self-host install only:

Settings → Plugins → Add from URL → `https://github.com/kreuzberg-dev/plugins`. Select the plugin(s) you want.

### Gemini CLI

Self-host install:

```text
gemini extensions install https://github.com/kreuzberg-dev/plugins
```

### Factory Droid

Self-host install:

```text
droid plugin marketplace add https://github.com/kreuzberg-dev/plugins
droid plugin install kreuzberg@kreuzberg
droid plugin install kreuzcrawl@kreuzberg
droid plugin install kreuzberg-cloud@kreuzberg
```

Pending review for official Factory Droid marketplace.

### GitHub Copilot CLI

Self-host install:

```text
copilot plugin marketplace add https://github.com/kreuzberg-dev/plugins
copilot plugin install kreuzberg@kreuzberg
copilot plugin install kreuzcrawl@kreuzberg
copilot plugin install kreuzberg-cloud@kreuzberg
```

### opencode

Add the published packages to `opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["@kreuzberg/opencode-kreuzberg", "@kreuzberg/opencode-kreuzcrawl"]
}
```

`kreuzberg-cloud` is skills-only in v0.1.0 and is not published as an opencode package yet.

## Binary Requirements

Each plugin shells out to a real CLI. Install whichever you use:

| Plugin | Binary | Install |
|--------|--------|---------|
| kreuzberg | `kreuzberg` | `brew install kreuzberg-dev/tap/kreuzberg` |
| kreuzcrawl | `kreuzcrawl` | `brew install kreuzberg-dev/tap/kreuzcrawl` |
| kreuzberg-cloud | `kreuzberg-cloud` (v0.2.0) | — (skills-only in v0.1.0) |

For `kreuzberg-cloud`, set the API key via `KREUZBERG_API_KEY` environment variable or `~/.kreuzberg/cloud.toml`.

## How Agent Skills Work

Each plugin ships SKILL.md files describing what it can do. Agent harnesses auto-load skills based on the `description:` frontmatter in each file. When you ask your agent to extract a document or crawl a site, the matching skill fires automatically — you don't invoke skills directly.

Example: when you say "extract text and tables from this PDF", the `kreuzberg` skill detects the request and loads the `extract` MCP tool from the local `kreuzberg` binary. The agent then calls that tool with your document, getting back structured text, tables, and metadata. The same pattern applies to web crawling with `kreuzcrawl` and cloud extraction with `kreuzberg-cloud`.

Skills are loaded at agent startup. Their descriptions stay in context so agents can decide when to use them. This means skills consume zero tokens unless the agent decides to invoke them.

## Layout

```text
.claude-plugin/
├── marketplace.json           # Claude marketplace
.github/plugin/
├── marketplace.json           # Copilot CLI marketplace
plugins/
├── kreuzberg/
│   └── plugin.json            # MCP server config
├── kreuzcrawl/
│   └── plugin.json
└── kreuzberg-cloud/
    └── plugin.json
scripts/
├── bump-version.sh            # lockstep version bump
└── validate-manifests.sh      # CI parity check
```

## Releasing

```bash
echo 0.2.0 > VERSION
scripts/bump-version.sh "$(cat VERSION)"
scripts/validate-manifests.sh
git commit -am "chore: release v$(cat VERSION)"
git tag "v$(cat VERSION)" && git push --tags
```

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding skills, testing locally, and bumping versions.

## Security

Report security vulnerabilities privately at [SECURITY.md](SECURITY.md). Do not open public issues for security concerns.

## FAQ

**Can I use just one plugin?**

Yes. `/plugin install kreuzberg@kreuzberg` installs only kreuzberg.

**Do skills consume context?**

Only when triggered. Skill descriptions load at startup (~300 tokens total) but stay in context. They consume zero tokens unless the agent decides to invoke the MCP tools.

**Can I customize a skill locally?**

Yes. Fork the repo, edit the skill SKILL.md, and use `/plugin marketplace add <local-path>` to self-host your version.

**How do I report a broken skill?**

Open an issue at [kreuzberg-dev/plugins](https://github.com/kreuzberg-dev/plugins/issues) with the plugin name, agent harness, and exact request that failed.

**When will the kreuzberg-cloud MCP server arrive?**

Iteration 3, no firm date. The v0.1.0 skills-only release is functional now and will gain MCP transport in v0.2.0.

## License

MIT. See [LICENSE](LICENSE).

## Part of Kreuzberg.dev

- [Kreuzberg](https://github.com/kreuzberg-dev/kreuzberg) — document intelligence: text, tables, metadata from 91+ formats with optional OCR.
- [Kreuzberg Cloud](https://github.com/kreuzberg-dev/kreuzberg-cloud) — managed extraction API with SDKs, dashboards, and observability.
- [kreuzcrawl](https://github.com/kreuzberg-dev/kreuzcrawl) — web crawling and scraping with HTML→Markdown and headless-Chrome fallback.
- [html-to-markdown](https://github.com/kreuzberg-dev/html-to-markdown) — fast, lossless HTML→Markdown engine.
- [liter-llm](https://github.com/kreuzberg-dev/liter-llm) — universal LLM API client with native bindings for 14 languages and 143 providers.
- [tree-sitter-language-pack](https://github.com/kreuzberg-dev/tree-sitter-language-pack) — tree-sitter grammars and code-intelligence primitives.
- [alef](https://github.com/kreuzberg-dev/alef) — the polyglot binding generator that produces every per-language binding across the 5 polyglot repos.
