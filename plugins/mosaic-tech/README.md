# mosaic-tech

AI application development assistant for Mosaic Wellness engineering teams. One-click setup review, debugging, architecture guidance, and security audits for projects using Claude API, Agent SDK, and MCP servers.

## Installation

```bash
# From marketplace (team-wide)
/plugin marketplace add mosaic-wellness/claude-plugins
/plugin install mosaic-tech

# Local development
claude plugins add /path/to/claude-plugins/plugins/mosaic-tech
```

## Usage

```bash
/mosaic-tech              # Interactive menu
/mosaic-tech review       # Full project setup review
/mosaic-tech debug        # Troubleshoot broken setup
/mosaic-tech security     # Security audit
/mosaic-tech stack        # Architecture/model guidance
```

## Components

### Agents

| Agent | Purpose |
|---|---|
| `setup-reviewer` | Scans project for config issues, outdated SDKs, missing best practices |
| `debugger` | Troubleshoots API errors, connection failures, runtime issues |
| `security-auditor` | Finds leaked keys, prompt injection risks, unsafe patterns |
| `stack-advisor` | Recommends architecture, model, SDK for your use case |

### Skills (auto-loaded knowledge)

| Skill | Content |
|---|---|
| `ai-app-essentials` | Model IDs, SDK setup, API parameters, common gotchas |
| `security-checklist` | API key management, prompt injection, PII handling |

### Hooks

| Hook | Trigger | Action |
|---|---|---|
| PreToolUse (Write/Edit) | Before writing files | Warns if hardcoded API keys detected |
| PostToolUse (Bash) | After running commands | Warns if API keys appear in output |

### References

| Document | Content |
|---|---|
| `claude-api-reference.md` | Claude API patterns, streaming, tool use, caching |
| `agent-sdk-reference.md` | Agent SDK setup, patterns, architecture |
| `mcp-dev-reference.md` | MCP server development, transport types, testing |
| `testing-ai-apps.md` | Unit/integration/eval testing strategies |
| `cost-optimization.md` | Model routing, caching, batch API, token management |
| `prompt-engineering.md` | System prompts, few-shot, structured output |

## What It Checks (Setup Review)

- SDK versions (current vs deprecated)
- API key management (.env, .gitignore)
- Error handling and retry logic
- Model configuration (IDs, max_tokens, temperature)
- MCP server setup (transport, auth, .mcp.json)
- Streaming and performance patterns
- Project structure and testing
- Agent SDK configuration (if applicable)

## Safety

- **Never prints actual API keys** — always redacted in output
- **Hooks catch accidental key commits** — warns before writing files with keys
- **Git history scanning** — checks for previously committed secrets
- **No destructive actions** — read-only analysis with recommendations
