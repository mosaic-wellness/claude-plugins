# URL Route Reference

Maps URLs to admin-mcp page types and tools.

---

## Section 1: URL Pattern Matching

| URL Pattern | Page Type | Admin-MCP Category | Identifier |
|---|---|---|---|
| `/` | Widgetized Home | Widget Page tools | `home` |
| `/wlanding/{identifier}` | Widgetized Landing Page | Widget Page tools | `{identifier}` from URL path |
| `/product/{urlKey}` | Widgetized PDP (+ experiment support) | PDP tools + Experiment tools | `{urlKey}.json` |
| `/dp/{urlKey}` | Widgetized PDP (flag-gated, no experiments) | PDP tools | `{urlKey}.json` |
| `/dp/{urlKey}/{productUrlKey}` | Widgetized PDP variant (flag-gated) | PDP tools | `{productUrlKey}.json` |
| `/{slug}` (catch-all) | Unknown — check both | Try Widget Page first, then PDP | `{slug}` or `{slug}.json` |
| `/category/{name}` | Category Page | Page Config tools | `categories/{name}` |
| `/sub-category/{name}` | Sub-Category Page | Page Config tools | `sub-categories/{name}` |
| `/growth/*` | Growth Page | Page Config tools | `growth/{name}` |
| `/fest/{name}` | Fest/Event Page | Page Config tools | `fest/{name}` |
| `/shop`, `/v2/shop-page` | Shop Page | Page Config tools | `shop-page` or `v2/shop-page` |
| `/ingredients/{name}` | Ingredients Page | Page Config tools | `ingredients/{name}` |
| `/account/*` | Account | **NOT supported** | — |
| `/consultation/*` | Consultation | **NOT supported** | — |
| `/forms/*` | Forms | **NOT supported** | — |
| `/checkout/*` | Checkout | **NOT supported** | — |

---

## Section 2: Hostname to Brand Code

| Hostname Pattern | Brand Code | Staging URL |
|---|---|---|
| `*.manmatters.com`, `stg.manmatters.com` | `mm` | `https://stg.manmatters.com` |
| `*.manmatters.in`, `stg.manmatters.in` | `mm-in` | `https://stg.manmatters.in` |
| `*.manmatters.ae`, `stg.manmatters.ae` | `mm-ae` | `https://stg.manmatters.ae` |
| `*.manmatters.co`, `stg.manmatters.co` | `mm-co` | `https://stg.manmatters.co` |
| `*.bebodywise.com`, `stg.bebodywise.com` | `bw` | `https://stg.bebodywise.com` |
| `*.bebodywise.ae`, `stg.bebodywise.ae` | `bw-ae` | `https://stg.bebodywise.ae` |
| `*.bebodywise.co`, `stg.bebodywise.co` | `bw-co` | `https://stg.bebodywise.co` |
| `*.bebodywise.us`, `stg.bebodywise.us` | `bw-us` | `https://stg.bebodywise.us` |
| `*.ourlittlejoys.com`, `stg.ourlittlejoys.com` | `lj` | `https://stg.ourlittlejoys.com` |
| `*.ourlittlejoys.ae`, `stg.ourlittlejoys.ae` | `lj-ae` | `https://stg.ourlittlejoys.ae` |
| `*.ourlittlejoys.co`, `stg.ourlittlejoys.co` | `lj-co` | `https://stg.ourlittlejoys.co` |
| `stg-sa.ourlittlejoys.com`, `sa.ourlittlejoys.com` | `lj-sa` | `https://stg-sa.ourlittlejoys.com` |
| `*.littlejoys.us`, `stg.littlejoys.us` | `lj-us` | `https://stg.littlejoys.us` |
| `*.rootlabs.in`, `stg.rootlabs.in` | `rl-in` | `https://stg.rootlabs.in` |
| `*.rootlabs.co`, `stg.rootlabs.co` | `rl-us` | `https://stg.rootlabs.co` |
| `*.onlywhatsneeded.in`, `stg.onlywhatsneeded.in` | `wn-in` | `https://stg.onlywhatsneeded.in` |
| `*.absolutescience.in`, `stg.absolutescience.in` | `as-in` | `https://stg.absolutescience.in` |

**Notes:**
- `lj-sa` uses a non-standard staging pattern: `stg-sa.ourlittlejoys.com` (not `stg.`)
- `lj-us` uses `littlejoys.us` domain (not `ourlittlejoys.us`)
- `rl-us` uses `rootlabs.co` domain
- `fw` brand has no preview URLs configured

---

## Section 3: Resolution Algorithm

Given a URL like `https://stg.manmatters.com/product/minoxidil-5-hair-growth`:

1. **Extract hostname:** `stg.manmatters.com`
2. **Match hostname to brand code:** `stg.manmatters.com` → `mm`
3. **Extract path:** `/product/minoxidil-5-hair-growth`
4. **Match path to pattern:** `/product/{urlKey}` → PDP type
5. **Derive identifier:** `urlKey` = `minoxidil-5-hair-growth` → `page_name` = `minoxidil-5-hair-growth.json`
6. **Select tool:** PDP type → use `get_pdp_config(page_name: "minoxidil-5-hair-growth.json", brand: "mm")`

### PDP route note (`/product/` vs `/dp/`):
Both routes render the same widgetized PDP when `NEXT_PUBLIC_ENABLE_NEW_PDP` is enabled. The difference:
- `/product/{urlKey}` — supports **experiment variants** (reads `expId` from cookies, passes to SSR)
- `/dp/{urlKey}` — widgetized but **no experiment support**

From admin-mcp's perspective, both use the same PDP tools (`get_pdp_config`, `update_pdp_section`, etc.). Use experiment tools (`get_experiment_config`, `create_pdp_experiment`) only when working with `/product/` URLs.

### Catch-all `/{slug}` resolution:
When the path doesn't match a known pattern (like `/some-landing-page`):

1. Try widget page first:
   ```
   get_widget_page_config(identifier: "some-landing-page", brand: "mm")
   ```
2. If 404, try PDP:
   ```
   get_pdp_config(page_name: "some-landing-page.json", brand: "mm")
   ```
3. If both fail, the page is not managed by admin-mcp.

### Production vs staging URLs:
- Staging URLs use `stg.` prefix (or `stg-sa.` for lj-sa)
- Production URLs use the bare domain (e.g., `manmatters.com`)
- Both resolve to the same brand code — the difference is which environment to target

---

## Section 4: Page Configs (Category, Sub-Category, Growth, Fest, Shop, Ingredients)

These page types live in the same `pagedata` S3 bucket as widget pages but use type-specific path prefixes. They can often be managed using widget page tools with the appropriate identifier.

| URL Pattern | Page Type | S3 Key | Try With Widget Tools |
|---|---|---|---|
| `/category/{name}` | Category | `categories/{name}` | `get_widget_page_config(identifier: "categories/{name}", brand)` |
| `/sub-category/{name}` | Sub-Category | `sub-categories/{name}` | `get_widget_page_config(identifier: "sub-categories/{name}", brand)` |
| `/growth/*` | Growth | `growth/{name}` | `get_widget_page_config(identifier: "growth/{name}", brand)` |
| `/fest/{name}` | Fest/Event | `fest/{name}` | `get_widget_page_config(identifier: "fest/{name}", brand)` |
| `/shop` | Shop | `shop-page` | `get_widget_page_config(identifier: "shop-page", brand)` |
| `/ingredients/{name}` | Ingredients | `ingredients/{name}` | `get_widget_page_config(identifier: "ingredients/{name}", brand)` |

See `${CLAUDE_PLUGIN_ROOT}/references/page-config-reference.md` for full details.

---

## Section 5: App Config (Mobile)

The Mosaic RN Mobile App fetches configuration from:

| Endpoint | Auth | Purpose |
|---|---|---|
| `/utility/app-config-merge?staticVersion=v2` | Yes | **Primary** — merged static + dynamic config |
| `/utility/app-config-static` | No | Raw base config from S3 |
| `/utility/app-config-dynamic` | Yes | User-specific dynamic config |
| `/utility/app-config` | Yes | Custom merged config |

**S3 key:** `app-config-merge` (or `app-config-v2`) in the `pagedata` bucket.

Try reading with: `get_widget_page_config(identifier: "app-config-merge", brand: "mm")`

See `${CLAUDE_PLUGIN_ROOT}/references/app-config-reference.md` for full details on config structure, feature flags, bottom tabs, and version gating.

---

## Section 6: Pages NOT Supported by Admin-MCP

These page types cannot be managed through admin-mcp or S3 JSON configs:

| Path Pattern | Why Not Supported |
|---|---|
| `/account/*` | Account pages are rendered by frontend components with API data, no S3 config |
| `/consultation/*` | Consultation flow is managed by health-service, not page configs |
| `/forms/*` | Forms are managed by the forms service |
| `/checkout/*` | Checkout flow is managed by middleware + OMS, not page configs |
| `/blog/*` | Blog content is managed separately |

If a user asks to update one of these pages, explain that admin-mcp manages **S3-backed JSON configurations** — pages driven by other services or databases require changes in the respective service repos.
