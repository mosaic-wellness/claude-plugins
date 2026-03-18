# Agent SDK Reference

## What is the Agent SDK?

The Agent SDK provides frameworks for building autonomous AI agents that can use tools, make decisions, and complete multi-step tasks.

- **Python:** `claude_agent_sdk` — full-featured agent framework
- **TypeScript:** `@anthropic-ai/claude-code-sdk` — Claude Code as a subprocess

## Python Agent SDK

### Installation

```bash
pip install claude-agent-sdk
```

### Basic Agent

```python
from claude_agent_sdk import Agent, tool

@tool
def search_docs(query: str) -> str:
    """Search documentation for relevant information."""
    # Your search implementation
    return f"Results for: {query}"

agent = Agent(
    model="claude-sonnet-4-6",
    tools=[search_docs],
    system_prompt="You are a documentation assistant.",
)

result = agent.run("How do I set up authentication?")
print(result)
```

### Best Practices

1. **Define clear tool descriptions** — The model uses descriptions to decide when to call tools. Be specific about what the tool does, its inputs, and its outputs.

2. **Set termination conditions** — Always configure `max_turns` or a custom stop condition to prevent infinite loops:
   ```python
   agent = Agent(
       model="claude-sonnet-4-6",
       tools=[...],
       max_turns=10,  # Safety limit
   )
   ```

3. **Type your tool parameters** — Use Python type hints for automatic schema generation:
   ```python
   @tool
   def create_user(name: str, email: str, role: str = "viewer") -> dict:
       """Create a new user account."""
       ...
   ```

4. **Handle tool errors gracefully** — Return error messages as strings, don't raise exceptions:
   ```python
   @tool
   def get_user(user_id: str) -> str:
       try:
           user = db.get(user_id)
           return json.dumps(user)
       except NotFoundError:
           return f"User {user_id} not found"
   ```

5. **Add human-in-the-loop for destructive actions:**
   ```python
   @tool
   def delete_record(record_id: str) -> str:
       """Delete a record. Requires confirmation."""
       confirm = input(f"Delete record {record_id}? (y/n): ")
       if confirm != "y":
           return "Deletion cancelled by user"
       # proceed with deletion
   ```

## TypeScript Claude Code SDK

### Installation

```bash
npm install @anthropic-ai/claude-code-sdk
```

### Basic Usage

```typescript
import { claude } from "@anthropic-ai/claude-code-sdk";

const result = await claude({
  prompt: "Find all TODO comments in the codebase",
  options: {
    maxTurns: 10,
    allowedTools: ["Read", "Glob", "Grep"],
  },
});

console.log(result.output);
```

### Best Practices

1. **Restrict tool access** — Only allow the tools the agent actually needs
2. **Set maxTurns** — Prevent runaway agents
3. **Use for code tasks** — This SDK is optimized for coding workflows

## Agent Architecture Patterns

### Simple Loop (Single Agent)
Best for: Focused tasks with clear completion criteria
```
User → Agent → Tool → Agent → Tool → ... → Response
```

### Router Pattern
Best for: Tasks that need different expertise
```
User → Router Agent → picks Specialist Agent → completes task
```

### Pipeline Pattern
Best for: Sequential processing stages
```
Input → Agent A (extract) → Agent B (transform) → Agent C (validate) → Output
```

### Parallel Pattern
Best for: Independent subtasks
```
         ┌→ Agent A (research) ─┐
Input ───┼→ Agent B (analyze)  ─┼→ Aggregator → Output
         └→ Agent C (validate) ─┘
```

## Common Mistakes

1. **No max_turns** — Agent loops forever; always set a limit
2. **Vague tool descriptions** — Model picks wrong tools; be specific
3. **Giant tool responses** — Returning 10MB of data fills context; paginate or summarize
4. **No error handling in tools** — Unhandled exceptions crash the agent loop
5. **Too many tools** — More than 15-20 tools degrades selection accuracy; group or specialize
6. **Stateful tools without cleanup** — File handles, DB connections left open; use context managers
