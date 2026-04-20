#!/bin/bash
# Beacon telemetry — fires on /beacon invocation via hook.
# Sends: command name, git email, repo name, timestamp.
# Sends nothing else. Opt out: export BEACON_TELEMETRY_URL=off

URL="${BEACON_TELEMETRY_URL:-https://beacon-telemetry-production.up.railway.app/beacon/telemetry}"

if [ "$URL" = "off" ] || [ -z "$URL" ]; then
  exit 0
fi

COMMAND="$(echo "$1" | awk '{print $1}' | tr -cd 'a-zA-Z0-9-')"
EMAIL="$(git config user.email 2>/dev/null || echo unknown)"
PROJECT="$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo unknown)"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

curl -s -X POST "$URL" \
  -H "Content-Type: application/json" \
  -d "{\"command\":\"${COMMAND:-menu}\",\"user_email\":\"$EMAIL\",\"project_name\":\"$PROJECT\",\"ts\":\"$TS\"}" \
  --connect-timeout 2 --max-time 3 > /dev/null 2>&1 &
