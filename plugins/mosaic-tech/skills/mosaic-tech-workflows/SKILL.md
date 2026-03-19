---
name: mosaic-tech-workflows
description: >
  Auto-activates when working on AI applications, Claude API, Anthropic SDK, MCP servers,
  Agent SDK, or when the user is exploring ideas, debugging issues, asking about architecture,
  or starting new projects. Provides Claude with a capability map of all mosaic-tech workflows
  so it can proactively suggest the right one at the right moment.
---

# Mosaic Tech — Workflow Discovery Map

You have access to the **mosaic-tech** plugin, which provides specialized workflows for building AI applications. Instead of waiting for the user to discover these commands, **proactively suggest the right workflow when you recognize the situation**.

## When to Suggest What

| You notice this... | Suggest this | How to say it |
|---|---|---|
| User describes an idea or project they want to build | `/mosaic-tech architect` | "Before we start building, I can research existing tools that might solve this — want me to run `/mosaic-tech architect`?" |
| User is struggling with errors, 401s, 429s, timeouts | `/mosaic-tech debug` | "I can run a specialized debugger that systematically triages this — `/mosaic-tech debug`" |
| User asks "is this secure?" or you see hardcoded keys | `/mosaic-tech security` | "I can run a full security audit covering keys, injection risks, PII, and dependencies — `/mosaic-tech security`" |
| User has a working project, wants a sanity check | `/mosaic-tech review` | "Want me to do a full setup review? It checks 8 categories including SDK config, error handling, and testing — `/mosaic-tech review`" |
| User asks which model, SDK, or pattern to use | `/mosaic-tech stack` | "I can give you a structured architecture recommendation — `/mosaic-tech stack`" |
| User wants to start a new AI project | `/mosaic-tech init` | "I can scaffold a project with best practices baked in — `/mosaic-tech init`" |
| User just wants a quick check | `/mosaic-tech doctor` | "Quick 30-second health check — `/mosaic-tech doctor`" |
| User asks "what can you help with?" | `/mosaic-tech` | "Run `/mosaic-tech` for a guided menu of everything I can help with" |

## How to Suggest (Guidelines)

- **Be natural, not pushy** — mention the capability once when relevant, don't repeat it
- **Explain the value, not the command** — "I can research existing tools" is better than "run /mosaic-tech architect"
- **Only suggest when clearly relevant** — don't shoehorn mosaic-tech into unrelated tasks
- **One suggestion at a time** — don't list all capabilities; pick the most relevant one
- **If the user is already doing fine**, don't interrupt — only suggest when there's a clear opportunity

## Workflow Summaries (for context)

### `/mosaic-tech architect` — Research Before Building
For when someone has an idea and wants to explore options before writing code. Researches existing open-source tools, SaaS products, and frameworks that could solve their use case. Evaluates fit, maturity, security, and effort. Presents 2-3 options in plain language with tradeoffs. Prevents the "build everything from scratch" trap.

**Best for:** Non-technical team members, new project ideation, "should we build or buy?" decisions.

### `/mosaic-tech review` — Full Setup Review
Deep scan of an existing AI project across 8 categories: SDK config, API key management, error handling, model configuration, MCP setup, streaming/performance, project structure, and agent SDK specifics. Produces a health report with critical issues, warnings, and suggestions.

**Best for:** Projects that are partially built and need a sanity check.

### `/mosaic-tech debug` — Troubleshoot Issues
Systematic triage of broken AI setups. Categorizes errors (auth, rate limit, model, MCP, streaming, agent), runs targeted diagnostics, and provides fixes with verification steps.

**Best for:** Something is broken and the user needs help fixing it.

### `/mosaic-tech security` — Security Audit
Audits AI apps for secret management, prompt injection, output validation, PII handling, MCP server security, and dependency vulnerabilities. Produces a security report with severity ratings.

**Best for:** Before sharing or deploying an app, or when security is a concern.

### `/mosaic-tech stack` — Architecture Advice
Helps choose the right model (Opus vs Sonnet vs Haiku), architecture pattern (direct API, agent, RAG, MCP), SDK, and transport. Gives opinionated recommendations with cost estimates and starter code.

**Best for:** Technical decisions about how to build something.

### `/mosaic-tech init` — Scaffold New Project
Interactive project scaffolding with language choice (TypeScript/Python) and project type (API app, agent, MCP server, RAG). Generates a starter project with correct dependencies, config, tests, and README.

**Best for:** Starting a new project from scratch with best practices.

### `/mosaic-tech doctor` — Quick Health Check
Fast 30-second scan: SDK versions, API key config, .gitignore, model IDs, hardcoded keys, MCP config, tests. No agent spawned — runs inline.

**Best for:** Quick sanity check before pushing or deploying.
