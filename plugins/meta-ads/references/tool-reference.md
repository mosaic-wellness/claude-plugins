# Meta Ads Tool Reference

## `list_ad_accounts`

Use when:
- the user does not know the correct ad account
- you need to validate token access
- the user works across multiple businesses or clients

Notes:
- `business_id` can be used to list `owned`, `client`, or `all` business-linked accounts
- without `business_id`, the tool uses `me/adaccounts`

## `list_campaigns`

Use when:
- the user wants a list of campaigns
- you need campaign IDs before running detailed insights
- you want a compact browse step before performance analysis

## `list_ad_sets`

Use when:
- the analysis is about targeting, budget buckets, or ad set delivery
- the user named a campaign and wants the ad sets underneath it

## `list_ads`

Use when:
- the user wants ad-level inventory or creative inspection
- you need ad IDs before running ad-level insights

Use `include_creative_fields: true` only when necessary.

## `get_object`

Use when:
- you already know the exact object ID
- the user wants fields for one campaign, ad set, ad, creative, or report run

## `get_insights`

Use when:
- the user asks about spend, CTR, CPC, ROAS, reach, or performance
- the user wants delivery broken down by campaign, ad set, or ad
- the user asks for a demographic, placement, or country breakdown

Important inputs:
- `object_id`
- `level`
- `preset_fields` or `fields`
- `date_preset` or `time_range`
- `breakdowns`
- `use_async`

## `get_async_report_status`

Use when:
- `get_insights` returned `report_run_id`
- the job is still running
- you want to fetch results only after completion
