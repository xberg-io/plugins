// AI-RULEZ :: GENERATED FILE — DO NOT EDIT
// Content-Hash: blake3:5b4fb200cefe0c4b89dddc03842abcb050f35a252cf883bf195cd19798bca6de
// Source-Hash: blake3:1d60ccacd381c0139c3ec83f2c73d2d8fa36b01cca58fb556caa821455cc55c8
// Schema-Version: v1

/**
 * OpenCode-specific plugin entrypoint.
 *
 * ai-rulez copies this source module into the generated OpenCode package. Shared
 * skills, commands, agents, and MCP configuration belong in their normal
 * `.ai-rulez` sources; add only OpenCode-specific tools or hooks here.
 *
 * To extend this plugin:
 * 1. Import `tool` from `@opencode-ai/plugin`.
 * 2. Define tool arguments with `tool.schema` and validate every external input.
 * 3. Return the OpenCode hooks object from this function.
 * 4. Preview with `ai-rulez generate --plugin --dry-run` before regenerating.
 *
 * Pass subprocess arguments as an array. Never interpolate external input into
 * a shell command.
 */
const LiterLlmPlugin = async () => ({});

export default LiterLlmPlugin;
