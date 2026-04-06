#!/usr/bin/env python3
"""Dependency-light stdio MCP server for Meta Marketing API reads.

This server intentionally uses only the Python standard library so users can
point Claude Code at it without installing an SDK first.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


SERVER_NAME = "meta-ads"
SERVER_VERSION = "1.0.0"
DEFAULT_API_VERSION = os.environ.get("META_API_VERSION", "v25.0")
DEFAULT_TIMEOUT_SECONDS = int(os.environ.get("META_TIMEOUT_SECONDS", "30"))
DEFAULT_PAGE_LIMIT = int(os.environ.get("META_DEFAULT_PAGE_LIMIT", "25"))
DEFAULT_MAX_PAGES = int(os.environ.get("META_DEFAULT_MAX_PAGES", "1"))
GRAPH_HOST = "https://graph.facebook.com"


INSIGHTS_FIELD_PRESETS = {
    "delivery": [
        "account_id",
        "account_name",
        "campaign_id",
        "campaign_name",
        "adset_id",
        "adset_name",
        "ad_id",
        "ad_name",
        "date_start",
        "date_stop",
        "spend",
        "impressions",
        "reach",
        "frequency",
        "cpm",
        "cpc",
        "ctr",
        "clicks",
        "inline_link_clicks",
        "inline_link_click_ctr",
    ],
    "performance": [
        "account_id",
        "account_name",
        "campaign_id",
        "campaign_name",
        "objective",
        "optimization_goal",
        "date_start",
        "date_stop",
        "spend",
        "impressions",
        "reach",
        "frequency",
        "cpm",
        "cpc",
        "ctr",
        "clicks",
        "inline_link_clicks",
        "inline_link_click_ctr",
        "results",
        "cost_per_result",
        "purchase_roas",
    ],
    "video": [
        "account_id",
        "account_name",
        "campaign_id",
        "campaign_name",
        "date_start",
        "date_stop",
        "spend",
        "impressions",
        "reach",
        "video_play_actions",
        "video_p25_watched_actions",
        "video_p50_watched_actions",
        "video_p75_watched_actions",
        "video_p95_watched_actions",
        "video_p100_watched_actions",
        "video_avg_time_watched_actions",
        "video_thruplay_watched_actions",
    ],
}

OBJECT_FIELD_PRESETS = {
    "ad_account": [
        "id",
        "account_id",
        "name",
        "account_status",
        "currency",
        "timezone_name",
        "timezone_offset_hours_utc",
        "amount_spent",
        "spend_cap",
        "business",
    ],
    "campaign": [
        "id",
        "name",
        "status",
        "effective_status",
        "objective",
        "buying_type",
        "bid_strategy",
        "daily_budget",
        "lifetime_budget",
        "start_time",
        "stop_time",
        "created_time",
        "updated_time",
    ],
    "adset": [
        "id",
        "name",
        "status",
        "effective_status",
        "campaign_id",
        "optimization_goal",
        "billing_event",
        "bid_strategy",
        "daily_budget",
        "lifetime_budget",
        "start_time",
        "end_time",
        "created_time",
        "updated_time",
        "targeting",
    ],
    "ad": [
        "id",
        "name",
        "status",
        "effective_status",
        "campaign_id",
        "adset_id",
        "creative",
        "configured_status",
        "conversion_domain",
        "created_time",
        "updated_time",
    ],
    "adcreative": [
        "id",
        "name",
        "title",
        "body",
        "object_story_spec",
        "asset_feed_spec",
        "image_hash",
        "thumbnail_url",
        "url_tags",
    ],
    "report_run": [
        "id",
        "account_id",
        "async_percent_completion",
        "async_status",
        "date_start",
        "date_stop",
        "is_running",
        "time_ref",
        "schedule_id",
    ],
}


def _json_dumps(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=True, separators=(",", ":"))


def _read_message() -> dict[str, Any] | None:
    content_length = None
    while True:
        header_line = sys.stdin.buffer.readline()
        if not header_line:
            return None
        if header_line in (b"\r\n", b"\n"):
            break
        key, _, value = header_line.decode("utf-8").partition(":")
        if key.lower() == "content-length":
            content_length = int(value.strip())
    if content_length is None:
        raise ValueError("Missing Content-Length header")
    body = sys.stdin.buffer.read(content_length)
    return json.loads(body.decode("utf-8"))


def _write_message(message: dict[str, Any]) -> None:
    body = _json_dumps(message).encode("utf-8")
    header = f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8")
    sys.stdout.buffer.write(header)
    sys.stdout.buffer.write(body)
    sys.stdout.buffer.flush()


def _response(message_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": message_id, "result": result}


def _error(message_id: Any, code: int, message: str, data: Any | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": message_id,
        "error": {"code": code, "message": message},
    }
    if data is not None:
        payload["error"]["data"] = data
    return payload


def _coerce_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return [str(value).strip()]


def _coerce_account_id(account_id: str) -> str:
    account_id = str(account_id).strip()
    if not account_id:
        raise ValueError("ad_account_id is required")
    return account_id if account_id.startswith("act_") else f"act_{account_id}"


def _pick_fields(explicit_fields: Any, preset_name: str | None, default_fields: list[str]) -> list[str]:
    fields = _coerce_list(explicit_fields)
    if fields:
        return fields
    if preset_name:
        preset = INSIGHTS_FIELD_PRESETS.get(preset_name) or OBJECT_FIELD_PRESETS.get(preset_name)
        if preset:
            return preset
    return default_fields


def _encode_graph_params(params: dict[str, Any]) -> dict[str, str]:
    encoded: dict[str, str] = {}
    for key, value in params.items():
        if value is None or value == "":
            continue
        if isinstance(value, bool):
            encoded[key] = "true" if value else "false"
        elif isinstance(value, (dict, list)):
            encoded[key] = json.dumps(value, separators=(",", ":"))
        else:
            encoded[key] = str(value)
    return encoded


def _sanitize_url(url: str | None) -> str | None:
    if not url:
        return url
    parsed = urllib.parse.urlsplit(url)
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    safe_query = [
        (key, value)
        for key, value in query
        if key not in {"access_token", "appsecret_proof"}
    ]
    return urllib.parse.urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, urllib.parse.urlencode(safe_query), parsed.fragment)
    )


def _sanitize_payload(payload: Any) -> Any:
    if isinstance(payload, dict):
        sanitized: dict[str, Any] = {}
        for key, value in payload.items():
            if key in {"access_token", "appsecret_proof"}:
                continue
            if key == "paging" and isinstance(value, dict):
                sanitized[key] = {
                    inner_key: _sanitize_url(inner_value) if inner_key in {"next", "previous"} else _sanitize_payload(inner_value)
                    for inner_key, inner_value in value.items()
                }
                continue
            sanitized[key] = _sanitize_payload(value)
        return sanitized
    if isinstance(payload, list):
        return [_sanitize_payload(item) for item in payload]
    return payload


def _format_tool_result(payload: Any, is_error: bool = False) -> dict[str, Any]:
    return {
        "content": [{"type": "text", "text": json.dumps(_sanitize_payload(payload), indent=2, sort_keys=True)}],
        "isError": is_error,
    }


def _meta_error_summary(error_payload: dict[str, Any]) -> dict[str, Any]:
    error = error_payload.get("error", {}) if isinstance(error_payload, dict) else {}
    return {
        "message": error.get("message", "Meta API request failed"),
        "type": error.get("type"),
        "code": error.get("code"),
        "error_subcode": error.get("error_subcode"),
        "fbtrace_id": error.get("fbtrace_id"),
    }


class MetaApiClient:
    def __init__(self) -> None:
        self.access_token = os.environ.get("META_ACCESS_TOKEN", "").strip()
        self.app_secret = os.environ.get("META_APP_SECRET", "").strip()
        self.api_version = os.environ.get("META_API_VERSION", DEFAULT_API_VERSION).strip() or DEFAULT_API_VERSION
        self.default_ad_account_id = os.environ.get("META_DEFAULT_AD_ACCOUNT_ID", "").strip()
        self.timeout_seconds = int(os.environ.get("META_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)))

    def ensure_configured(self) -> None:
        if not self.access_token:
            raise RuntimeError(
                "META_ACCESS_TOKEN is not configured. Run /meta-ads setup or export META_ACCESS_TOKEN before starting Claude Code."
            )

    def _appsecret_proof(self) -> str | None:
        if not self.app_secret or not self.access_token:
            return None
        return hmac.new(
            self.app_secret.encode("utf-8"),
            msg=self.access_token.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

    def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        retries: int = 2,
    ) -> dict[str, Any]:
        self.ensure_configured()
        request_params = dict(params or {})
        request_params["access_token"] = self.access_token
        proof = self._appsecret_proof()
        if proof:
            request_params["appsecret_proof"] = proof

        encoded_params = _encode_graph_params(request_params)
        url = f"{GRAPH_HOST}/{self.api_version}/{path.lstrip('/')}"
        request_data = None
        request_headers = {
            "Accept": "application/json",
            "User-Agent": f"{SERVER_NAME}/{SERVER_VERSION}",
        }

        if method.upper() == "GET":
            if encoded_params:
                url = f"{url}?{urllib.parse.urlencode(encoded_params)}"
        else:
            request_headers["Content-Type"] = "application/x-www-form-urlencoded"
            request_data = urllib.parse.urlencode(encoded_params).encode("utf-8")

        request = urllib.request.Request(url, data=request_data, method=method.upper(), headers=request_headers)

        for attempt in range(retries + 1):
            try:
                with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                    body = response.read().decode("utf-8")
                    return json.loads(body)
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                payload: dict[str, Any]
                try:
                    payload = json.loads(body)
                except json.JSONDecodeError:
                    payload = {"error": {"message": body or f"HTTP {exc.code}", "code": exc.code}}

                error_info = payload.get("error", {})
                meta_code = error_info.get("code")
                retryable = exc.code in {429, 500, 502, 503, 504} or meta_code in {1, 2, 4, 17, 32, 613}
                if retryable and attempt < retries:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                raise RuntimeError(json.dumps(_meta_error_summary(payload)))
            except urllib.error.URLError as exc:
                if attempt < retries:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                raise RuntimeError(f"Network error calling Meta API: {exc.reason}") from exc


CLIENT = MetaApiClient()


TOOLS = [
    {
        "name": "list_ad_accounts",
        "description": (
            "List ad accounts available to the configured Meta token. Use this first when the user "
            "does not know the correct act_<id> value. If business_id is provided, can list owned or client accounts."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "business_id": {"type": "string", "description": "Optional Meta business ID for business-scoped account listing."},
                "relationship": {
                    "type": "string",
                    "enum": ["me", "owned", "client", "all"],
                    "description": "Source of accounts. Defaults to me when business_id is omitted, otherwise owned.",
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional account fields to request. Keep this narrow for faster responses.",
                },
                "limit": {"type": "integer", "minimum": 1, "maximum": 200, "description": "Rows per page. Default 25."},
                "max_pages": {"type": "integer", "minimum": 1, "maximum": 10, "description": "Maximum pages to fetch. Default 1."},
            },
        },
    },
    {
        "name": "list_campaigns",
        "description": (
            "List campaigns under an ad account. Use for inventory browsing before drilling into performance. "
            "Supports effective_status filters and pagination limits."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "ad_account_id": {"type": "string", "description": "Ad account ID, with or without the act_ prefix. Defaults to META_DEFAULT_AD_ACCOUNT_ID."},
                "effective_status": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional effective_status filters such as ACTIVE, PAUSED, WITH_ISSUES.",
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional campaign fields. Defaults to name/status/objective/budget/timestamps.",
                },
                "limit": {"type": "integer", "minimum": 1, "maximum": 200, "description": "Rows per page. Default 25."},
                "max_pages": {"type": "integer", "minimum": 1, "maximum": 10, "description": "Maximum pages to fetch. Default 1."},
            },
        },
    },
    {
        "name": "list_ad_sets",
        "description": (
            "List ad sets either under an ad account or a specific campaign. Prefer campaign_id for a narrower result set."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "ad_account_id": {"type": "string", "description": "Ad account ID, with or without act_. Optional when campaign_id is provided."},
                "campaign_id": {"type": "string", "description": "Optional campaign ID to scope the query."},
                "effective_status": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional effective_status filters such as ACTIVE or PAUSED.",
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional ad set fields. Defaults to delivery, budget, targeting, and timing fields.",
                },
                "limit": {"type": "integer", "minimum": 1, "maximum": 200, "description": "Rows per page. Default 25."},
                "max_pages": {"type": "integer", "minimum": 1, "maximum": 10, "description": "Maximum pages to fetch. Default 1."},
            },
        },
    },
    {
        "name": "list_ads",
        "description": (
            "List ads under an ad account, campaign, or ad set. Use include_creative_fields only when the user needs creative metadata."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "ad_account_id": {"type": "string", "description": "Ad account ID, with or without act_. Optional when campaign_id or adset_id is provided."},
                "campaign_id": {"type": "string", "description": "Optional campaign ID to scope the query."},
                "adset_id": {"type": "string", "description": "Optional ad set ID to scope the query."},
                "effective_status": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional effective_status filters such as ACTIVE, PAUSED, WITH_ISSUES.",
                },
                "include_creative_fields": {
                    "type": "boolean",
                    "description": "When true, request creative and tracking-related fields in addition to core delivery fields.",
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional ad fields. If omitted, uses a compact default set.",
                },
                "limit": {"type": "integer", "minimum": 1, "maximum": 200, "description": "Rows per page. Default 25."},
                "max_pages": {"type": "integer", "minimum": 1, "maximum": 10, "description": "Maximum pages to fetch. Default 1."},
            },
        },
    },
    {
        "name": "get_object",
        "description": (
            "Fetch a single ad account, campaign, ad set, ad, ad creative, or async report run by ID. "
            "Use this for exact details after list results identify the right object."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "object_id": {"type": "string", "description": "The exact Meta object ID or act_<id> ad account ID."},
                "object_type": {
                    "type": "string",
                    "enum": ["ad_account", "campaign", "adset", "ad", "adcreative", "report_run"],
                    "description": "Used to choose safe default fields.",
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional explicit fields. If omitted, uses an object-type preset.",
                },
            },
            "required": ["object_id", "object_type"],
        },
    },
    {
        "name": "get_insights",
        "description": (
            "Run a Meta Marketing API insights query for an ad account, campaign, ad set, or ad. "
            "Use preset_fields for common reporting and set use_async=true for wide or breakdown-heavy reports."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "object_id": {
                    "type": "string",
                    "description": "act_<id> for account-level reports or the exact campaign/adset/ad ID for narrower reports. Defaults to META_DEFAULT_AD_ACCOUNT_ID.",
                },
                "level": {
                    "type": "string",
                    "enum": ["account", "campaign", "adset", "ad"],
                    "description": "Required when object_id is an ad account and optional otherwise.",
                },
                "preset_fields": {
                    "type": "string",
                    "enum": ["delivery", "performance", "video"],
                    "description": "Safe field preset for common analysis. Ignored when fields is provided.",
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Explicit insights fields. Prefer this only when you know exactly which metrics you need.",
                },
                "date_preset": {
                    "type": "string",
                    "description": "Meta date preset such as today, yesterday, last_7d, last_30d, this_month, maximum.",
                },
                "time_range": {
                    "type": "object",
                    "properties": {
                        "since": {"type": "string", "description": "Start date in YYYY-MM-DD."},
                        "until": {"type": "string", "description": "End date in YYYY-MM-DD."},
                    },
                    "description": "Explicit time window. Use instead of date_preset when exact dates matter.",
                },
                "time_increment": {
                    "oneOf": [{"type": "string"}, {"type": "integer"}],
                    "description": "daily, monthly, all_days, or a numeric day bucket. Daily is useful for trend analysis.",
                },
                "breakdowns": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional breakdowns such as age, gender, country, platform_position, publisher_platform.",
                },
                "action_breakdowns": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional action breakdowns when working with nested action metrics.",
                },
                "action_attribution_windows": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional attribution windows such as 1d_click, 7d_click, 1d_view.",
                },
                "filtering": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Optional Meta filtering clauses as documented by the Marketing API.",
                },
                "sort": {"type": "array", "items": {"type": "string"}, "description": "Optional sort order such as spend_descending."},
                "limit": {"type": "integer", "minimum": 1, "maximum": 500, "description": "Rows per page. Default 25."},
                "max_pages": {"type": "integer", "minimum": 1, "maximum": 10, "description": "Maximum pages to fetch for sync reports. Default 1."},
                "use_async": {"type": "boolean", "description": "Use Meta async report runs. Recommended for large date ranges or many breakdowns."},
            },
        },
    },
    {
        "name": "get_async_report_status",
        "description": (
            "Check an async insights report run and optionally fetch rows once it reaches Job Completed. "
            "Use after get_insights returns report_run_id."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "report_run_id": {"type": "string", "description": "The report_run_id returned by get_insights with use_async=true."},
                "include_results": {"type": "boolean", "description": "When true and the report is complete, also fetch insight rows."},
                "limit": {"type": "integer", "minimum": 1, "maximum": 500, "description": "Rows per page for fetched results. Default 25."},
                "max_pages": {"type": "integer", "minimum": 1, "maximum": 10, "description": "Maximum result pages to fetch. Default 1."},
            },
            "required": ["report_run_id"],
        },
    },
]


def _paginate(path: str, params: dict[str, Any], limit: int | None, max_pages: int | None) -> dict[str, Any]:
    request_params = dict(params)
    if limit:
        request_params["limit"] = limit
    remaining_pages = max_pages or DEFAULT_MAX_PAGES
    page_count = 0
    items: list[Any] = []
    last_paging: dict[str, Any] | None = None
    response = CLIENT.request("GET", path, request_params)

    while True:
        page_count += 1
        items.extend(response.get("data", []))
        last_paging = response.get("paging")
        next_url = (last_paging or {}).get("next")
        if not next_url or page_count >= remaining_pages:
            break
        sanitized_next = _sanitize_url(next_url)
        parsed = urllib.parse.urlsplit(next_url)
        response = CLIENT.request("GET", parsed.path.replace(f"/{CLIENT.api_version}/", "", 1), dict(urllib.parse.parse_qsl(parsed.query)))
        if sanitized_next:
            response.setdefault("paging", {})["next"] = sanitized_next

    return {
        "data": items,
        "paging": last_paging,
        "page_count": page_count,
        "returned_rows": len(items),
    }


def _list_ad_accounts(arguments: dict[str, Any]) -> dict[str, Any]:
    fields = _pick_fields(
        arguments.get("fields"),
        None,
        OBJECT_FIELD_PRESETS["ad_account"],
    )
    relationship = (arguments.get("relationship") or ("owned" if arguments.get("business_id") else "me")).strip()
    limit = int(arguments.get("limit") or DEFAULT_PAGE_LIMIT)
    max_pages = int(arguments.get("max_pages") or DEFAULT_MAX_PAGES)
    business_id = arguments.get("business_id")

    if not business_id:
        results = _paginate(
            "me/adaccounts",
            {"fields": ",".join(fields)},
            limit,
            max_pages,
        )
        results["source"] = "me/adaccounts"
        return results

    if relationship not in {"owned", "client", "all", "me"}:
        raise ValueError("relationship must be one of me, owned, client, all")

    sources: list[tuple[str, str]] = []
    if relationship in {"owned", "all"}:
        sources.append(("owned", f"{business_id}/owned_ad_accounts"))
    if relationship in {"client", "all"}:
        sources.append(("client", f"{business_id}/client_ad_accounts"))
    if relationship == "me":
        sources.append(("me", "me/adaccounts"))

    combined: list[dict[str, Any]] = []
    paging: dict[str, Any] = {}
    for source_name, path in sources:
        page = _paginate(path, {"fields": ",".join(fields)}, limit, max_pages)
        for row in page["data"]:
            if isinstance(row, dict):
                row.setdefault("_source", source_name)
                combined.append(row)
        paging[source_name] = page.get("paging")

    return {
        "source": relationship,
        "business_id": business_id,
        "returned_rows": len(combined),
        "data": combined,
        "paging": paging,
    }


def _list_campaigns(arguments: dict[str, Any]) -> dict[str, Any]:
    ad_account_id = _coerce_account_id(arguments.get("ad_account_id") or CLIENT.default_ad_account_id)
    fields = _pick_fields(
        arguments.get("fields"),
        None,
        OBJECT_FIELD_PRESETS["campaign"],
    )
    params: dict[str, Any] = {"fields": ",".join(fields)}
    effective_status = _coerce_list(arguments.get("effective_status"))
    if effective_status:
        params["effective_status"] = effective_status
    limit = int(arguments.get("limit") or DEFAULT_PAGE_LIMIT)
    max_pages = int(arguments.get("max_pages") or DEFAULT_MAX_PAGES)
    results = _paginate(f"{ad_account_id}/campaigns", params, limit, max_pages)
    results["ad_account_id"] = ad_account_id
    return results


def _list_ad_sets(arguments: dict[str, Any]) -> dict[str, Any]:
    fields = _pick_fields(
        arguments.get("fields"),
        None,
        OBJECT_FIELD_PRESETS["adset"],
    )
    params: dict[str, Any] = {"fields": ",".join(fields)}
    effective_status = _coerce_list(arguments.get("effective_status"))
    if effective_status:
        params["effective_status"] = effective_status
    limit = int(arguments.get("limit") or DEFAULT_PAGE_LIMIT)
    max_pages = int(arguments.get("max_pages") or DEFAULT_MAX_PAGES)

    if arguments.get("campaign_id"):
        path = f"{arguments['campaign_id']}/adsets"
    else:
        ad_account_id = _coerce_account_id(arguments.get("ad_account_id") or CLIENT.default_ad_account_id)
        path = f"{ad_account_id}/adsets"
    results = _paginate(path, params, limit, max_pages)
    results["scope"] = path
    return results


def _list_ads(arguments: dict[str, Any]) -> dict[str, Any]:
    base_fields = OBJECT_FIELD_PRESETS["ad"]
    creative_fields = base_fields + ["ad_review_feedback", "issues_info", "recommendations"]
    fields = _pick_fields(
        arguments.get("fields"),
        None,
        creative_fields if arguments.get("include_creative_fields") else base_fields,
    )
    params: dict[str, Any] = {"fields": ",".join(fields)}
    effective_status = _coerce_list(arguments.get("effective_status"))
    if effective_status:
        params["effective_status"] = effective_status
    limit = int(arguments.get("limit") or DEFAULT_PAGE_LIMIT)
    max_pages = int(arguments.get("max_pages") or DEFAULT_MAX_PAGES)

    if arguments.get("adset_id"):
        path = f"{arguments['adset_id']}/ads"
    elif arguments.get("campaign_id"):
        path = f"{arguments['campaign_id']}/ads"
    else:
        ad_account_id = _coerce_account_id(arguments.get("ad_account_id") or CLIENT.default_ad_account_id)
        path = f"{ad_account_id}/ads"
    results = _paginate(path, params, limit, max_pages)
    results["scope"] = path
    return results


def _get_object(arguments: dict[str, Any]) -> dict[str, Any]:
    object_type = arguments["object_type"]
    object_id = arguments["object_id"]
    if object_type == "ad_account":
        object_id = _coerce_account_id(object_id)
    fields = _pick_fields(arguments.get("fields"), object_type, OBJECT_FIELD_PRESETS[object_type])
    response = CLIENT.request("GET", object_id, {"fields": ",".join(fields)})
    return {
        "object_type": object_type,
        "object_id": object_id,
        "data": response,
    }


def _get_insights(arguments: dict[str, Any]) -> dict[str, Any]:
    object_id = arguments.get("object_id") or CLIENT.default_ad_account_id
    if not object_id:
        raise ValueError("object_id is required unless META_DEFAULT_AD_ACCOUNT_ID is configured")
    if str(object_id).isdigit():
        object_id = f"act_{object_id}"
    is_account_scope = str(object_id).startswith("act_")
    if is_account_scope:
        object_id = _coerce_account_id(object_id)

    fields = _pick_fields(arguments.get("fields"), arguments.get("preset_fields") or "performance", INSIGHTS_FIELD_PRESETS["performance"])
    params: dict[str, Any] = {"fields": ",".join(fields)}

    if arguments.get("level"):
        params["level"] = arguments["level"]
    elif is_account_scope:
        # Campaign-level rows are the most useful default when the user starts from an ad account.
        params["level"] = "campaign"
    if arguments.get("time_range"):
        params["time_range"] = arguments["time_range"]
    elif arguments.get("date_preset"):
        params["date_preset"] = arguments["date_preset"]
    if arguments.get("time_increment") is not None:
        params["time_increment"] = arguments["time_increment"]
    if arguments.get("breakdowns"):
        params["breakdowns"] = _coerce_list(arguments.get("breakdowns"))
    if arguments.get("action_breakdowns"):
        params["action_breakdowns"] = _coerce_list(arguments.get("action_breakdowns"))
    if arguments.get("action_attribution_windows"):
        params["action_attribution_windows"] = _coerce_list(arguments.get("action_attribution_windows"))
    if arguments.get("filtering"):
        params["filtering"] = arguments["filtering"]
    if arguments.get("sort"):
        params["sort"] = _coerce_list(arguments.get("sort"))

    limit = int(arguments.get("limit") or DEFAULT_PAGE_LIMIT)
    max_pages = int(arguments.get("max_pages") or DEFAULT_MAX_PAGES)
    path = f"{object_id}/insights"

    if arguments.get("use_async"):
        async_response = CLIENT.request("POST", path, {**params, "limit": limit, "async": True})
        return {
            "object_id": object_id,
            "request": {
                "path": path,
                "params": {key: value for key, value in params.items()},
                "mode": "async",
            },
            "report_run_id": async_response.get("report_run_id") or async_response.get("id"),
            "data": async_response,
        }

    results = _paginate(path, params, limit, max_pages)
    return {
        "object_id": object_id,
        "request": {
            "path": path,
            "params": {key: value for key, value in params.items()},
            "mode": "sync",
        },
        **results,
    }


def _get_async_report_status(arguments: dict[str, Any]) -> dict[str, Any]:
    report_run_id = arguments["report_run_id"]
    limit = int(arguments.get("limit") or DEFAULT_PAGE_LIMIT)
    max_pages = int(arguments.get("max_pages") or DEFAULT_MAX_PAGES)
    report = CLIENT.request("GET", report_run_id, {"fields": ",".join(OBJECT_FIELD_PRESETS["report_run"])})
    result: dict[str, Any] = {"report": report}
    status = str(report.get("async_status", "")).lower()
    is_complete = "complete" in status
    if arguments.get("include_results") and is_complete:
        result["results"] = _paginate(f"{report_run_id}/insights", {}, limit, max_pages)
    elif arguments.get("include_results"):
        result["note"] = "Report is not complete yet. Poll again when async_status indicates completion."
    return result


TOOL_HANDLERS = {
    "list_ad_accounts": _list_ad_accounts,
    "list_campaigns": _list_campaigns,
    "list_ad_sets": _list_ad_sets,
    "list_ads": _list_ads,
    "get_object": _get_object,
    "get_insights": _get_insights,
    "get_async_report_status": _get_async_report_status,
}


def _handle_tool_call(arguments: dict[str, Any]) -> dict[str, Any]:
    tool_name = arguments.get("name")
    tool_arguments = arguments.get("arguments") or {}
    if tool_name not in TOOL_HANDLERS:
        return _format_tool_result({"error": f"Unknown tool: {tool_name}"}, is_error=True)
    try:
        payload = TOOL_HANDLERS[tool_name](tool_arguments)
        return _format_tool_result(payload)
    except Exception as exc:  # pragma: no cover - defensive error formatting
        safe_message = str(exc)
        try:
            parsed = json.loads(safe_message)
            safe_message = parsed.get("message", safe_message)
        except json.JSONDecodeError:
            pass
        return _format_tool_result(
            {
                "error": safe_message,
                "tool": tool_name,
                "hint": "Check your ad account ID, token scopes, and time window. Use list_ad_accounts first if the account ID is unknown.",
            },
            is_error=True,
        )


def _handle_request(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    message_id = message.get("id")
    params = message.get("params") or {}

    if method == "initialize":
        protocol_version = params.get("protocolVersion") or "2025-03-26"
        return _response(
            message_id,
            {
                "protocolVersion": protocol_version,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        )

    if method == "notifications/initialized":
        return None

    if method == "ping":
        return _response(message_id, {})

    if method == "tools/list":
        return _response(message_id, {"tools": TOOLS})

    if method == "tools/call":
        return _response(message_id, _handle_tool_call(params))

    if method == "resources/list":
        return _response(message_id, {"resources": []})

    if method == "prompts/list":
        return _response(message_id, {"prompts": []})

    if message_id is None:
        return None
    return _error(message_id, -32601, f"Method not found: {method}")


def main() -> int:
    while True:
        try:
            message = _read_message()
            if message is None:
                return 0
            response = _handle_request(message)
            if response is not None:
                _write_message(response)
        except Exception as exc:  # pragma: no cover - stdio server safeguard
            message_id = None
            try:
                message_id = locals().get("message", {}).get("id")
            except Exception:
                message_id = None
            error_response = _error(
                message_id,
                -32603,
                f"Internal server error: {exc}",
                {"traceback": traceback.format_exc(limit=3)},
            )
            _write_message(error_response)


if __name__ == "__main__":
    raise SystemExit(main())
