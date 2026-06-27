# TypeScript / Node.js API Reference

Package: `@xberg-io/html-to-markdown-node`
The TypeScript package (`@xberg-io/html-to-markdown`) re-exports everything from `@xberg-io/html-to-markdown-node` (the native NAPI-RS binding) and adds file/stream helpers.

## Installation

```bash
npm install @xberg-io/html-to-markdown-node
# or
pnpm add @xberg-io/html-to-markdown-node
```

## Primary Function

```typescript
import { convert } from '@xberg-io/html-to-markdown-node';

// convert() returns a JSON string — always JSON.parse() the result
const result = JSON.parse(convert(html, options?));
console.log(result.content);    // Markdown string or null
console.log(result.tables);     // array of table objects
console.log(result.warnings);   // array of warning objects
console.log(result.metadata);   // metadata object or null
```

**Important:** `convert()` returns a JSON-encoded string, not a parsed object. This is intentional — NAPI-RS serialization of deeply-nested objects is expensive. Always call `JSON.parse()` on the result.

## Function Signatures

### Core (from `@xberg-io/html-to-markdown-node`)

```typescript
// Primary conversion — returns JSON string, always JSON.parse() the result
function convert(html: string, options?: JsConversionOptions): string;
```

### File and Stream Helpers (from `@xberg-io/html-to-markdown`)

```typescript
import {
  convertFile,
  convertStream,
  wrapVisitorCallback,
  wrapVisitorCallbacks,
  hasMetadataSupport,
} from "@xberg-io/html-to-markdown-node";
import type { Readable } from "node:stream";

// File helpers (async, return JSON string — JSON.parse() the result)
async function convertFile(filePath: string, options?: JsConversionOptions | null): Promise<string>;

// Stream helpers (async, return JSON string — JSON.parse() the result)
async function convertStream(
  stream: Readable | AsyncIterable<string | Buffer>,
  options?: JsConversionOptions | null,
): Promise<string>;
```

## Interfaces

### JsConversionOptions

All fields are optional. Defaults match Rust defaults. Enum values are PascalCase strings (e.g. `'Atx'`, `'Spaces'`).

```typescript
interface JsConversionOptions {
  headingStyle?: "Atx" | "Underlined" | "AtxClosed";
  listIndentType?: "Spaces" | "Tabs";
  listIndentWidth?: number;
  bullets?: string;
  strongEmSymbol?: string; // '*' or '_'
  escapeAsterisks?: boolean;
  escapeUnderscores?: boolean;
  escapeMisc?: boolean;
  escapeAscii?: boolean;
  codeLanguage?: string;
  autolinks?: boolean;
  defaultTitle?: boolean;
  brInTables?: boolean;
  highlightStyle?: "DoubleEqual" | "Html" | "Bold" | "None";
  extractMetadata?: boolean;
  whitespaceMode?: "Normalized" | "Strict";
  stripNewlines?: boolean;
  wrap?: boolean;
  wrapWidth?: number;
  convertAsInline?: boolean;
  subSymbol?: string;
  supSymbol?: string;
  newlineStyle?: "Spaces" | "Backslash";
  codeBlockStyle?: "Indented" | "Backticks" | "Tildes";
  keepInlineImagesIn?: string[];
  preprocessing?: JsPreprocessingOptions;
  encoding?: string;
  debug?: boolean;
  stripTags?: string[];
  preserveTags?: string[];
  skipImages?: boolean;
  outputFormat?: "Markdown" | "Djot" | "Plain";
}
```

**Note on enum values:** NAPI-RS `const enum` values are PascalCase strings (e.g. `'Atx'` not `'atx'`, `'Spaces'` not `'spaces'`). Using lowercase will be rejected at runtime.

### JsPreprocessingOptions

```typescript
interface JsPreprocessingOptions {
  enabled?: boolean;
  preset?: "minimal" | "standard" | "aggressive";
  removeNavigation?: boolean;
  removeForms?: boolean;
}
```

### JsMetadataConfig

Fields use camelCase (matching the NAPI-RS binding):

```typescript
interface JsMetadataConfig {
  extractDocument?: boolean;
  extractHeaders?: boolean;
  extractLinks?: boolean;
  extractImages?: boolean;
  extractStructuredData?: boolean;
  maxStructuredDataSize?: number;
}
```

### JsInlineImage (in result.images)

Inline images are extracted when `extractImages` is enabled in options. The result is in `result.images`:

```typescript
interface JsInlineImage {
  data: Buffer;
  format: string;
  filename?: string;
  description?: string;
  dimensions?: number[]; // [width, height]
  source: string; // "img_data_uri" | "svg_element"
  attributes: Record<string, string>;
}
```

## ConversionResult (from convert())

The result of `JSON.parse(convert(html))`:

```typescript
interface ConversionResult {
  content: string | null; // Markdown text
  document: object | null; // structured document tree (null unless includeDocumentStructure enabled)
  metadata: object | null; // HtmlMetadata if metadata feature enabled
  tables: Array<{
    cells: Array<Array<string>>; // rows x columns of cell text
    markdown: string; // rendered table in target format
    isHeaderRow: Array<boolean>; // per-row flag: true if row was inside <thead>
  }>;
  warnings: Array<{
    message: string;
    kind: string;
  }>;
}
```

**Note on `tables`:** The Node.js binding uses a flat `cells: Array<Array<string>>` structure (no `grid` wrapper), plus `isHeaderRow` for header detection. This differs from the Rust `TableGrid` struct.

## Visitor Pattern

The visitor is passed as a third argument to `convert()`:

```typescript
import { convert } from "@xberg-io/html-to-markdown-node";
import { wrapVisitorCallbacks } from "@xberg-io/html-to-markdown-node";

const visitor = wrapVisitorCallbacks({
  visitElementStart: (ctx) => {
    // ctx.tagName, ctx.attributes available
    return { type: "continue" };
  },
  visitText: (ctx, text) => {
    return { type: "continue" };
  },
});

const result = convert(html, options, visitor);
```

Visitor return types: `{ type: 'continue' }` | `{ type: 'skip' }` | `{ type: 'preserve_html' }` | `{ type: 'custom', output: string }` | `{ type: 'error', message: string }`.

## Examples

```typescript
// Simple conversion
import { convert } from "@xberg-io/html-to-markdown-node";
const result = JSON.parse(convert("<h1>Hello</h1>"));
console.log(result.content); // "# Hello\n"

// Metadata extraction — enabled via extractMetadata option, result in result.metadata
const result2 = JSON.parse(convert(html, { extractMetadata: true }));
console.log(result2.metadata.document.title);
console.log(result2.metadata.headers.length);

// Tables — always in result.tables
const result3 = JSON.parse(convert(html));
for (const table of result3.tables) {
  console.log(table.markdown);
}

// Inline images — enable extractImages in options
const result4 = JSON.parse(convert(html, { extractImages: true, captureSvg: true }));
for (const image of result4.images) {
  console.log(image.format, image.filename);
}

// File conversion
import { convertFile } from "@xberg-io/html-to-markdown-node";
const json = await convertFile("./page.html", { headingStyle: "Atx" });
const fileResult = JSON.parse(json);
console.log(fileResult.content);
```
