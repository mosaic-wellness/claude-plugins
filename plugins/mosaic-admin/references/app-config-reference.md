# App Config Reference

Mobile app configuration for the Mosaic RN App — feature flags, tab visibility, version gating, and dynamic UI configuration.

---

## Overview

The Mosaic React Native mobile app fetches a merged configuration at startup that controls feature flags, bottom tab visibility, version-gated behavior, and UI settings. The config is a combination of:

1. **Static config** — Base JSON stored in S3 (`pagedata` bucket)
2. **Dynamic config** — Per-user modifications applied by middleware at runtime (tabs, features, user type)

---

## API Endpoints

| Endpoint | Auth | Description |
|---|---|---|
| `GET /utility/app-config-static` | No | Raw static config from S3 (no user-specific modifications) |
| `GET /utility/app-config-dynamic` | Yes | Dynamic user-specific config |
| `GET /utility/app-config` | Yes | Custom merged config |
| `GET /utility/app-config-merge?staticVersion=v2` | Yes | **Primary endpoint** — merged static + dynamic config with user modifications |

The mobile app uses **`/utility/app-config-merge?staticVersion=v2`** as its primary config source.

---

## S3 Storage

- **Bucket:** `pagedata` bucket for each brand (e.g., `mm-pagedata-staging`, `manmatters-stage-json` for mm)
- **Key:** `app-config-merge.json` or `app-config-v2.json` (version-dependent)
- **Format:** JSON

---

## Config Structure

### Top-Level Shape

```json
{
  "bottomTabs": {
    "tabs": [
      {
        "id": "home",
        "label": "Home",
        "icon": "home-icon",
        "deepLink": "/",
        "visible": true,
        "order": 1
      },
      {
        "id": "shop",
        "label": "Shop",
        "icon": "shop-icon",
        "deepLink": "/shop",
        "visible": true,
        "order": 2
      }
    ],
    "newUserOverrides": { ... },
    "repeatUserOverrides": { ... }
  },
  "featureFlags": {
    "enableNewCheckout": true,
    "enableVideoConsult": false,
    "enableWalletPayment": true,
    "enableReferral": true,
    ...
  },
  "versionGating": {
    "minVersion": "3.0.0",
    "forceUpdateVersion": "2.5.0",
    "softUpdateVersion": "2.8.0",
    "updateMessage": "Please update for the best experience"
  },
  "deepLinks": {
    "home": "/",
    "shop": "/shop",
    "consultation": "/consultation",
    ...
  },
  "uiConfig": {
    "headerStyle": { ... },
    "brandColors": { ... },
    "fontConfig": { ... }
  },
  "growthConfig": {
    "homeWidgets": [ ... ],
    "referralConfig": { ... }
  }
}
```

### Bottom Tabs Configuration

The most commonly edited section. Controls which tabs appear in the mobile app navigation:

```json
{
  "bottomTabs": {
    "tabs": [
      { "id": "home", "label": "Home", "icon": "home", "deepLink": "/", "visible": true, "order": 1 },
      { "id": "shop", "label": "Shop", "icon": "shop", "deepLink": "/shop", "visible": true, "order": 2 },
      { "id": "consult", "label": "Consult", "icon": "consult", "deepLink": "/consultation", "visible": true, "order": 3 },
      { "id": "reorder", "label": "Reorder", "icon": "reorder", "deepLink": "/reorder", "visible": false, "order": 4 },
      { "id": "account", "label": "Account", "icon": "account", "deepLink": "/account", "visible": true, "order": 5 }
    ]
  }
}
```

**User-type overrides:** Middleware dynamically modifies tab visibility based on:
- **New users** — May hide "Reorder" tab, show "Consult" prominently
- **Repeat users** — May show "Reorder" tab, adjust tab order

### Feature Flags

Boolean flags that gate features across the app:

```json
{
  "featureFlags": {
    "enableNewCheckout": true,
    "enableVideoConsult": false,
    "enableWalletPayment": true,
    "enableReferral": true,
    "enableSubscription": true,
    "enableSelfAssessment": true,
    "enableQuickDelivery": false
  }
}
```

### Version Gating

Controls forced/soft updates:

```json
{
  "versionGating": {
    "minVersion": "3.0.0",
    "forceUpdateVersion": "2.5.0",
    "softUpdateVersion": "2.8.0",
    "updateMessage": "Please update the app for the best experience"
  }
}
```

- `forceUpdateVersion` — Users below this version MUST update (blocking screen)
- `softUpdateVersion` — Users below this version see a dismissible update prompt
- `minVersion` — Minimum supported version

---

## Middleware Modification Pipeline

The `/utility/app-config-merge` endpoint applies per-user modifications:

```
1. Fetch base config from S3 (pagedata bucket)
2. Identify user type (NEW vs REPEAT) from auth token + Redis
3. Apply bottom tab overrides based on user type
4. Apply feature flag overrides based on:
   - User cohort
   - App version
   - Brand-specific rules
5. Return merged config
```

**Key file:** `backend/middleware/api/helpers/utility/getModifiedAppConfig.ts`

---

## Mobile App Consumption

### Store (Zustand)

```typescript
// src/store/appConfig/useAppConfig.store.ts
const useAppConfigStore = create<AppConfigStore>(set => ({
  appConfig: null,
  isLoadingAppConfig: false,
  setAppConfig: (newAppConfig) => set({ appConfig: newAppConfig }),
}));
```

### Hook

```typescript
// src/contexts/appConfig/appConfig.hook.ts
export const useAppConfig = (): IAppConfig | null => {
  const staticConfig = useAppConfigStore(store => store.appConfig);
  return staticConfig;
};
```

### Fetch Constant

```typescript
// src/constants/api.ts
APP_CONFIG_STATIC: `${BASE_URL}utility/app-config-merge?staticVersion=v2`
```

---

## How to Manage App Configs Today

### Reading

The static base config can be fetched via:
1. **Widget page tools** — Try `get_widget_page_config(identifier: "app-config-merge", brand: "mm")`
2. **Direct API** — `GET https://stg.manmatters.com/proxy/utility/app-config-static`
3. **S3 console** — Browse the `pagedata` bucket directly

### Editing

1. **Zeus admin dashboard** — Direct editing at `https://stg-zeus.mosaicwellness.in`
2. **Widget page tools** — If the identifier resolves, use `update_widget_page_section` for targeted edits
3. **Direct S3** — Upload modified JSON (requires IAM permissions)

### Common Edit Scenarios

| Scenario | Section to Edit | Example |
|---|---|---|
| Show/hide a bottom tab | `bottomTabs.tabs[N].visible` | Set `reorder` tab `visible: true` for repeat users |
| Toggle a feature flag | `featureFlags.{flagName}` | Set `enableNewCheckout: false` to disable |
| Force app update | `versionGating.forceUpdateVersion` | Set to `3.1.0` to force update below that |
| Change tab order | `bottomTabs.tabs[N].order` | Reorder tabs by changing `order` values |
| Add a new deep link | `deepLinks.{name}` | Add new route for a campaign page |

---

## Brand-Specific Behavior

Each brand has its own app config in its `pagedata` bucket. Common differences:

| Brand | Notable Differences |
|---|---|
| `mm` (Man Matters) | Full feature set, all tabs enabled |
| `bw` (Bodywise) | Different tab configuration, brand-specific features |
| `lj` (Little Joys) | Simplified tab set, kid-focused features |
| International (`mm-ae`, `bw-ae`, etc.) | Region-specific features disabled (e.g., COD, quick delivery) |

---

## Known Gaps (Future MCP Tool Candidates)

The following capabilities are NOT yet available in admin-mcp:

1. **`get_app_config`** — Fetch the current app config for a brand (static base)
2. **`update_app_config`** — Update app config sections (feature flags, tabs, version gating)
3. **`diff_app_config_versions`** — Compare staging vs production app configs
4. **`preview_app_config`** — View the effective config for a specific user type/version

These would enable direct management of mobile app behavior through admin-mcp without needing Zeus dashboard access.

---

## Caching and Propagation

- **CDN cache:** App config is NOT CDN-cached (dynamic per request)
- **Redis cache:** User type data cached in Redis
- **App-side cache:** Config stored in Zustand store, refreshed on app launch
- **Propagation time:** Changes to S3 base config are reflected immediately on next app launch (no CDN delay)
