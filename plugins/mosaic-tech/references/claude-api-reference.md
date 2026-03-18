# Claude API Reference

## Authentication

The Anthropic SDK automatically reads `ANTHROPIC_API_KEY` from the environment. You can also pass it explicitly:

```typescript
// TypeScript — auto from env (recommended)
const client = new Anthropic();

// TypeScript — explicit
const client = new Anthropic({ apiKey: "sk-ant-..." });

// Python — auto from env (recommended)
client = anthropic.Anthropic()

// Python — explicit
client = anthropic.Anthropic(api_key="sk-ant-...")
```

## Messages API

### Basic Request

```typescript
const response = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  system: "You are a helpful coding assistant.",
  messages: [
    { role: "user", content: "Write a fibonacci function in TypeScript" }
  ],
});

console.log(response.content[0].text);
```

### Multi-turn Conversation

```typescript
const messages = [
  { role: "user", content: "What is 2+2?" },
  { role: "assistant", content: "2+2 equals 4." },
  { role: "user", content: "And what about 3+3?" },
];

const response = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  messages,
});
```

### Streaming

```typescript
// TypeScript SDK streaming
const stream = client.messages.stream({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Write a poem" }],
});

stream.on("text", (text) => process.stdout.write(text));
const finalMessage = await stream.finalMessage();
```

```python
# Python SDK streaming
with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Write a poem"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

### Tool Use

```typescript
const tools = [{
  name: "search_database",
  description: "Search the product database by query string. Returns matching products with name, price, and ID.",
  input_schema: {
    type: "object",
    properties: {
      query: { type: "string", description: "Search query" },
      limit: { type: "number", description: "Max results (default 10)" }
    },
    required: ["query"]
  }
}];

const response = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  tools,
  messages: [{ role: "user", content: "Find products matching 'hair oil'" }],
});

// Handle tool use
if (response.stop_reason === "tool_use") {
  const toolBlock = response.content.find(b => b.type === "tool_use");
  const result = await executeMyTool(toolBlock.name, toolBlock.input);

  // Send result back
  const followUp = await client.messages.create({
    model: "claude-sonnet-4-6",
    max_tokens: 1024,
    tools,
    messages: [
      { role: "user", content: "Find products matching 'hair oil'" },
      { role: "assistant", content: response.content },
      { role: "user", content: [{
        type: "tool_result",
        tool_use_id: toolBlock.id,
        content: JSON.stringify(result)
      }]}
    ],
  });
}
```

### Vision (Images)

```typescript
const response = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  messages: [{
    role: "user",
    content: [
      {
        type: "image",
        source: { type: "url", url: "https://example.com/image.png" }
      },
      { type: "text", text: "Describe this image" }
    ]
  }],
});
```

### Structured Output (JSON Mode)

```typescript
const response = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  system: "Always respond with valid JSON.",
  messages: [{
    role: "user",
    content: "Extract: name, email, phone from this text: John Doe, john@example.com, 555-1234"
  }],
});
```

For guaranteed JSON structure, use tool use with a strict schema — the model will conform to the input_schema.

## Error Handling

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

try {
  const message = await client.messages.create({ ... });
} catch (error) {
  if (error instanceof Anthropic.AuthenticationError) {
    console.error("Invalid API key");
  } else if (error instanceof Anthropic.RateLimitError) {
    console.error("Rate limited — SDK will auto-retry by default");
  } else if (error instanceof Anthropic.APIError) {
    console.error(`API error: ${error.status} ${error.message}`);
  } else {
    throw error;
  }
}
```

## Configuration Options

```typescript
const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,  // default: reads from env
  maxRetries: 2,       // default: 2 (set 0 to disable)
  timeout: 60_000,     // default: 10 minutes (in ms)
  baseURL: "...",      // override API endpoint (rare)
});
```

## Prompt Caching

For repeated system prompts or context, use prompt caching to reduce costs:

```typescript
const response = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  system: [{
    type: "text",
    text: "Very long system prompt...",
    cache_control: { type: "ephemeral" }
  }],
  messages: [{ role: "user", content: "Question" }],
});
```

Cached input tokens cost 90% less. Cache TTL is 5 minutes (refreshed on use).

## Batch API

For non-real-time processing (50% cheaper):

```typescript
const batch = await client.messages.batches.create({
  requests: items.map((item, i) => ({
    custom_id: `item-${i}`,
    params: {
      model: "claude-haiku-4-5-20251001",
      max_tokens: 1024,
      messages: [{ role: "user", content: item.prompt }],
    }
  }))
});
```

Results available within 24 hours. Great for bulk classification, extraction, or content generation.
