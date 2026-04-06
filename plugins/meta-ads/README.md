# meta-ads

Claude Code plugin for Meta ad reporting. It adds a local stdio MCP server for Meta Marketing API reads, plus setup and reporting guidance so agents can answer spend, delivery, campaign, ad set, and ad performance questions without making the user think about Graph API details.

## Installation

```bash
# From marketplace
/plugin marketplace add mosaic-wellness/claude-plugins
/plugin install meta-ads

# Local development
claude plugins add /path/to/claude-plugins/plugins/meta-ads
```

## First-Time Setup

Run `/meta-ads setup`.

The command will:

1. Create `~/.config/claude/meta-ads.env` with placeholders
2. Add a `meta-ads` stdio server entry to the current project's `.mcp.json`
3. Point that entry at the plugin's local Python MCP bridge
4. Keep secrets out of the repository by sourcing them from the user-local env file

Default env file contents:

```bash
export META_ACCESS_TOKEN='YOUR_TOKEN_HERE'
export META_APP_SECRET='YOUR_APP_SECRET_HERE'
export META_API_VERSION='v25.0'
export META_DEFAULT_AD_ACCOUNT_ID='act_1234567890'
```

## Usage

```bash
/meta-ads
/meta-ads setup
/meta-ads list my ad accounts
/meta-ads show spend by campaign for the last 7 days
/meta-ads compare age and gender breakdown for act_123 in March
/meta-ads fetch async report 987654321 and include results
```

## Components

| Type | Name | Purpose |
|---|---|---|
| Command | `/meta-ads` | Setup, routing, and normal user entry point |
| MCP | `meta-ads` | Local stdio server that calls Meta Graph/Marketing API |
| Skill | `meta-ads-essentials` | Safe defaults, hierarchy, auth, and query design |
| Skill | `reporting-playbook` | Common reporting and diagnosis workflows |
| Hook | PreToolUse/PostToolUse | Prevent accidental token leakage into repo files or terminal output |

## MCP Tools

| Tool | Purpose |
|---|---|
| `list_ad_accounts` | Discover accessible ad accounts |
| `list_campaigns` | Browse campaigns within an ad account |
| `list_ad_sets` | Browse ad sets at account or campaign scope |
| `list_ads` | Browse ads at account, campaign, or ad set scope |
| `get_object` | Fetch a single ad account, campaign, ad set, ad, creative, or async report run |
| `get_insights` | Run sync or async insights queries with safe presets |
| `get_async_report_status` | Poll async report runs and fetch rows when complete |

## Design Choices

- **Read-only by design**: the MCP bridge only exposes reporting and inspection operations.
- **No extra package install**: the server uses only Python's standard library.
- **Secret-safe setup**: the recommended flow stores tokens in `~/.config/claude/meta-ads.env`, not in repo files.
- **Async ready**: wide or breakdown-heavy insights jobs can be started asynchronously and polled later.
- **Field-limited defaults**: tool presets intentionally request a compact field set to keep responses fast and usable in agent context.

## Notes

- The default API version is `v25.0`, but it is fully configurable via `META_API_VERSION`.
- If your team manages multiple businesses or tokens, start with `/meta-ads list my ad accounts` before setting a default ad account.
- The plugin supports Facebook and Instagram ad reporting wherever the Meta Marketing API surfaces those entities.
