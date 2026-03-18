---
name: ai-app-essentials
description: >
  Core knowledge for building AI applications with Claude — model IDs, SDK setup patterns,
  API parameters, error types, and common gotchas. Auto-activates when working on projects
  that import Anthropic SDK, Claude Agent SDK, or MCP SDK, or when the user asks about
  Claude API, model selection, token limits, or AI app architecture.
---

# AI App Essentials

## Current Model IDs (as of 2025)

| Model | ID | Best For |
|---|---|---|
| Claude Opus 4.6 | `claude-opus-4-6` | Complex reasoning, architecture, hard problems |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | General purpose, coding, analysis — best value |
| Claude Haiku 4.5 | `claude-haiku-4-5-20251001` | Fast tasks, classification, extraction — cheapest |

**Deprecated model IDs (do NOT use):**
- `claude-3-opus-20240229` → use `claude-opus-4-6`
- `claude-3-sonnet-20240229` → use `claude-sonnet-4-6`
- `claude-3-haiku-20240307` → use `claude-haiku-4-5-20251001`
- `claude-3-5-sonnet-20241022` → use `claude-sonnet-4-6`

## Context Windows

| Model | Input | Output |
|---|---|---|
| Opus 4.6 | 200K tokens | 32K tokens (standard) |
| Sonnet 4.6 | 200K tokens | 16K tokens (standard) |
| Haiku 4.5 | 200K tokens | 8K tokens (standard) |

Extended thinking can increase output limits significantly.

## SDK Setup — TypeScript

```typescript
import Anthropic from "@anthropic-ai/sdk";

// Create client — reads ANTHROPIC_API_KEY from env automatically
const client = new Anthropic();

// Basic message
const message = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Hello" }],
});

// With system prompt
const message = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  system: "You are a helpful assistant.",
  messages: [{ role: "user", content: "Hello" }],
});

// Streaming
const stream = client.messages.stream({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Hello" }],
});

for await (const event of stream) {
  if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
    process.stdout.write(event.delta.text);
  }
}
```

## SDK Setup — Python

```python
import anthropic

# Create client — reads ANTHROPIC_API_KEY from env automatically
client = anthropic.Anthropic()

# Basic message
message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)

# Async
async_client = anthropic.AsyncAnthropic()
message = await async_client.messages.create(...)

# Streaming
with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

## Required API Parameters

| Parameter | Required | Notes |
|---|---|---|
| `model` | Yes | Must be a valid model ID |
| `max_tokens` | Yes | Maximum output tokens (set appropriately, not too low) |
| `messages` | Yes | At least one user message |
| `system` | No | System prompt (string or array of content blocks) |
| `temperature` | No | 0-1, default 1. Use 0 for deterministic output |
| `tools` | No | Tool definitions for function calling |
| `stream` | No | Enable streaming (boolean) |

## Error Types

| Error | HTTP Code | Meaning | Action |
|---|---|---|---|
| `AuthenticationError` | 401 | Invalid API key | Check key format and value |
| `PermissionError` | 403 | Key lacks permission | Check API key tier/permissions |
| `NotFoundError` | 404 | Invalid model/endpoint | Check model ID, SDK version |
| `RateLimitError` | 429 | Too many requests | Built-in retry handles this; check usage tier |
| `APIError` | 500 | Server error | Retry with backoff |
| `OverloadedError` | 529 | API overloaded | Retry with longer backoff, consider different model |

## Tool Use Pattern

```typescript
const response = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  tools: [{
    name: "get_weather",
    description: "Get current weather for a location",
    input_schema: {
      type: "object",
      properties: {
        location: { type: "string", description: "City name" }
      },
      required: ["location"]
    }
  }],
  messages: [{ role: "user", content: "What's the weather in London?" }],
});

// Check if model wants to use a tool
if (response.stop_reason === "tool_use") {
  const toolUse = response.content.find(b => b.type === "tool_use");
  // Execute tool, then send result back
}
```

## Common Gotchas

1. **max_tokens is required** — Unlike some APIs, Claude requires you to set this explicitly
2. **API key from env** — SDK reads `ANTHROPIC_API_KEY` automatically; don't pass it explicitly unless needed
3. **System prompt is NOT a message** — It's a separate `system` parameter, not a message with `role: "system"`
4. **Streaming is a different method** — Use `.stream()` or `.messages.stream()`, not `.create({ stream: true })` in the TS SDK
5. **Tool results must be sent back** — If `stop_reason === "tool_use"`, you must send the tool result in the next turn
6. **Content is an array** — `response.content` is always an array of content blocks, not a string
7. **Token counting** — `response.usage.input_tokens` and `response.usage.output_tokens` for cost tracking
8. **No `role: "system"` in messages** — Messages array only has `user` and `assistant` roles
