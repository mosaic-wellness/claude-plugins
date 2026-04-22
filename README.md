# Claude Plugins

Claude Code plugins for Mosaic Wellness teams.

## Available Plugins

| Plugin | What it does |
|--------|-------------|
| [mosaic-buddy](./plugins/mosaic-buddy/) | Technical co-pilot — health checks, reviews, brainstorming, docs, debugging, coaching |
| [mosaic-admin](./plugins/mosaic-admin/) | Admin MCP plugin for managing page configs (PDPs, widget pages, experiments) via Zeus |

## Quick Start

```bash
# Install the plugin (one-time)
/install-plugin https://github.com/mosaic-wellness/claude-plugins

# Use it
/mosaic-buddy              # interactive menu
/mosaic-buddy doctor       # health check your project
/mosaic-admin              # manage page configs
```

## Adding a New Plugin

1. Create a directory under `plugins/your-plugin-name/`
2. Add `.claude-plugin/plugin.json` with name, version, description
3. Add your commands, agents, skills, hooks
4. Register the plugin in `.claude-plugin/marketplace.json` at the repo root
5. Run `scripts/bump.sh <name> minor --commit` to version and publish
