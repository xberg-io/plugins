# Changelog

All notable changes to Kreuzberg Plugins are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- MCP server transport for kreuzberg-cloud
- html-to-markdown and tree-sitter-language-pack MCP servers (plugin wiring is in place; the upstream `mcp` subcommands land in their next releases)

## [0.2.1] - 2026-06-20

### Fixed

- Scope the cli-proxy npm packages to `@kreuzberg/<tool>-cli` (npx); update the MCP launchers and install docs accordingly. PyPI/uvx names stay flat (`<tool>-cli`).

## [0.2.0] - 2026-06-20

### Added

- **html-to-markdown** plugin: fast, lossless HTML→Markdown with metadata, tables, and document-structure extraction
- **liter-llm** plugin: universal LLM API client for 143 providers (chat, streaming, tools, embeddings, search, OCR) plus an OpenAI-compatible proxy and an MCP server
- **tree-sitter-language-pack** plugin: parse and extract code intelligence from 300+ languages (structure, imports, symbols, syntax-aware chunking)
- Auto-installing MCP launchers (existing binary → npx → uvx → brew → checksum-verified prebuilt download) for kreuzberg, kreuzcrawl, and liter-llm; CLI/MCP wiring for html-to-markdown and tree-sitter-language-pack
- New skills — kreuzberg: `chunking`, `batch-extraction`, `extracting-keywords`; kreuzcrawl: `mapping-urls`, `automating-the-browser`, `serving-the-api`; kreuzberg-cloud: `versioning-documents`
- `<tool>-cli` npm/PyPI proxy packages so `npx <tool>-cli` / `uvx <tool>-cli` install and run each CLI

### Changed

- Standardized skill conventions, frontmatter, README structure, and manifest capabilities across all plugins (documented in CONTRIBUTING.md)
- Corrected install documentation to the real channels (brew tap, npx/uvx, prebuilt release binaries)

## [0.1.0] - 2026-06-08

### Added

- **kreuzberg** plugin: local document extraction (PDF, Office, images with OCR, HTML, email, archives, academic; 91+ formats)
- **kreuzcrawl** plugin: web crawling and scraping with HTML→Markdown and headless-Chrome fallback
- **kreuzberg-cloud** plugin: managed extraction API (skills-only; MCP server in v0.2.0)
- Multi-harness support: Claude Code, Codex CLI, Cursor, Gemini CLI, Factory Droid, GitHub Copilot CLI, opencode
- Skill-based agent integration with automatic tool loading
- Marketplace registration for official Claude Code and Factory Droid (pending review)
- Self-hosted marketplace for all harnesses
- Contributing guidelines and security policy

[Unreleased]: https://github.com/kreuzberg-dev/plugins/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/kreuzberg-dev/plugins/releases/tag/v0.1.0
