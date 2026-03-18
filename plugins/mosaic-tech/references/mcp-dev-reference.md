# MCP Server Development Reference

## What is MCP?

Model Context Protocol (MCP) is a standard for connecting AI models to external tools and data sources. You build an MCP server that exposes tools, and any MCP client (Claude Code, Claude Desktop, Cursor, etc.) can use them.

## Transport Types

| Transport | Use Case | Deployment |
|---|---|---|
| stdio | Local CLI tools, development | Runs as subprocess |
| HTTP (Streamable) | Team shared services, production | Central server |
| SSE | Legacy compatibility | Being deprecated in favor of HTTP |

## TypeScript MCP Server

### Setup

```bash
npm init -y
npm install @modelcontextprotocol/sdk zod
npm install -D typescript @types/node
```

### Basic Server (stdio)

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({
  name: "my-tools",
  version: "1.0.0",
});

// Define a tool
server.tool(
  "search_products",
  "Search the product catalog by name or category",
  {
    query: z.string().describe("Search query"),
    category: z.string().optional().describe("Filter by category"),
    limit: z.number().default(10).describe("Max results"),
  },
  async ({ query, category, limit }) => {
    const results = await searchProducts(query, category, limit);
    return {
      content: [{ type: "text", text: JSON.stringify(results, null, 2) }],
    };
  }
);

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
```

### HTTP Server

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import express from "express";

const app = express();
const server = new McpServer({ name: "my-tools", version: "1.0.0" });

// ... define tools ...

app.post("/mcp", async (req, res) => {
  const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });
  res.on("close", () => transport.close());
  await server.connect(transport);
  await transport.handleRequest(req, res);
});

app.listen(3000);
```

## Client Configuration (.mcp.json)

```json
{
  "mcpServers": {
    "my-tools-local": {
      "command": "node",
      "args": ["./dist/index.js"],
      "env": {
        "DATABASE_URL": "postgres://..."
      }
    },
    "my-tools-remote": {
      "type": "http",
      "url": "https://my-tools.example.com/mcp",
      "headers": {
        "x-api-key": "your-key-here"
      }
    }
  }
}
```

**Important:** For HTTP servers, you MUST include `"type": "http"` — without it, Claude Code won't connect.

## Tool Design Best Practices

### 1. Write Clear Descriptions
The model uses the description to decide when to call your tool. Be specific:

```typescript
// BAD — vague
server.tool("search", "Search for things", ...);

// GOOD — specific
server.tool(
  "search_products",
  "Search the product catalog by name, SKU, or category. Returns product name, price, stock status, and ID. Use for finding specific products or browsing categories.",
  ...
);
```

### 2. Use Zod for Validation
Zod provides runtime validation AND generates JSON Schema for the tool definition:

```typescript
server.tool("create_order", "Create a new order", {
  product_id: z.string().describe("Product ID from search results"),
  quantity: z.number().min(1).max(100).describe("Number of units"),
  shipping: z.enum(["standard", "express"]).describe("Shipping method"),
}, async (input) => { ... });
```

### 3. Return Structured Content
Always return well-structured text content:

```typescript
return {
  content: [{
    type: "text",
    text: JSON.stringify({
      success: true,
      data: results,
      count: results.length,
    }, null, 2)
  }]
};
```

### 4. Handle Errors Properly
Return error as content, don't throw:

```typescript
server.tool("get_user", "Get user details", { id: z.string() },
  async ({ id }) => {
    try {
      const user = await db.getUser(id);
      return { content: [{ type: "text", text: JSON.stringify(user) }] };
    } catch (error) {
      return {
        content: [{ type: "text", text: `Error: User ${id} not found` }],
        isError: true,
      };
    }
  }
);
```

### 5. Implement Authentication (HTTP)
For shared servers, always authenticate:

```typescript
app.post("/mcp", async (req, res) => {
  const apiKey = req.headers["x-api-key"];
  if (!apiKey || !isValidKey(apiKey)) {
    return res.status(401).json({ error: "Unauthorized" });
  }
  // ... handle MCP request
});
```

## Testing MCP Servers

### Manual Testing with Claude Code
```bash
# Add to .mcp.json and test interactively
claude  # Start Claude Code, it auto-connects to MCP servers
```

### Programmatic Testing
```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const transport = new StdioClientTransport({
  command: "node",
  args: ["./dist/index.js"],
});

const client = new Client({ name: "test-client", version: "1.0.0" });
await client.connect(transport);

// List tools
const tools = await client.listTools();
console.log(tools);

// Call a tool
const result = await client.callTool({
  name: "search_products",
  arguments: { query: "hair oil" },
});
console.log(result);
```

## Common Mistakes

1. **Missing `"type": "http"` in .mcp.json** — Claude Code defaults to stdio, won't connect to HTTP server
2. **No authentication on HTTP servers** — Anyone can call your tools
3. **Throwing errors instead of returning them** — Crashes the connection
4. **Tool names with spaces** — Use snake_case for tool names
5. **Too many tools (50+)** — Degrades model's tool selection; group related operations
6. **No CORS for browser-based clients** — Add CORS headers if needed
7. **Blocking operations without timeout** — Long-running tools should have timeouts
