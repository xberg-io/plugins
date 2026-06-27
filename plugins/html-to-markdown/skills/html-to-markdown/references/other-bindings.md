# Other Language Bindings

Brief reference for Go, Ruby, PHP, Java, C#, Elixir, R, WASM, and C FFI.

---

## Go

**Module:** `github.com/xberg-io/html-to-markdown/packages/go/v3`
**Package:** `htmltomarkdown`
**Install:** `go get github.com/xberg-io/html-to-markdown/packages/go/v3`

Uses cgo with the C FFI layer. Options are passed as JSON strings internally.

```go
import "github.com/xberg-io/html-to-markdown/packages/go/v3/htmltomarkdown"

// Primary function — returns *ConversionResult
result, err := htmltomarkdown.Convert(html)
if err != nil {
    log.Fatal(err)
}
fmt.Println(result.Content)        // markdown string
fmt.Println(len(result.Tables))    // extracted tables
fmt.Println(len(result.Warnings))  // processing warnings

// With options (variadic)
result, err = htmltomarkdown.Convert(html, &htmltomarkdown.ConversionOptions{
    HeadingStyle: "atx",
})

// Metadata is in result.Metadata when metadata extraction is enabled
fmt.Println(result.Metadata)

// Tables are always in result.Tables
for _, table := range result.Tables {
    fmt.Println(table.Markdown)
}
```

### Go ConversionOptions

Options are passed as a pointer to `ConversionOptions`. Fields use Go naming conventions (PascalCase). Pass `nil` or omit the argument for defaults.

---

## Ruby

**Gem:** `html-to-markdown`
**Install:** `gem install html-to-markdown`
**Require:** `require 'html_to_markdown'`

Uses Magnus (native extension via Rust).

```ruby
require 'html_to_markdown'

# Primary function — returns a Hash
result = HtmlToMarkdown.convert(html)
puts result[:content]          # markdown string
puts result[:tables].length    # extracted tables
puts result[:warnings].length  # processing warnings
puts result[:metadata]         # metadata hash (or nil)

# With options (Hash)
result = HtmlToMarkdown.convert(html, {
    heading_style: "atx",
    code_block_style: "backticks",
    autolinks: true,
})

# Metadata — in result[:metadata]
result = HtmlToMarkdown.convert(html)
metadata = result[:metadata]

# Inline images — set extract_images: true
result = HtmlToMarkdown.convert(html, { extract_images: true })
images = result[:images]

# Tables — always in result[:tables]
result[:tables].each { |t| puts t[:markdown] }

# Reusable options handle (performance)
handle = HtmlToMarkdown.options({ heading_style: "atx" })
result = HtmlToMarkdown.convert(html, handle)
```

### Ruby convert() return Hash

```ruby
{
    content: String,              # markdown text
    document: nil,                # not yet wired
    metadata: Hash | nil,         # HtmlMetadata
    tables: Array,                # [{grid: {...}, markdown: "..."}]
    images: Array,                # inline images (if extract_images: true)
    warnings: Array               # [{message: "...", kind: "..."}]
}
```

---

## PHP

**Composer:** `xberg-io/html-to-markdown`
**Install:** `composer require xberg-io/html-to-markdown`
**PHP requirement:** 8.4+

Uses ext-php-rs (native PHP extension). The facade class is `HtmlToMarkdownRs` under the `Html\To\Markdown\Rs` namespace.

```php
<?php
declare(strict_types=1);

use Html\To\Markdown\Rs\HtmlToMarkdownRs;

// Primary function — returns ConversionResult with content, metadata, tables, images, warnings
$result = HtmlToMarkdownRs::convert('<h1>Hello</h1>');
$markdown = $result->content;

// With options (ConversionOptions object)
use Html\To\Markdown\Rs\ConversionOptions;

$options = new ConversionOptions();
$options->headingStyle = 'atx';
$options->codeBlockStyle = 'backticks';
$options->autolinks = true;

$result = HtmlToMarkdownRs::convert('<h1>Hello</h1>', $options);

// Metadata — in $result->metadata
$metadata = $result->metadata;
echo $metadata->document->title;

// Tables — always in $result->tables
foreach ($result->tables as $table) {
    echo $table->markdown;
}

// Inline images — set extractImages: true in options
$options->extractImages = true;
$result = HtmlToMarkdownRs::convert('<img src="data:..." />', $options);
$images = $result->images;
```

---

## Java

**Maven:** `io.xberg:html-to-markdown`
**GroupId:** `io.xberg`
**ArtifactId:** `html-to-markdown`
**Java requirement:** 21+ (uses Panama FFM API)

```xml
<dependency>
  <groupId>io.xberg</groupId>
  <artifactId>html-to-markdown</artifactId>
  <version>3.2.0</version>
</dependency>
```

```java
import io.xberg.htmltomarkdown.HtmlToMarkdown;
import io.xberg.htmltomarkdown.ConversionResult;
import io.xberg.htmltomarkdown.HtmlToMarkdownRsException;

// Primary function — returns ConversionResult
try {
    ConversionResult result = HtmlToMarkdown.convert("<h1>Hello</h1>");
    System.out.println(result.content());    // markdown string
    System.out.println(result.tables());     // List<TableData>
    System.out.println(result.warnings());   // List<ProcessingWarning>
    System.out.println(result.metadata());   // metadata map (when enabled)
} catch (HtmlToMarkdownRsException e) {
    System.err.println("Conversion failed: " + e.getMessage());
}

// With options
import io.xberg.htmltomarkdown.ConversionOptions;

ConversionOptions options = new ConversionOptions();
options.setHeadingStyle("atx");
ConversionResult result = HtmlToMarkdown.convert("<h1>Hello</h1>", options);

// Tables — always in result.tables()
for (var table : result.tables()) {
    System.out.println(table.markdown());
}
```

---

## C# (.NET)

**NuGet:** `XbergIo.HtmlToMarkdown`
**Install:** `dotnet add package XbergIo.HtmlToMarkdown`
**.NET requirement:** 6+

The static entry point class is `HtmlToMarkdownRs`. The exception type is `HtmlToMarkdownRsException`.

```csharp
using HtmlToMarkdown;

// Primary function
var result = HtmlToMarkdownRs.Convert("<h1>Hello</h1>", null);
Console.WriteLine(result.Content);         // markdown string
Console.WriteLine(result.Tables.Count);    // table count
Console.WriteLine(result.Warnings.Count);  // warning count
Console.WriteLine(result.Metadata?.Document?.Title);  // metadata (when enabled)

// With options
var options = new ConversionOptions { ExtractImages = true };
var result2 = HtmlToMarkdownRs.Convert(html, options);
foreach (var image in result2.Images) {
    Console.WriteLine(image.Format);
}

// Tables — always in result.Tables
foreach (var table in result.Tables) {
    Console.WriteLine(table.Markdown);
}
```

### HtmlToMarkdownRsException

```csharp
try {
    var result = HtmlToMarkdownRs.Convert(html, null);
} catch (HtmlToMarkdownRsException e) {
    Console.Error.WriteLine($"Conversion failed: {e.Message}");
}
```

---

## Elixir

**Hex:** `html_to_markdown`
**Module:** `HtmlToMarkdown`
**Elixir requirement:** 1.14+ (uses Rustler NIFs)

```elixir
# mix.exs
{:html_to_markdown, "~> 3.0"}
```

```elixir
# Primary function — returns {:ok, map()} | {:error, term()}
{:ok, result} = HtmlToMarkdown.convert("<h1>Hello</h1>")
IO.puts result.content      # markdown string
IO.inspect result.tables    # list of table maps
IO.inspect result.warnings  # list of warning maps
IO.inspect result.metadata  # metadata map (when enabled)

# Bang variant (raises on error)
result = HtmlToMarkdown.convert!("<h1>Hello</h1>")

# With options
{:ok, result} = HtmlToMarkdown.convert(html, %{
    heading_style: "atx",
    code_block_style: "backticks",
})

# Metadata — in result.metadata
{:ok, result} = HtmlToMarkdown.convert(html)
metadata = result.metadata

# Tables — always in result.tables
Enum.each(result.tables, fn table -> IO.puts table.markdown end)

# Inline images — set extract_images: true
{:ok, result} = HtmlToMarkdown.convert(html, %{extract_images: true})
images = result.images

# Options handle (reuse for performance)
{:ok, handle} = HtmlToMarkdown.create_options_handle(%{heading_style: "atx"})
{:ok, result} = HtmlToMarkdown.convert(html, handle)
```

---

## R

**CRAN:** `htmltomarkdown`
**Install:** `install.packages("htmltomarkdown")`
**R requirement:** 4.1+

Uses extendr (Rust bindings for R).

```r
library(htmltomarkdown)

# Primary function
result <- convert("<h1>Hello</h1>")
cat(result$content)          # markdown string
length(result$tables)        # table count

# With options (named list)
result <- convert("<h1>Hello</h1>", list(
    heading_style = "atx",
    code_block_style = "backticks"
))

# Metadata — in result$metadata
result <- convert("<h1>Hello</h1>")
metadata <- result$metadata

# Tables — always in result$tables
for (table in result$tables) {
    cat(table$markdown)
}

# Inline images — set extract_images = TRUE
result <- convert("<img src='data:...' />", list(extract_images = TRUE))
images <- result$images

# Options handle (performance)
handle <- create_options_handle(list(heading_style = "atx"))
result <- convert_handle("<h1>Hello</h1>", handle)
```

---

## WASM

**Package:** `@xberg-io/html-to-markdown-wasm` (built with wasm-pack)

```javascript
import init, {
  convert,
  convertBytes,
  createConversionOptionsHandle,
  convertWithOptionsHandle,
} from "@xberg-io/html-to-markdown-wasm";

await init(); // initialize WASM module

// convert() — returns JSON string, always JSON.parse() the result
const result = JSON.parse(convert("<h1>Hello</h1>", {}));
console.log(result.content); // markdown string
console.log(result.tables); // extracted tables
console.log(result.metadata); // metadata (when enabled)

// convertBytes() — accepts Uint8Array
const encoder = new TextEncoder();
const bytes = encoder.encode("<h1>Hello</h1>");
const result2 = JSON.parse(convertBytes(bytes, {}));

// Metadata — in result.metadata when extract_metadata is enabled
const result3 = JSON.parse(convert("<h1>Hello</h1>", { extractMetadata: true }));
console.log(result3.metadata);

// Tables — always in result.tables
for (const table of result.tables) {
  console.log(table.markdown);
}

// Options handle (reuse for performance)
const handle = createConversionOptionsHandle({ headingStyle: "atx" });
const json = convertWithOptionsHandle("<h1>Hello</h1>", handle);
```

---

## Node.js / npm

**Package:** `@xberg-io/html-to-markdown-node`
**Install:** `npm install @xberg-io/html-to-markdown-node`

Uses NAPI-RS. Platform-specific native binaries are delivered as optional dependencies.

```json
{
  "optionalDependencies": {
    "@xberg-io/html-to-markdown-node-darwin-arm64": "3.2.0",
    "@xberg-io/html-to-markdown-node-darwin-x64": "3.2.0",
    "@xberg-io/html-to-markdown-node-linux-arm64-gnu": "3.2.0",
    "@xberg-io/html-to-markdown-node-linux-arm64-musl": "3.2.0",
    "@xberg-io/html-to-markdown-node-linux-x64-gnu": "3.2.0",
    "@xberg-io/html-to-markdown-node-linux-x64-musl": "3.2.0",
    "@xberg-io/html-to-markdown-node-linux-arm-gnueabihf": "3.2.0",
    "@xberg-io/html-to-markdown-node-win32-x64-msvc": "3.2.0",
    "@xberg-io/html-to-markdown-node-win32-arm64-msvc": "3.2.0"
  }
}
```

---

## C FFI

**Crate:** `html-to-markdown-ffi`
**Header:** `html_to_markdown.h` (generated by cbindgen)

Used internally by Go, Java, and C# bindings. All exported symbols use the `htm_` prefix. Direct C usage:

```c
#include "html_to_markdown.h"

// htm_convert() — returns an opaque HTMConversionResult handle
HTMConversionOptions *opts = htm_conversion_options_from_json("{\"headingStyle\":\"atx\"}");
HTMConversionResult *result = htm_convert(html_cstr, opts);
htm_conversion_options_free(opts);

if (result) {
    // Extract fields as malloc'd strings
    char *content = htm_conversion_result_content(result);
    // use content ...
    htm_free_string(content);

    htm_conversion_result_free(result);
}

// Error handling
int32_t code = htm_last_error_code();
const char *msg = htm_last_error_context(); // borrowed — do NOT free

// Version
const char *ver = htm_version(); // static — do NOT free
```

**Key FFI contracts:**

- All exported functions use the `htm_` prefix.
- Strings returned by `htm_conversion_result_content()` and similar field accessors must be freed with `htm_free_string()`. Never use the system `free()`.
- `htm_last_error_context()` and `htm_version()` return borrowed/static pointers — do NOT free them.
- Every `_free()` function has a matching allocator (`htm_convert` → `htm_conversion_result_free`, `htm_conversion_options_from_json` → `htm_conversion_options_free`).
