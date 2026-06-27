# Language Bindings Reference

Xberg provides native bindings for multiple programming languages, each with precompiled binaries for x86_64 and aarch64 on Linux and macOS. This reference covers installation and basic usage for each binding.

## Go

**Installation:**

```bash
go get github.com/xberg-io/xberg/packages/go/v5
```

**Basic Extraction:**

```go
package main

import (
    "context"
    "fmt"
    "github.com/xberg-io/xberg/packages/go/v5/xberg"
)

func main() {
    ctx := context.Background()
    result, err := xberg.ExtractFile(ctx, "document.pdf", nil)
    if err != nil {
        panic(err)
    }
    fmt.Println(result.Content)
}
```

See the [Go binding documentation](https://github.com/xberg-io/xberg/tree/main/packages/go) for complete API reference.

## Ruby

**Installation:**

```bash
gem install xberg
```

Or in your Gemfile:

```ruby
gem 'xberg'
```

**Basic Extraction:**

```ruby
require 'xberg'

result = Xberg.extract_file_sync('document.pdf')
puts result.content
```

See the [Ruby binding documentation](https://github.com/xberg-io/xberg/tree/main/packages/ruby) for complete API reference.

## Java

**Installation:**
Add to your Maven `pom.xml`:

```xml
<dependency>
    <groupId>io.xberg</groupId>
    <artifactId>xberg</artifactId>
    <version>4.2.x</version>
</dependency>
```

**Basic Extraction:**

```java
import io.xberg.Xberg;
import io.xberg.ExtractionResult;

public class Example {
    public static void main(String[] args) throws Exception {
        ExtractionResult result = Xberg.extractFile("document.pdf");
        System.out.println(result.getContent());
    }
}
```

See the [Java binding documentation](https://github.com/xberg-io/xberg/tree/main/packages/java) for complete API reference.

## C

**Installation:**

```bash
dotnet add package Xberg
```

**Basic Extraction:**

```csharp
using Xberg;

var result = XbergClient.ExtractFileSync("document.pdf");
Console.WriteLine(result.Content);
```

See the [C# binding documentation](https://github.com/xberg-io/xberg/tree/main/packages/csharp) for complete API reference.

## PHP

**Installation:**

```bash
composer require xberg/xberg
```

**Basic Extraction:**

```php
<?php
require 'vendor/autoload.php';

use Xberg\Xberg;

$xberg = new Xberg();
$result = $xberg->extractFile('document.pdf');
echo $result->content;
```

See the [PHP binding documentation](https://github.com/xberg-io/xberg/tree/main/packages/php) for complete API reference.

## Elixir

**Installation:**
Add to your `mix.exs` dependencies:

```elixir
def deps do
  [
    xberg: "~> 4.2"
  ]
end
```

**Basic Extraction:**

```elixir
{:ok, result} = Xberg.extract_file("document.pdf")
IO.puts(result.content)
```

See the [Elixir binding documentation](https://github.com/xberg-io/xberg/tree/main/packages/elixir) for complete API reference.

## WebAssembly (WASM)

**Installation:**

```bash
npm install @xberg-io/xberg-wasm
```

**Basic Extraction:**

```typescript
import { extractBytes } from "@xberg-io/xberg-wasm";

const fileData = await fs.promises.readFile("document.pdf");
const result = await extractBytes(fileData, "application/pdf");
console.log(result.content);
```

Supports browsers, Deno, and Cloudflare Workers.

See the [WASM binding documentation](https://github.com/xberg-io/xberg/tree/main/packages/typescript) for complete API reference.

## Docker

**Installation:**
Pull the official image from GitHub Container Registry:

```bash
docker pull ghcr.io/xberg-io/xberg
```

**API Server Mode:**

```bash
docker run -p 8000:8000 ghcr.io/xberg-io/xberg serve --host 0.0.0.0
```

**CLI Mode:**

```bash
docker run -v $(pwd):/data ghcr.io/xberg-io/xberg extract /data/document.pdf
```

**MCP Server Mode:**

```bash
docker run -i ghcr.io/xberg-io/xberg mcp
```

Image sizes:

- Core image: 1.0-1.3GB
- Full image: ~1.0-1.3GB

See the [Docker guide](https://docs.xberg.io/guides/docker/) for deployment details.

## Platform Support

All language bindings include precompiled binaries for x86_64 and aarch64 on Linux and macOS. Windows support varies by binding. Refer to the main [README](https://github.com/xberg-io/xberg) for platform compatibility matrix.
