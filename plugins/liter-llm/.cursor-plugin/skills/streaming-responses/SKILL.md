---
name: streaming-responses
description: Use when streaming tokens incrementally from an LLM via liter-llm over SSE or async iterators. Covers chat_stream, delta handling, and null-content chunks.
---

<!--
AI-RULEZ :: GENERATED FILE — DO NOT EDIT
Content-Hash: blake3:df7f4ae1ab36743798209d92e87aac1c81da9aa8742319a8b84a898b2d1649b1
Source-Hash: blake3:24bc8c5900c1b5df25fc7be857793c983a5012134d0044d08dd7dbc479aaf3a2
Schema-Version: v1
-->


# Streaming Responses

Use `chat_stream(...)` to receive tokens as they are produced instead of waiting
for the full completion. The proxy streams over SSE; bindings expose async
iterators.

## Python

```python
import asyncio, os
from liter_llm import create_client
from liter_llm._internal_bindings import ChatCompletionRequest

async def main() -> None:
    client = create_client(api_key=os.environ["OPENAI_API_KEY"])
    request = ChatCompletionRequest.from_json(
        '{"model":"openai/gpt-4o","messages":[{"role":"user","content":"Tell me a story"}],"stream":true}'
    )
    async for chunk in client.chat_stream(request):
        if chunk.choices and chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()

asyncio.run(main())
```

## TypeScript

```typescript
import { createClient } from "@xberg-io/liter-llm";

const client = createClient(process.env.OPENAI_API_KEY!);
const chunks = await client.chatStream({
  model: "openai/gpt-4o",
  messages: [{ role: "user", content: "Tell me a story" }],
});
for await (const chunk of chunks) {
  process.stdout.write(chunk.choices?.[0]?.delta?.content ?? "");
}
```

## Notes

- The first and last chunks often carry null content. Always null-check
  `chunk.choices[0].delta.content` (Python) or
  `chunk.choices[0]?.delta?.content` (TypeScript) before using it.
- Tool-call deltas arrive in `delta.tool_calls`; accumulate
  `function.arguments` fragments across chunks before parsing.
- Through the proxy, request streaming with `"stream": true` on
  `/v1/chat/completions`.
