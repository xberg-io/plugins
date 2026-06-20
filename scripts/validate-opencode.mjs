import { pathToFileURL } from "node:url";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));

const plugins = [
  {
    path: "plugins/kreuzberg/.opencode/plugins/kreuzberg.js",
    exportName: "KreuzbergPlugin",
    tools: ["kreuzberg_extract", "kreuzberg_detect", "kreuzberg_formats"],
  },
  {
    path: "plugins/kreuzcrawl/.opencode/plugins/kreuzcrawl.js",
    exportName: "KreuzcrawlPlugin",
    tools: ["kreuzcrawl_scrape", "kreuzcrawl_crawl", "kreuzcrawl_map"],
  },
  {
    path: "plugins/kreuzberg-cloud/.opencode/plugins/kreuzberg-cloud.js",
    exportName: "KreuzbergCloudPlugin",
    tools: [],
  },
];

for (const plugin of plugins) {
  const moduleUrl = pathToFileURL(resolve(root, plugin.path));
  const mod = await import(moduleUrl.href);
  const factory = mod.default ?? mod[plugin.exportName];

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
}

console.log(`validate-opencode: ${plugins.length} entrypoints import cleanly`);
