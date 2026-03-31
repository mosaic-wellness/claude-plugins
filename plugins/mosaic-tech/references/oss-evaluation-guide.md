# Open Source Evaluation Guide

Reference guide for evaluating open-source tools before recommending them to the team.

## Quick Health Check

Before recommending any open-source tool, verify these minimum thresholds:

| Signal | Green | Yellow | Red |
|---|---|---|---|
| GitHub stars | >1,000 | 200-1,000 | <200 |
| Last commit | <1 month | 1-6 months | >6 months |
| Contributors | >10 | 3-10 | 1-2 |
| Open issues ratio | <30% of total | 30-50% | >50% |
| Documentation | Dedicated docs site | Good README | Sparse/none |
| License | MIT, Apache 2.0, BSD | LGPL, MPL | AGPL, GPL, proprietary |
| Release cadence | Regular (monthly+) | Quarterly | No releases / sporadic |
| Test coverage | CI passing, tests exist | Some tests | No tests |

## License Guide (Plain Language)

| License | Can use commercially? | Must share changes? | Can keep code private? | Watch out for |
|---|---|---|---|---|
| **MIT** | Yes | No | Yes | Nothing — most permissive |
| **Apache 2.0** | Yes | No | Yes | Must include license notice |
| **BSD** | Yes | No | Yes | Similar to MIT |
| **MPL 2.0** | Yes | Only modified files | Mostly yes | Modified files must be shared |
| **LGPL** | Yes | Only if you modify the library | Yes (your code) | Dynamic linking is fine |
| **GPL** | Yes | Yes — all linked code | No | Viral — your whole app becomes GPL |
| **AGPL** | Yes | Yes — even for network use | No | Most restrictive — network use triggers sharing |
| **Proprietary** | Check terms | N/A | N/A | May have usage limits, fees |

**Rule of thumb for Mosaic Wellness:** Prefer MIT/Apache/BSD. Flag AGPL/GPL for review. Never use proprietary without legal approval.

## Security Red Flags

Immediately flag and avoid if you see:

- **No HTTPS on docs/website** — basic security not maintained
- **Hardcoded credentials in source** — poor security practices
- **No input validation** — injection risks
- **Eval/exec usage on user input** — code execution vulnerability
- **Outdated dependencies with known CVEs** — `npm audit` or `pip audit` shows critical issues
- **No authentication mechanism** — if the tool handles data, it needs auth
- **Single maintainer + no activity** — bus factor of 1, likely abandoned
- **Forked from archived repo** — upstream is dead, fork may follow

## Evaluation Template

When evaluating a tool for recommendation, fill out this mental checklist:

```
Tool: [name]
URL: [github/website]
Stars: [count] | Last commit: [date] | Contributors: [count]
License: [type]

Fit Assessment:
- Does it solve the core problem? [yes/partially/no]
- What percentage of the use case does it cover? [X%]
- What's missing that we'd need to build? [list]

Maturity Assessment:
- Is there a stable release? [yes/no]
- Is documentation adequate for non-technical setup? [yes/no]
- Is there an active community (Discord, forums, issues)? [yes/no]

Security Assessment:
- License compatible with commercial use? [yes/no]
- Any known CVEs? [yes/no]
- Does it handle data securely? [yes/no/not applicable]
- Authentication/authorization built in? [yes/no/not applicable]

Deployment Assessment:
- How is it deployed? [Docker/npm/pip/SaaS/manual]
- Self-hosted option available? [yes/no]
- What infrastructure does it need? [list]
- Estimated time to working prototype? [hours/days/weeks]
```

## Common D2C Use Cases and Where to Look

| Use Case | Search Terms | Notable Tools to Check |
|---|---|---|
| Customer support chatbot | "open source chatbot", "customer support AI" | Chatwoot, Typebot, Botpress |
| Document/SOP Q&A (RAG) | "open source RAG", "document QA" | AnythingLLM, Danswer/Onyx, PrivateGPT |
| Sentiment analysis | "review analysis", "sentiment open source" | Claude API (direct), MonkeyLearn |
| Content generation | "AI content tool", "copywriting AI" | Claude API (direct), various wrappers |
| Internal dashboard + AI | "open source admin panel AI" | Retool, Appsmith, Tooljet (+ Claude API) |
| WhatsApp/messaging bot | "whatsapp bot open source" | Chatwoot, Baileys, evolution-api |
| Image generation/editing | "product image AI" | Stability API, Replicate |
| Search/recommendation | "open source search AI" | Typesense, Meilisearch, Qdrant |
| Workflow automation | "open source automation" | n8n, Activepieces, Windmill |
| Form/survey with AI | "open source form builder" | Formbricks, Typebot |

**Note:** This table is a starting point. Always search for current alternatives — the AI tools landscape changes rapidly.
