# Meta Ads Setup And Auth

This plugin uses a local stdio MCP server instead of a hosted service. Claude Code launches the server locally, and that process calls Meta's Graph/Marketing API with credentials supplied through environment variables.

## Recommended Secret Layout

Keep secrets in a user-local file:

```bash
~/.config/claude/meta-ads.env
```

Suggested contents:

```bash
export META_ACCESS_TOKEN='YOUR_TOKEN_HERE'
export META_APP_SECRET='YOUR_APP_SECRET_HERE'
export META_API_VERSION='v25.0'
export META_DEFAULT_AD_ACCOUNT_ID='act_1234567890'
```

Set restrictive permissions:

```bash
chmod 600 ~/.config/claude/meta-ads.env
```

## Recommended `.mcp.json` Entry

The setup command should write an entry like this, preserving any other MCP servers:

```json
{
  "mcpServers": {
    "meta-ads": {
      "command": "/bin/zsh",
      "args": [
        "-lc",
        "set -a && source ~/.config/claude/meta-ads.env && set +a && python3 /absolute/path/to/plugins/meta-ads/scripts/meta_ads_mcp.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

## Research Notes

The plugin design follows current official Meta guidance exposed in the Business SDK quick starts and Graph API security docs:

- Meta's official Business SDK quick starts say a Meta app must add the Marketing API product before use.
- The same quick starts recommend turning on **App Secret Proof for Server API calls** in the app settings.
- Official SDK examples also center the ad account hierarchy (`act_<id>`), cursor-style pagination, and explicit field selection instead of broad "fetch everything" requests.

The plugin therefore:

- supports App Secret Proof automatically when `META_APP_SECRET` is present
- keeps default field presets intentionally small
- paginates list/report responses conservatively
- exposes async insights polling for large reports

## Token Scope Guidance

Meta's official SDK quick starts document `ads_management` in their access-token examples. For this plugin's read-only reporting use cases, prefer the narrowest token your team's Meta app setup supports. If your org already uses a broader Marketing API token standard, the plugin still works because it only exposes read operations.
