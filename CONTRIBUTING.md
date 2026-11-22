# Contributing

Plugin content belongs in the product repositories (`plugin/` directory); open changes there. This repository only lists releases.

## Setup

```sh
mise run setup          # mise install (poly, python) and the poly git hooks
```

Tools follow the [toolchains](https://github.com/xberg-io/toolchains) baseline named in `toolchains.toml`; `mise.lock` is generated, never hand-edited. The AI governance files (`AGENTS.md`, `CLAUDE.md`) are generated from `.ai-rulez/`:

```sh
npx -y ai-rulez@latest generate --no-local --strict-config
npx -y ai-rulez@latest lock
```

## Tasks

| Task | Does |
|------|------|
| `mise run test` | Unit tests for the marketplace scripts |
| `mise run validate` | Check every marketplace file against the product repositories (needs network) |
| `mise run governance:check` | Check that the generated AI governance files match their sources |

- Move a pin: `python3 scripts/bump-ref.py <plugin> <tag>`, then `mise run validate`.
- Add a plugin: add an entry to every file in `scripts/marketplace.py` `FORMATS` (same name, repository, path and ref), then validate.
- Lint and format: `poly lint <paths>` and `poly fmt <paths>` (a dry run; `--fix` writes).
- Commits: conventional commits, one logical change each; the hooks check them.
