# kreuzcrawl

Web crawling and scraping with HTML→Markdown conversion and a headless-Chrome
fallback. This extension wraps the local `kreuzcrawl` CLI and registers its
MCP server.

## What you get

- `kreuzcrawl scrape <url>` — fetch a single page and render it as clean
  Markdown plus structured metadata.
- `kreuzcrawl crawl <url>` — follow links across a domain, bounded by
  `--depth`, `--max-pages`, and `--concurrent`.
- `kreuzcrawl map <url>` — enumerate URLs from sitemaps and link extraction
  without rendering content.
- `kreuzcrawl interact <url> --actions <json>` — drive a real browser to
  click, type, scroll, and capture the resulting DOM.
- `kreuzcrawl mcp` — the MCP server (stdio transport) is auto-registered for
  Gemini CLI when this extension is installed.

## Prerequisite

The `kreuzcrawl` binary must be on `PATH`. Install one of:

```bash
brew install kreuzberg-dev/tap/kreuzcrawl
# or run without a persistent install (self-installs the binary):
npx @kreuzberg/kreuzcrawl-cli --help
uvx --from kreuzcrawl kreuzcrawl --help
# or build from source (mcp/api subcommands are non-default features):
cargo install --git https://github.com/kreuzberg-dev/kreuzcrawl kreuzcrawl-cli --features all
```

## Skills

Reach for the focused skills before invoking the CLI by hand:

- `skills/kreuzcrawl/` — installation, command surface, when to use the MCP
  server.
- `skills/crawling-a-site/` — when the user wants to follow links across a
  domain.
- `skills/scraping-html-to-markdown/` — when the user wants a single page as
  Markdown.
- `skills/headless-fallback/` — when static fetches return empty bodies or
  WAF blocks.

## Notes

- All commands accept `--format markdown` to print raw Markdown instead of
  JSON. Use Markdown when piping to a file the user will read; use JSON when
  programmatic consumers downstream need metadata.
- Use the MCP tools (auto-registered) when available — they save shelling out
  and surface typed errors. Fall back to the CLI for scripting and pipelines.
- Respect `robots.txt` by default with `--respect-robots-txt`. Crawl politely:
  `--rate-limit` defaults to 200 ms per domain.
