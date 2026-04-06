# Reporting Examples

## Last 7 Days By Campaign

```json
{
  "object_id": "act_1234567890",
  "level": "campaign",
  "preset_fields": "performance",
  "date_preset": "last_7d"
}
```

## Daily Spend Trend

```json
{
  "object_id": "act_1234567890",
  "level": "campaign",
  "preset_fields": "delivery",
  "date_preset": "last_30d",
  "time_increment": 1
}
```

## Country Breakdown

```json
{
  "object_id": "act_1234567890",
  "level": "campaign",
  "preset_fields": "performance",
  "time_range": {
    "since": "2026-03-01",
    "until": "2026-03-31"
  },
  "breakdowns": ["country"],
  "use_async": true
}
```

## Video Creative Review

```json
{
  "object_id": "act_1234567890",
  "level": "ad",
  "preset_fields": "video",
  "date_preset": "last_7d"
}
```
