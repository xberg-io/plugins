# xberg-enterprise

Managed Xberg document intelligence on `api.xberg.io` from Gemini CLI
sessions. The cloud surface accepts PDFs, Office docs, images, and URL crawls;
returns text, tables, metadata, and images; supports webhook delivery,
presigned uploads for large files, document versioning and diffing, sandbox
keys, and per-project usage tracking.

## v0.1.0 limitation

This release is documentation-only — seven skills covering the API surface and
no MCP server. The `xberg-enterprise` CLI binary lands in plugin v0.2.0 and
will be auto-registered as an MCP server at that point. Until then, call the
HTTP API directly (curl) or use the official TypeScript / Python SDKs.

## Authentication

Every request needs a Bearer token in the `Authorization` header:

```bash
curl https://api.xberg.io/v1/usage \
  -H "Authorization: Bearer $XBERG_API_KEY"
```

Provision the key one of two ways:

1. Export `XBERG_API_KEY` in your shell or session.
2. Write `~/.xberg/cloud.toml` with `api_key = "sk_live_..."`.

The plugin's `SessionStart` hook checks both on every session and emits a
setup reminder if neither is configured. Sandbox keys (24h, 50-page quota,
no signup) can be minted via `POST /v1/sandbox/key` — see the `sandbox-keys`
skill.

## Skills shipped

- `xberg-enterprise` — full API surface, when to prefer cloud over local.
- `offloading-extraction` — submitting jobs via `POST /v1/extract`.
- `tracking-cloud-jobs` — polling `GET /v1/jobs/{id}` and webhook delivery.
- `versioning-documents` — `GET /v1/documents/{id}`, version history, and diffs.
- `presigned-uploads` — three-step flow for files larger than ~50 MB.
- `managing-cloud-usage` — quota and billing visibility via `GET /v1/usage`.
- `sandbox-keys` — minting ephemeral keys for evaluation.

## Working with the user

State the exact endpoint and payload before issuing the request. Quote
filenames and job IDs. Prefer presigned uploads for anything over 50 MB —
the JSON `data` field is base64 and inflates large bodies. When extraction
is queued, ask whether to poll or rely on the user's webhook.

For installation across hosts (Claude Code, Codex, Cursor, opencode,
Gemini), see the marketplace
[README](https://github.com/xberg-io/plugins).
