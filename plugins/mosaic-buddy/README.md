# Mosaic Buddy

**Your project's technical co-pilot.** Built for the people at Mosaic who build internal tools with Claude Code — PMs, ops, revenue, growth. You don't need to be an engineer. You just need to type `/mosaic-buddy`.

---

## Get Started

```bash
/plugin install mosaic-buddy
```

Then run `/mosaic-buddy` in any project. That's it.

<details>
<summary>Local development setup</summary>

```bash
git clone git@github.com:mosaic-wellness/claude-plugins.git
cd claude-plugins/plugins/mosaic-buddy
claude plugin link .
```
</details>

---

## What Can It Do?

| You say... | It does... | Command |
|---|---|---|
| "Is this ready to share?" | Full health audit — 80+ checks across reliability, safety, code quality, and UX | `/mosaic-buddy doctor` |
| "Are my tech choices solid?" | Quick scan for red flags — wrong DB, missing auth, deprecated models | `/mosaic-buddy review-stack` |
| "How does this hold up?" | Architecture review that asks about your intent before flagging anything | `/mosaic-buddy review` |
| "Would a user actually like this?" | UX audit with time estimates, not jargon | `/mosaic-buddy ux` |
| "I have an idea" | Turns a rough idea into a 1-page spec through conversation | `/mosaic-buddy brainstorm` |
| "Give it to me straight" | Honest product + code review — good stuff first, then what your VP would notice | `/mosaic-buddy grillme` |
| "Write it down" | Creates PRDs, tech specs, and decision records | `/mosaic-buddy document` |
| "Something's broken" | Structured debugging — classify, investigate, fix, document | `/mosaic-buddy debug` |
| "How am I doing with Claude?" | Coaching report that finds your superpowers and time sinks | `/mosaic-buddy 5x` or `10x` |

Or just run **`/mosaic-buddy`** with no arguments to see an interactive menu.

---

## Safety Built In

Two hooks run automatically on every project:

- **Before you write a file** — blocks if it contains a hardcoded API key
- **After a bash command** — warns if the output leaked a key

You don't need to configure anything. They just work.

---

## Stack Guidance

Every command knows our approved stack and will guide you toward it:

| Layer | Use this | Not this |
|---|---|---|
| Backend | Fastify (Node 20) | Express, Hono, Nest.js |
| Frontend | React + Vite | Next.js*, Vue, Angular |
| Database | MySQL + Prisma | SQLite, PostgreSQL, MongoDB |
| Auth | Google OAuth | Custom JWT, passport-local |
| Deploy | EC2 | Vercel, Lambda, Docker |
| AI | @anthropic-ai/sdk | LangChain, OpenAI |

*\*Next.js is OK if you genuinely need SSR.*

---

## Privacy & Telemetry

Lightweight, anonymous usage tracking helps the team understand adoption. Here's exactly what's sent:

| Field | Example |
|---|---|
| Command name | `doctor` |
| Git email | `you@mosaic.com` |
| Repo folder name | `expense-tracker` |
| Timestamp | `2026-04-21T10:30:00Z` |

**Nothing else.** No file contents, no source code, no API keys, no arguments beyond the command name.

Opt out anytime:
```bash
export MOSAIC_BUDDY_TELEMETRY_URL=off
```

---

## License

MIT — see [LICENSE](LICENSE)
