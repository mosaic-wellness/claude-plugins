# mosaic-admin — Claude Code Plugin

Admin MCP plugin for managing Mosaic Wellness page configs (PDPs, widget pages, experiments, brand settings) via the Zeus admin-mcp server.

## Prerequisites

- Claude Code CLI installed
- Access to the admin-mcp staging server (ask DevOps for the API key prefix `amk_`)

## Installation

### Via Marketplace (recommended)

```bash
# 1. Add the marketplace (one-time)
/plugin marketplace add mosaic-wellness/ai-playbooks

# 2. Install the plugin
/plugin install mosaic-admin
```

### Via Local Path (development)

If you're working on the plugin itself from the `core-stack` monorepo:

```bash
claude plugins add /path/to/core-stack/ai-playbooks/plugins/mosaic-admin
```

## First-Time Setup

Run `/mosaic-admin setup` in Claude Code. The command will:

1. Check for `.mcp.json` in the project root
2. Guide you through creating an API key via the admin dashboard
3. Write the `admin-mcp` server entry to `.mcp.json`

You'll need to approve the MCP server trust dialog once.

## Usage

```
/mosaic-admin                           # Interactive menu
/mosaic-admin setup                     # Configure MCP connection
/mosaic-admin update hero on mm PDP     # Edit existing page content
/mosaic-admin create monsoon sale page  # Build a new page
/mosaic-admin check experiments on bw   # Manage A/B tests
```

## Components

| Type | Name | Purpose |
|---|---|---|
| Command | `/mosaic-admin` | Entry point — setup + interactive routing |
| Agent | `page-editor` | Edit existing PDPs and widget pages |
| Agent | `page-builder` | Create new pages (clone + customize) |
| Agent | `experiment-manager` | A/B experiment lifecycle |
| Skill | `admin-essentials` | Brand codes, URL resolution, gotchas |
| Hook | PreToolUse | Safety check on all write operations |

## Safety

- **Staging only** — all writes go to staging S3. Production publishing is only available through the admin dashboard UI.
- **Lock-based editing** — agents acquire page locks before writes and release them after.
- **Brand guard hook** — warns before writing to non-default brands (anything other than `mm`).

## Reference Docs

The `references/` directory contains 9 guides (1,500+ lines) covering tools, workflows, brands, error handling, and domain concepts. Agents and skills load these automatically.
