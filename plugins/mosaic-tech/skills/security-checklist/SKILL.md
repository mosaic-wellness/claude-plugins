---
name: security-checklist
description: >
  Security best practices for AI applications — API key management, prompt injection prevention,
  output validation, PII handling, and MCP server security. Auto-activates when working on
  AI applications that handle user input, store API keys, or expose MCP tools.
---

# AI App Security Checklist

## API Key Management

### Do
- Store keys in `.env` files, never in source code
- Add `.env`, `.env.local`, `.env.*.local` to `.gitignore`
- Provide `.env.example` with placeholder values
- Use environment variables at runtime (`process.env.ANTHROPIC_API_KEY`)
- Rotate keys if they may have been exposed
- Use separate keys for development and production

### Don't
- Hardcode keys in source files
- Commit `.env` files to git
- Log API keys (even partially)
- Include keys in client-side code
- Share keys in Slack/email
- Use the same key across all environments

### Key Format Reference
- Anthropic: `sk-ant-api03-...` (starts with `sk-ant-`)
- OpenAI: `sk-...` (starts with `sk-`)
- Admin MCP: `amk_...` (starts with `amk_`)

## Prompt Injection Prevention

### System Prompt Safety
- Never interpolate user input into system prompts
- Keep system prompts as static strings
- User input belongs in the `messages` array as `role: "user"` content only
- If you must include dynamic data in system prompts, use a strict allowlist

### Input Sanitization
- Validate and sanitize all user input before including in API calls
- Strip or escape control characters and prompt delimiters
- Set maximum input length limits
- Log suspicious inputs for monitoring

### Output Safety
- Never trust AI output for security-critical operations
- Validate AI-generated JSON before parsing
- Sanitize AI output before rendering as HTML
- Never use AI output directly in database queries
- Never use AI output in shell commands without validation

## PII & Data Handling

### Before Sending to AI
- Identify what PII is being sent (names, emails, health data, etc.)
- Ensure you have consent to process this data via AI
- Consider redacting PII before sending (replace with placeholders)
- Be aware of data residency requirements

### Logging & Storage
- Don't log full AI prompts/responses if they contain PII
- Implement log redaction for sensitive fields
- Set retention policies for AI interaction logs
- Use structured logging to control what's captured

### Regulatory
- HIPAA: Medical/health data requires special handling
- GDPR: EU user data requires consent and right-to-deletion
- Document your AI data flow for compliance audits

## MCP Server Security

### Authentication
- Always require authentication for HTTP/SSE MCP servers
- Use API keys or OAuth tokens (not basic auth)
- Validate auth on every request (not just connection)
- Implement key rotation support

### Tool Safety
- Validate all tool input parameters against schemas
- Use allowlists for file paths, URLs, and commands
- Never pass tool inputs directly to shell commands
- Implement rate limiting per client
- Log all tool invocations for audit trails

### Network
- Use HTTPS for all remote MCP servers
- Configure CORS appropriately (not wildcard)
- Set request size limits
- Implement timeout on long-running tools
