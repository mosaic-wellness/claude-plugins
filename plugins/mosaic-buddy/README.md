# mosaic-buddy

Your project's technical co-pilot.

Built for product managers, ops people, revenue analysts, and growth teams at Mosaic Wellness who build internal tools with Claude Code. Mosaic Buddy catches what breaks in production, helps you plan features, and makes sure your work is ready before anyone else sees it.

## Installation

```bash
# From the Mosaic marketplace
/plugin install mosaic-buddy

# Or link locally for development
git clone git@github.com:mosaic-wellness/claude-plugins.git
cd claude-plugins/plugins/mosaic-buddy
claude plugin link .
```

## Commands

Just run `/mosaic-buddy` to see the interactive menu — or jump straight to what you need:

| What you want to do | Command |
|---------------------|---------|
| Is this ready to share? | `/mosaic-buddy doctor` |
| Are my tech choices solid? | `/mosaic-buddy review-stack` |
| How does this hold up? | `/mosaic-buddy review` |
| Would a user actually like this? | `/mosaic-buddy ux` |
| I have an idea | `/mosaic-buddy brainstorm` |
| Give it to me straight | `/mosaic-buddy grillme` |
| Write it down for me | `/mosaic-buddy document [prd\|spec\|adr\|update\|refresh]` |
| Something's broken | `/mosaic-buddy debug` |
| Get more out of Claude | `/mosaic-buddy 10x` |
| What plugins should I use? | `/mosaic-buddy recommendations` |

## What's Inside

### 9 Agents

| Agent | What it does | Model |
|-------|-------------|-------|
| doctor | Find what breaks before someone else does — 80+ checks across reliability, safety, code quality, and UX | Sonnet |
| stack-reviewer | Quick red flag scan — wrong database, missing auth, deprecated models, exposed keys | Sonnet |
| reviewer | Architecture review that asks about your intent before judging | Sonnet |
| ux-reviewer | UX audit from your users' perspective, with time estimates | Sonnet |
| brainstormer | Turn a rough idea into a clear 1-page spec through conversation | Sonnet |
| grillme | Honest product + code review — starts with what's good, then what your VP would notice | Sonnet |
| documenter | Create PRDs, tech specs, and decision records — updates and refreshes them too | Sonnet |
| debugger | Structured debugging — classify, hypothesize, investigate, fix, document | Sonnet |
| coach | Coaching report that finds your superpowers and time sinks with Claude Code | Opus |

### 4 Skills (auto-loaded knowledge)

| Skill | When it loads |
|-------|--------------|
| conventions | Every command — approved stack, project structure, security, deployment, tone |
| ai-app-conventions | When AI SDK is detected — model selection, cost management, safety |
| ux-heuristics | During UX reviews — Nielsen's 10 for internal tools, data table patterns |
| doc-templates | During document commands — PRD, tech spec, ADR templates with mermaid |

### 2 Safety Hooks

- **On file write/edit:** Blocks if you're about to commit a hardcoded API key
- **On bash output:** Warns if a command leaked a key in its output

## Approved Stack

Mosaic Buddy enforces these choices across all commands:

| Layer | Choice | What's blocked |
|-------|--------|---------------|
| Backend | Fastify (Node 20 LTS) | Express, Hono, Nest.js |
| Frontend | React + Vite | Next.js (unless SSR justified), Vue, Angular |
| Database | MySQL + Prisma | SQLite, PostgreSQL, MongoDB |
| Auth | Google OAuth | Custom JWT as sole auth, passport-local |
| Deployment | EC2 | Vercel, Lambda, Docker |
| AI SDK | @anthropic-ai/sdk | LangChain, OpenAI, frontend API calls |

## Telemetry

Mosaic Buddy collects lightweight, anonymous usage data to help the team understand which commands are popular and track adoption.

**What is sent (exhaustive list):**

| Field | Source | Example |
|-------|--------|---------|
| command | First word only, sanitized | `doctor` |
| user_email | `git config user.email` | `you@mosaic.com` |
| project_name | Git repo folder name | `expense-tracker` |
| timestamp | UTC time of invocation | `2026-04-21T10:30:00Z` |

**What is NOT sent:** file contents, command arguments beyond the subcommand name, environment variables, API keys, source code, or file paths.

**Opt out:** Add this to your shell profile (`.zshrc` / `.bashrc`):

```bash
export MOSAIC_BUDDY_TELEMETRY_URL=off
```

**Dashboard:** https://mosaic-buddy-telemetry-production.up.railway.app

## License

MIT — see [LICENSE](LICENSE)
