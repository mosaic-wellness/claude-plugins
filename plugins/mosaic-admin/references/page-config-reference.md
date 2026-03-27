# Page Config Reference

Covers page types beyond PDPs and widget/landing pages — category, sub-category, growth, shop, fest, and ingredients pages.

---

## Overview

Mosaic Wellness serves several page types from S3 JSON configs through middleware. While PDPs and widget pages have dedicated admin-mcp tools, other page types share similar patterns but are managed through different middleware endpoints and S3 paths.

---

## Page Types and Middleware Endpoints

| Page Type | Middleware Endpoint | Path Param | Cache | S3 Bucket |
|---|---|---|---|---|
| Category | `GET /category/:categoryName` | `categoryName` | 600s (10 min) | `pagedata` |
| Sub-Category | `GET /sub-category/:subCategoryName` | `subCategoryName` | 600s | `pagedata` |
| Landing Page | `GET /landing-page/:categoryName` | `categoryName` | 600s | `pagedata` |
| Ingredients | `GET /ingredients/:categoryName` | `categoryName` | 600s | `pagedata` |
| Fest/Event | `GET /fest/:festName` | `festName` | 600s | `pagedata` |
| Shop (v1) | `GET /shop-page` | — | 600s | `pagedata` |
| Shop (v2) | `GET /v2/shop-page` | — | — | `pagedata` |
| Shop (v3) | `POST /v3/shop-page` | — | — | `pagedata` |
| Growth Home | `GET /growth/home?version=v2` | — | — | `pagedata` |
| Widget Landing | `GET /widget-landing-page/:categoryName` | `categoryName` | — | `pagedata` |

### CDN-Cached Variants

Most page types have a `/mwsc/` prefixed variant for CDN caching:
- `/mwsc/category/:categoryName` (10 min cache)
- `/mwsc/sub-category/:subCategoryName` (10 min cache)
- `/mwsc/ingredients/:categoryName` (10 min cache)
- `/mwsc/landing-page/:categoryName` (10 min cache)
- `/mwsc/fest/:festName` (10 min cache)
- `/mwsc/shop-page` (10 min cache)

---

## S3 Storage Paths

All page configs are stored in the **pagedata** S3 bucket for each brand.

| Page Type | S3 Key Pattern | Example |
|---|---|---|
| Category | `categories/{categoryName}.json` | `categories/hair.json` |
| Sub-Category | `sub-categories/{subCategoryName}.json` | `sub-categories/hair-growth.json` |
| Landing Page | `landing-pages/{categoryName}.json` | `landing-pages/monsoon-sale.json` |
| Growth | `growth/{identifier}.json` | `growth/home.json` |
| Fest/Event | `fest/{festName}.json` | `fest/diwali-sale.json` |
| Shop | `shop-page.json` or `v2/shop-page.json` | — |
| Ingredients | `ingredients/{categoryName}.json` | `ingredients/biotin.json` |

**Bucket naming:**
- Staging: `{brand}-pagedata-staging` (exception: `mm` uses `manmatters-stage-json`)
- Production: `{brand}-pagedata-prod`

---

## Data Shape

Page configs follow a widget-based structure similar to widget pages:

```json
{
  "pageTitle": "Hair Care",
  "pageDescription": "...",
  "widgets": [
    {
      "widgetType": "BANNER",
      "widgetData": {
        "title": "...",
        "items": [...]
      }
    },
    {
      "widgetType": "PRODUCT_GRID",
      "widgetData": {
        "title": "...",
        "products": [...]
      }
    }
  ],
  "seo": {
    "title": "...",
    "description": "...",
    "canonical": "..."
  }
}
```

### Key Differences from Widget Pages

| Feature | Widget Pages | Page Configs |
|---|---|---|
| Admin-MCP tools | Full CRUD (`get_widget_page_config`, etc.) | **No dedicated tools yet** |
| S3 path | `widget_pages/{identifier}.json` | Varies by type (see table above) |
| Repeat user variant | `{identifier}-repeat.json` | Not all types support repeat variants |
| Display order | 3-tier override system | Simple widget array ordering |
| Experiment support | Via `experiment.json` (`landing` type) | Category and home have experiment support |

---

## Experiment Support

The `experiment.json` file supports experiments for these page types:

| Experiment Type | Page Config Type | Identifier Format |
|---|---|---|
| `product` | PDP | `{urlKey}.json` |
| `landing` | Widget/Landing pages | `{identifier}` |
| `category` | Category pages | `{categoryName}` |
| `home` | Home page | `home` |

Use the existing experiment tools (`get_experiment_assignment_config`, `update_experiment_assignment`) with the appropriate `type` parameter.

---

## How to Manage Page Configs Today

### Reading Configs

Since page configs live in the same `pagedata` S3 bucket, the **widget page tools can often read them**:

```
get_widget_page_config(identifier: "categories/hair", brand: "mm")
```

However, the identifier format differs — page configs use path prefixes (`categories/`, `sub-categories/`, etc.) while widget pages use flat identifiers (`home`, `summer-sale`).

### Editing Configs

For editing, try:
1. **Widget page tools** — `update_widget_page_section` with the full S3 key as identifier
2. **Zeus admin dashboard** — Direct editing at `https://stg-zeus.mosaicwellness.in`
3. **Direct S3 access** — Via AWS console or CLI (requires appropriate IAM permissions)

### Creating New Pages

1. Clone an existing page config via Zeus admin dashboard
2. Or use `create_widget_page` with the appropriate identifier format

---

## Frontend URL Mapping

| Frontend URL Pattern | Page Type | Storefront Route |
|---|---|---|
| `/shop` or `/shop/*` | Shop | `apps/storefront-web` shop pages |
| `/category/{name}` | Category | SSR with middleware fetch |
| `/sub-category/{name}` | Sub-Category | SSR with middleware fetch |
| `/growth` | Growth | SSR with middleware fetch |
| `/fest/{name}` | Fest/Event | SSR with middleware fetch |
| `/ingredients/{name}` | Ingredients | SSR with middleware fetch |

---

## Known Gaps (Future MCP Tool Candidates)

The following capabilities are NOT yet available in admin-mcp and would need new tools:

1. **`list_page_configs`** — List all page configs by type (category, sub-category, etc.)
2. **`get_page_config`** — Fetch a page config with type-aware S3 path resolution
3. **`update_page_config`** — Update a page config with type-aware S3 path resolution
4. **`create_page_config`** — Clone/create a page config for a specific type
5. **`diff_page_config_versions`** — Compare staging vs production for page configs
6. **`preview_page_config_url`** — Generate preview URLs for page config types

These would wrap the same Zeus API (`getPage`/`updatePage`) but with type-aware path resolution.
