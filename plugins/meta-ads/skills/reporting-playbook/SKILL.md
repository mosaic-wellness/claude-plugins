---
name: reporting-playbook
description: >
  Playbooks for common Meta ad reporting tasks such as spend pacing, campaign comparison,
  demographic breakdowns, creative diagnosis, and async report workflows. Auto-activates
  when the user asks for performance analysis, comparisons, trends, or reporting summaries.
---

# Reporting Playbook

Use these patterns when the user wants insight, not just raw data.

## 1. Fast Account Health Check

Goal: answer "how are our ads doing?" quickly.

1. Resolve the ad account.
2. Run `get_insights` at `campaign` level with `preset_fields: performance`.
3. Use `date_preset: last_7d`.
4. Sort by spend descending if the user asks for top spenders.
5. Summarize:
   - total spend
   - highest-spend campaigns
   - strongest and weakest CTR / CPC / cost_per_result patterns

## 2. Campaign Comparison

Goal: compare a small set of campaigns.

1. Use `list_campaigns` if names or IDs are not known.
2. Run `get_insights` at `campaign` level for the relevant window.
3. Filter or summarize only the named campaigns.
4. Compare:
   - spend
   - impressions
   - CTR
   - CPC
   - cost_per_result
   - ROAS if present

## 3. Demographic or Placement Diagnosis

Goal: explain why performance changed.

1. Start with a normal `get_insights` query to establish topline movement.
2. Re-run with one breakdown family:
   - `["age", "gender"]`
   - `["publisher_platform"]`
   - `["platform_position"]`
   - `["country"]`
3. If the user wants a long window or ad-level breakdowns, switch to `use_async: true`.
4. Summarize where cost and conversion efficiency diverge the most.

## 4. Creative Review

Goal: find underperforming or promising ads.

1. Use `list_ads` within a campaign or ad set.
2. Run `get_insights` at ad level with:
   - `preset_fields: delivery` or `video`
   - a recent window such as `last_7d`
3. Pair ad names with delivery metrics.
4. Highlight:
   - spend concentration
   - low CTR / high CPC ads
   - video retention drop-offs when available

## 5. Async Workflow

Use async reports when the request is naturally large.

1. Start `get_insights` with `use_async: true`.
2. Return the `report_run_id` immediately.
3. Poll with `get_async_report_status`.
4. Only fetch results when `async_status` indicates completion.
5. If results are huge, fetch them and summarize rather than dumping all rows back to the user.

## Interpretation Guardrails

- High spend with weak CTR often points to audience, creative, or placement inefficiency.
- Strong CTR with weak result efficiency often points to landing page mismatch or optimization-event issues.
- Compare like with like:
  - same time window
  - same level
  - same attribution assumptions where possible
- State uncertainty when important conversion fields are absent from the response.
