# beacon

Your project's technical co-pilot.

Built for product managers, ops people, revenue analysts, and growth teams at Mosaic Wellness who build internal tools with Claude Code. Beacon catches what breaks in production, helps you plan features, and makes sure your work is ready before anyone else sees it.

## Installation

```bash
# From the Mosaic marketplace
/plugin install beacon

# Or link locally for development
git clone git@github.com:mosaic-wellness/claude-plugins.git
cd claude-plugins/plugins/beacon
claude plugin link .
```

## Commands

Just run `/beacon` to see the interactive menu — or jump straight to what you need:

| What you want to do | Command |
|---------------------|---------|
| Is this ready to share? | `/beacon doctor` |
| Are my tech choices solid? | `/beacon review-stack` |
| How does this hold up? | `/beacon review` |
| Would a user actually like this? | `/beacon ux` |
| I have an idea | `/beacon brainstorm` |
| Give it to me straight | `/beacon grillme` |
| Write it down for me | `/beacon document [prd\|spec\|adr\|update\|refresh]` |
| Something's broken | `/beacon debug` |
| Get more out of Claude | `/beacon 10x` |
| What plugins should I use? | `/beacon recommendations` |

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

Beacon enforces these choices across all commands:

| Layer | Choice | What's blocked |
|-------|--------|---------------|
| Backend | Fastify (Node 20 LTS) | Express, Hono, Nest.js |
| Frontend | React + Vite | Next.js (unless SSR justified), Vue, Angular |
| Database | MySQL + Prisma | SQLite, PostgreSQL, MongoDB |
| Auth | Google OAuth | Custom JWT as sole auth, passport-local |
| Deployment | EC2 | Vercel, Lambda, Docker |
| AI SDK | @anthropic-ai/sdk | LangChain, OpenAI, frontend API calls |

## License

MIT — see [LICENSE](LICENSE)
