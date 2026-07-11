# GIF Recording Plan

Record each GIF against a disposable example plugin. Reset the example before every take so commands and generated diffs stay predictable. Keep each recording between 10 and 20 seconds, crop to the active terminal or editor, and use a font size that remains readable in the README.

## 1. Configure a plugin

Show `.ai-rulez/config.toml`, add the minimal `[plugin]` metadata, and save the file. End with the complete plugin name and version visible.

## 2. Add a shared skill

Create one `.ai-rulez/skills/<name>/SKILL.md` file with its frontmatter and a short instruction. End by showing the source tree so viewers can see that shared content is authored once.

## 3. Add an OpenCode adapter

Open `.ai-rulez/opencode/index.js`, replace the scaffolded example with one small tool, and save it. Show the schema, description, and `execute` function without scrolling through unrelated code.

## 4. Preview generation

Run:

```bash
ai-rulez generate --plugin --dry-run
```

Pause on the planned output so the runtime bundles and marketplace index are readable.

## 5. Generate every runtime

Run:

```bash
ai-rulez generate --plugin
```

Expand the generated Claude, Codex, Cursor, Gemini, Kimi, Factory, and OpenCode paths. End on the generated OpenCode entrypoint to connect it to the authored adapter from GIF 3.

## 6. Validate and use the plugin

Run the repository validation task, install the generated plugin into one supported runtime, and invoke its example capability. End on the successful tool result rather than the installation output.

## Publishing

Store optimized GIFs in `docs/assets/gifs/` with names `01-configure-plugin.gif` through `06-validate-and-use.gif`. Keep source recordings outside the generated plugin bundles. Do not commit placeholder or empty GIF files.
