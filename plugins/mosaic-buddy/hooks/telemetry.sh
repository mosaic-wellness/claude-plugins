#!/bin/bash
# Mosaic Buddy telemetry — fires on SubagentStart and UserPromptSubmit.
#
# SubagentStart: logs when a mosaic-buddy agent actually executes (doctor, reviewer, etc.)
# UserPromptSubmit: logs inline commands (help, menu, recommendations) that don't spawn agents.
#
# Sends: command name, source (agent|prompt), git email, repo name, timestamp.
# Sends nothing else. Opt out: export MOSAIC_BUDDY_TELEMETRY_URL=off

URL="${MOSAIC_BUDDY_TELEMETRY_URL:-https://mosaic-buddy-telemetry-production.up.railway.app}"

if [ "$URL" = "off" ] || [ -z "$URL" ]; then
  exit 0
fi

# Read JSON from stdin
INPUT=$(cat)

# Extract hook event name
if command -v jq >/dev/null 2>&1; then
  EVENT=$(echo "$INPUT" | jq -r '.hook_event_name // empty')
else
  EVENT=$(echo "$INPUT" | grep -o '"hook_event_name":"[^"]*"' | sed 's/.*":"//;s/"$//')
fi

COMMAND=""
SOURCE=""

if [ "$EVENT" = "SubagentStart" ]; then
  # Agent execution — agent_type is the agent name (doctor, reviewer, etc.)
  if command -v jq >/dev/null 2>&1; then
    COMMAND=$(echo "$INPUT" | jq -r '.agent_type // empty')
  else
    COMMAND=$(echo "$INPUT" | grep -o '"agent_type":"[^"]*"' | sed 's/.*":"//;s/"$//')
  fi
  SOURCE="agent"

elif [ "$EVENT" = "UserPromptSubmit" ]; then
  # User prompt — only proceed if it starts with /mosaic-buddy
  if command -v jq >/dev/null 2>&1; then
    PROMPT=$(echo "$INPUT" | jq -r '.prompt // empty')
  else
    PROMPT=$(echo "$INPUT" | grep -o '"prompt":"[^"]*"' | sed 's/.*":"//;s/"$//')
  fi

  case "$PROMPT" in
    /mosaic-buddy*|/Mosaic-buddy*) ;;
    *) exit 0 ;;
  esac

  # Extract the subcommand (first word after /mosaic-buddy)
  COMMAND=$(echo "$PROMPT" | sed 's|^/[bB]eacon[[:space:]]*||' | awk '{print $1}' | tr -cd 'a-zA-Z0-9-')

  # Skip if this is an agent command — SubagentStart will handle it
  case "$COMMAND" in
    doctor|review|review-stack|ux|brainstorm|grillme|document|debug|10x) exit 0 ;;
  esac

  SOURCE="prompt"
else
  exit 0
fi

EMAIL="$(git config user.email 2>/dev/null || echo unknown)"
PROJECT="$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo unknown)"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

curl -s -o /dev/null "${URL}/t?c=${COMMAND:-menu}&u=${EMAIL}&p=${PROJECT}&s=${SOURCE}" \
  --connect-timeout 2 --max-time 3 &

exit 0
