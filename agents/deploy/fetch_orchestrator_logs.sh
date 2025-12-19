#!/bin/bash
#
# Fetch and analyze Creative Director orchestrator logs from Cloud Logging
#

set -e

# Load environment variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/../.."

if [ -f "$PROJECT_ROOT/.env" ]; then
    source <(grep -v '^#' "$PROJECT_ROOT/.env" | grep -v '^[[:space:]]*$' | sed 's/\r$//')
fi

PROJECT_ID="${PROJECT_ID:-devfestahlen}"
AGENT_ENGINE_ID="${AGENT_ENGINE_ID:-}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Fetching Orchestrator Logs ===${NC}\n"

if [ -z "$AGENT_ENGINE_ID" ]; then
    echo -e "${YELLOW}Warning: AGENT_ENGINE_ID not set in .env${NC}"
    echo -e "${YELLOW}Fetching all reasoning engine logs...${NC}\n"
    FILTER='resource.type="aiplatform.googleapis.com/ReasoningEngine"'
else
    echo -e "${GREEN}Fetching logs for Agent Engine: ${AGENT_ENGINE_ID}${NC}\n"
    FILTER="resource.type=\"aiplatform.googleapis.com/ReasoningEngine\" AND resource.labels.reasoning_engine_id=\"${AGENT_ENGINE_ID}\""
fi

# Allow custom time filter
TIME_FILTER="${1:-1h}"
echo -e "${GREEN}Time range: Last ${TIME_FILTER}${NC}"

# Output file
OUTPUT_FILE="/tmp/orchestrator_logs_$(date +%Y%m%d_%H%M%S).txt"

echo -e "\n${YELLOW}Fetching logs from Cloud Logging...${NC}"

gcloud logging read "$FILTER" \
    --project="$PROJECT_ID" \
    --limit=500 \
    --freshness="$TIME_FILTER" \
    --format="table(timestamp,textPayload)" \
    > "$OUTPUT_FILE"

echo -e "${GREEN}✓ Logs saved to: ${OUTPUT_FILE}${NC}"

# Count log entries
LOG_COUNT=$(grep -c "INFO\|ERROR\|WARNING" "$OUTPUT_FILE" || echo "0")
echo -e "${GREEN}✓ Retrieved ${LOG_COUNT} log entries${NC}\n"

# Show agent calls and responses
echo -e "${YELLOW}Agent Call Summary:${NC}"
grep -E "AGENT CALL|AGENT RESPONSE" "$OUTPUT_FILE" | head -20 || echo "No agent calls found in logs"

echo -e "\n${YELLOW}Errors:${NC}"
grep "ERROR" "$OUTPUT_FILE" | head -10 || echo "No errors found"

echo -e "\n${GREEN}Full logs available at: ${OUTPUT_FILE}${NC}"
echo -e "${YELLOW}To analyze logs in detail:${NC}"
echo -e "  python3 analyze_agent_logs.py ${OUTPUT_FILE}"
