---
name: meta-ads-essentials
description: >
  Core knowledge for using the meta-ads MCP server safely and effectively: setup, ad account
  discovery, object hierarchy, sync vs async insights, date windows, and compact field selection.
  Auto-activates whenever meta-ads MCP tools are in play or the user asks about Meta, Facebook,
  or Instagram ad performance.
---

# Meta Ads Essentials

You are working with the `meta-ads` MCP server, a read-only bridge to the Meta Marketing API for ad account discovery and reporting.

## Safety Defaults

- Prefer the user-local secret file `~/.config/claude/meta-ads.env`.
- Do not ask users to commit real access tokens or app secrets to `.mcp.json`.
- If setup is missing, route through `/meta-ads setup`.
- Treat the plugin as read-only. It is not for creating or editing campaigns.

## Auth and Setup

- Required env var: `META_ACCESS_TOKEN`
- Recommended env var: `META_APP_SECRET`
- Optional env vars:
  - `META_API_VERSION` (default `v25.0`)
  - `META_DEFAULT_AD_ACCOUNT_ID` (recommended once the correct account is known)

If the user has not configured a default account, call `list_ad_accounts` first.

## Object Hierarchy

```
Ad Account (act_<id>)
  -> Campaign
    -> Ad Set
      -> Ad
        -> Creative
```

## Tool Selection

### Discover access
- Use `list_ad_accounts` when:
  - the user does not know their ad account ID
  - the token might map to multiple accounts
  - you need to confirm business-owned vs client accounts

### Browse objects
- Use `list_campaigns` for campaign inventory
- Use `list_ad_sets` for ad set targeting/budget inspection
- Use `list_ads` for ad-level creative and delivery drill-down
- Use `get_object` once you already know the exact ID

### Run reporting
- Use `get_insights` for delivery and performance reporting
- Use `get_async_report_status` only after `get_insights` returns `report_run_id`

## Reporting Defaults

If the user does not specify a timeframe:
- Default to `last_7d` for recent performance questions
- Use exact `time_range` when the user references explicit dates

If the user does not specify a level:
- Use `campaign` when the object is an ad account
- Use the object's natural scope for campaign/ad set/ad IDs

If the user does not specify fields:
- Use `preset_fields: "performance"` for general spend/performance analysis
- Use `preset_fields: "delivery"` for basic media delivery checks
- Use `preset_fields: "video"` for video creative review

## Sync vs Async

Use synchronous insights when:
- the window is small
- there are no or few breakdowns
- the user wants a fast answer

Use async insights when:
- the date range is large
- multiple breakdowns are requested
- ad-level row counts will be high
- the first sync attempt times out or returns too much data

## Compact Query Guidance

- Always request the narrowest useful field set.
- Always ask for a specific ad account if multiple are accessible.
- Add `time_increment: "1"` or `daily` style increments only when trend analysis matters.
- Avoid requesting many breakdowns at once unless the user explicitly wants them.

## Common Analysis Patterns

### Spend by campaign
Use `get_insights` with:
- `object_id: act_<id>`
- `level: campaign`
- `preset_fields: performance`
- `date_preset: last_7d`

### Delivery by ad set
Use `get_insights` with:
- `object_id: act_<id>`
- `level: adset`
- `preset_fields: delivery`

### Demographic breakdown
Use `get_insights` with:
- `breakdowns: ["age", "gender"]`
- `use_async: true` if the window is wide

### Geo breakdown
Use `get_insights` with:
- `breakdowns: ["country"]`

## Response Discipline

- Summarize the answer in business terms, not just raw JSON.
- Call out the exact date window you used.
- If there are multiple accounts and the user did not specify one, ask instead of guessing.
- If the results are empty, say whether that likely means no spend, wrong account, or an overly narrow filter.
