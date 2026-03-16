# claude-plugins

Claude Code plugins for Mosaic Wellness teams.

## Available Plugins

| Plugin | Description |
|---|---|
| [mosaic-admin](./plugins/mosaic-admin/) | Admin MCP plugin for managing page configs (PDPs, widget pages, experiments) via Zeus |

## Installation

```bash
# 1. Add the marketplace (one-time)
/plugin marketplace add mosaic-wellness/claude-plugins

# 2. Install any plugin
/plugin install mosaic-admin
```

## Adding a New Plugin

1. Create a directory under `plugins/your-plugin-name/`
2. Add `.claude-plugin/plugin.json` with name, version, description
3. Add your commands, agents, skills, hooks
4. Register the plugin in `.claude-plugin/marketplace.json` at the repo root
5. Bump version in both `plugin.json` and `marketplace.json` for updates
