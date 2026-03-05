#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-https://gt.nikolai-linschmann.de}"
TMP_FILE="$(mktemp)"
trap 'rm -f "$TMP_FILE"' EXIT

curl -sS "${BASE_URL}/openapi.json" >"$TMP_FILE"

default_json='{}'
login_json='{"username":"test","password":"test"}'
training_preview_json='{"age":24,"strength":420,"talent":7,"style":"balanced","skill_bucket":"midfield","fatigue":20}'

passed=0
failed=0

mapfile -t endpoints < <(
  /root/projekte/GT/.venv/bin/python - <<'PY' "$TMP_FILE"
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8") as f:
    data = json.load(f)

for path, methods in data.get("paths", {}).items():
    for method in methods.keys():
        print(method.upper(), path)
PY
)

for row in "${endpoints[@]}"; do
  method="${row%% *}"
  path="${row#* }"

  # Skip websocket endpoint from HTTP verification.
  if [[ "$path" == "/api/v1/realtime" ]]; then
    continue
  fi

  url="${BASE_URL}${path}"
  url="${url//\{offerId\}/1}"
  url="${url//\{emailId\}/1}"
  url="${url//\{buildingId\}/1}"
  url="${url//\{playerId\}/1}"
  url="${url//\{fixtureId\}/1}"
  url="${url//\{campId\}/1}"
  url="${url//\{tacticId\}/1}"
  url="${url//\{resultId\}/1}"
  url="${url//\{auctionId\}/1}"
  url="${url//\{matchId\}/1}"
  url="${url//\{managerId\}/1}"
  url="${url//\{requestId\}/1}"
  url="${url//\{friendId\}/1}"
  url="${url//\{clubId\}/1}"
  url="${url//\{channelId\}/1}"
  url="${url//\{tierId\}/1}"
  url="${url//\{allianceId\}/1}"
  url="${url//\{memberId\}/1}"
  url="${url//\{taskId\}/1}"
  url="${url//\{id\}/1}"

  body="$default_json"
  if [[ "$path" == "/api/v1/auth/login" ]]; then
    body="$login_json"
  elif [[ "$path" == "/api/v1/training/preview" ]]; then
    body="$training_preview_json"
  fi

  status=""
  if [[ "$method" == "GET" || "$method" == "DELETE" ]]; then
    status=$(curl -sS -o /dev/null -w "%{http_code}" -X "$method" "$url")
  else
    status=$(curl -sS -o /dev/null -w "%{http_code}" -X "$method" -H "Content-Type: application/json" -d "$body" "$url")
  fi

  if [[ "$status" =~ ^2 ]]; then
    printf 'PASS %s %s -> %s\n' "$method" "$path" "$status"
    passed=$((passed+1))
  else
    printf 'FAIL %s %s -> %s\n' "$method" "$path" "$status"
    failed=$((failed+1))
  fi
 done

printf '\nSummary: passed=%d failed=%d\n' "$passed" "$failed"
if [[ "$failed" -gt 0 ]]; then
  exit 1
fi
