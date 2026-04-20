# mosaic-tech

Technical co-pilot for non-engineering teams at Mosaic Wellness.

Helps product managers, ops people, revenue analysts, and growth team members build and maintain internal tools with confidence. Speaks your language, catches real problems, offers to do the work.

## Installation

### From Marketplace

```bash
claude install mosaic-tech
```

### Local Development

```bash
git clone <repo-url>
cd claude-plugins/plugins/mosaic-tech
claude plugin link .
```

## Commands

| What you want to do | Command |
|---------------------|---------|
| Check before sharing | `/mosaic-tech doctor` |
| Check my tech choices | `/mosaic-tech review-stack` |
| Review how this is built | `/mosaic-tech review` |
| Review the user journey | `/mosaic-tech ux` |
| Help me plan a feature | `/mosaic-tech brainstorm` |
| Give me the real feedback | `/mosaic-tech grillme` |
| Write it down for me | `/mosaic-tech document [prd\|spec\|adr\|update\|refresh]` |
| Help me fix a bug | `/mosaic-tech debug` |
| See how I'm using Claude | `/mosaic-tech 10x [all]` |
| What plugins should I use? | `/mosaic-tech recommendations` |
| Show me everything | `/mosaic-tech help` |

Just run `/mosaic-tech` with no arguments to see the interactive menu.

## What's Inside

### 9 Agents

| Agent | Purpose | Model |
|-------|---------|-------|
| doctor | Thorough health audit (80+ checks) | Sonnet |
| reviewer | Intent-first architecture review | Sonnet |
| stack-reviewer | Stack red flag detection | Sonnet |
| ux-reviewer | UX audit for internal tools | Sonnet |
| brainstormer | Idea → structured spec | Sonnet |
| grillme | Holistic product + code review | Sonnet |
| documenter | PRD / spec / ADR generator | Sonnet |
| debugger | Structured debugging workflow | Sonnet |
| coach | Weekly coaching report | Opus |

### 4 Skills

| Skill | Purpose |
|-------|---------|
| conventions | Approved stack, project structure, security, deployment, tone |
| ai-app-conventions | Model selection, cost management, AI safety, MCP |
| ux-heuristics | UX patterns for internal tools |
| doc-templates | PRD, tech spec, ADR templates |

### 2 Hooks

- **PreToolUse (Write/Edit):** Blocks hardcoded API keys
- **PostToolUse (Bash):** Warns on leaked keys in output

## Approved Stack

| Layer | Choice |
|-------|--------|
| Backend | Fastify (Node 20 LTS) |
| Frontend | React + Vite |
| Database | MySQL + Prisma |
| Auth | Google OAuth |
| Deployment | EC2 |
| AI SDK | @anthropic-ai/sdk |

## License

MIT — see [LICENSE](LICENSE)
