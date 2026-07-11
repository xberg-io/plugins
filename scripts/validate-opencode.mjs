import { pathToFileURL } from "node:url";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { readFile } from "node:fs/promises";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const generatedHeader =
  /^\/\/ AI-RULEZ :: GENERATED FILE — DO NOT EDIT\n\/\/ Content-Hash: blake3:[0-9a-f]{64}\n\/\/ Source-Hash: blake3:[0-9a-f]{64}\n\/\/ Schema-Version: v1\n\n/;

const plugins = [
  {
    name: "xberg",
    path: "plugins/xberg/.opencode/plugins/xberg.js",
    packageName: "@xberg-io/opencode-xberg",
    tools: ["xberg_extract", "xberg_detect", "xberg_formats"],
  },
  {
    name: "crawlberg",
    path: "plugins/crawlberg/.opencode/plugins/crawlberg.js",
    packageName: "@xberg-io/opencode-crawlberg",
    tools: ["crawlberg_scrape", "crawlberg_crawl", "crawlberg_map"],
  },
  {
    name: "html-to-markdown",
    path: "plugins/html-to-markdown/.opencode/plugins/html-to-markdown.js",
    packageName: "@xberg-io/opencode-html-to-markdown",
    tools: ["html_to_markdown_convert", "html_to_markdown_fetch_url", "html_to_markdown_extract"],
  },
  {
    name: "tree-sitter-language-pack",
    path: "plugins/tree-sitter-language-pack/.opencode/plugins/tree-sitter-language-pack.js",
    packageName: "@xberg-io/opencode-tree-sitter-language-pack",
    tools: ["tspack_parse", "tspack_process", "tspack_info"],
  },
  {
    name: "liter-llm",
    path: "plugins/liter-llm/.opencode/plugins/liter-llm.js",
    packageName: "@xberg-io/opencode-liter-llm",
    tools: [],
  },
];

for (const plugin of plugins) {
  const moduleUrl = pathToFileURL(resolve(root, plugin.path));
  const mod = await import(moduleUrl.href);
  const factory = mod.default;

  if (typeof factory !== "function") {
    throw new Error(`${plugin.path} does not export a plugin function`);
  }

  const hooks = await factory({});
  const tools = hooks?.tool ?? {};
  const actual = Object.keys(tools).sort();
  const expected = plugin.tools.toSorted();

  if (JSON.stringify(actual) !== JSON.stringify(expected)) {
    throw new Error(`${plugin.path} tools ${JSON.stringify(actual)} != ${JSON.stringify(expected)}`);
  }

  for (const name of expected) {
    if (typeof tools[name]?.execute !== "function") {
      throw new Error(`${plugin.path} tool ${name} is missing an execute function`);
    }
  }

  const sourcePath = resolve(root, `plugins/${plugin.name}/.ai-rulez/opencode/index.js`);
  const generatedPath = resolve(root, plugin.path);
  const [source, generated] = await Promise.all([readFile(sourcePath, "utf8"), readFile(generatedPath, "utf8")]);

  const generatedBody = generated.replace(generatedHeader, "");
  if (generatedBody === generated) {
    throw new Error(`${plugin.path} is missing its generated-file header`);
  }
  if (source !== generatedBody) {
    throw new Error(`${plugin.path} is stale; run ai-rulez generate --plugin`);
  }

  const packagePath = resolve(root, `plugins/${plugin.name}/package.json`);
  const packageJson = JSON.parse(await readFile(packagePath, "utf8"));
  const expectedEntry = `./.opencode/plugins/${plugin.name}.js`;

  if (packageJson.name !== plugin.packageName) {
    throw new Error(`${packagePath} name ${JSON.stringify(packageJson.name)} != ${JSON.stringify(plugin.packageName)}`);
  }
  if (packageJson.type !== "module" || packageJson.main !== expectedEntry.slice(2)) {
    throw new Error(`${packagePath} does not point to the generated ESM entrypoint`);
  }
  if (packageJson.exports?.["."] !== expectedEntry) {
    throw new Error(`${packagePath} export does not point to ${expectedEntry}`);
  }
  if (packageJson.dependencies?.["@opencode-ai/plugin"] === undefined) {
    throw new Error(`${packagePath} is missing the @opencode-ai/plugin dependency`);
  }
  if (packageJson.repository?.type !== "git" || packageJson.repository?.url !== "https://github.com/xberg-io/plugins") {
    throw new Error(`${packagePath} must declare the GitHub repository for npm provenance`);
  }
}

console.log(`validate-opencode: ${plugins.length} entrypoints import cleanly`);
