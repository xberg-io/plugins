# modelcontextprotocol/registry

- Upstream: <https://github.com/modelcontextprotocol/registry>
- Status: **setup added — first publish pending labelled images**
- Reason: The current registry supports npm, PyPI, NuGet, OCI, and MCPB package verification. It does not support Cargo/crates.io metadata, so the CLI repos use GHCR OCI images.

## Implemented setup

- `xberg/server.json` publishes `io.github.xberg-io/xberg` via `ghcr.io/xberg-io/xberg-cli:<version>`.
- `crawlberg/server.json` publishes `io.github.xberg-io/crawlberg` via `ghcr.io/xberg-io/crawlberg:<version>`.
- Both Dockerfiles now add `io.modelcontextprotocol.server.name`.
- Both Docker publish workflows stamp release versions into `server.release.json`, run `mcp-publisher login github-oidc`, and publish after Docker image publication.

## First publish

1. Release labelled GHCR images through the Docker workflows.
2. Run `mcp-publisher login github` locally if doing the first publish by hand.
3. Run `mcp-publisher publish server.json` from each CLI repo, or let the release workflow publish via GitHub OIDC.

## Discovery until registry publication

- `punkpeye/awesome-mcp-servers` (PR #7633) covers MCP-server discovery.
- `jmanhype/awesome-claude-code` (PR #54) lists both as MCP servers.

Cloud plugin (xberg-enterprise) deferred until v0.2.0 ships the MCP wiring.
