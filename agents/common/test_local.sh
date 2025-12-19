#!/bin/bash

# Local Testing Script for Brand Strategist A2A Agent

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PORT=8082
BASE_URL="http://localhost:$PORT"

echo -e "${GREEN}=== Testing Brand Strategist A2A Agent Locally ===${NC}\n"

# Check if the agent is running
echo -e "${YELLOW}Checking if agent is running on port $PORT...${NC}"
if ! curl -s "$BASE_URL/.well-known/agent-card.json" > /dev/null 2>&1; then
    echo -e "${YELLOW}Agent is not running. Please start it first:${NC}"
    echo -e "${YELLOW}  python3 agent.py${NC}\n"
    exit 1
else
    echo -e "${GREEN}Agent is already running${NC}\n"
fi

# Check if jq is installed
if command -v jq &> /dev/null; then
    JQ_CMD="jq '.'"
else
    echo -e "${YELLOW}Note: jq not installed, showing raw JSON output${NC}\n"
    JQ_CMD="cat"
fi

# Test 1: Get agent card
echo -e "${YELLOW}Test 1: Getting agent card (metadata)...${NC}"
curl -s "$BASE_URL/.well-known/agent-card.json" | eval $JQ_CMD
echo -e "\n"

# Test 2: Create a session using JSON-RPC 2.0
echo -e "${YELLOW}Test 2: Creating a new session (JSON-RPC)...${NC}"
SESSION_RESPONSE=$(curl -s -X POST "$BASE_URL/" \
    -H "Content-Type: application/json" \
    -d '{
        "jsonrpc": "2.0",
        "id": 1,
        "method": "agent/invoke",
        "params": {
            "prompt": "Hello, I need market research for a new sustainable fashion brand targeting Gen Z."
        }
    }')

echo "$SESSION_RESPONSE" | eval $JQ_CMD
echo -e "\n"

# Test 3: Another query
echo -e "${YELLOW}Test 3: Asking for competitor analysis...${NC}"
QUERY_RESPONSE=$(curl -s -X POST "$BASE_URL/" \
    -H "Content-Type: application/json" \
    -d '{
        "jsonrpc": "2.0",
        "id": 2,
        "method": "agent/invoke",
        "params": {
            "prompt": "Who are the top 3 competitors in the plant-based food industry?"
        }
    }')

echo "$QUERY_RESPONSE" | eval $JQ_CMD

echo -e "\n${GREEN}=== Testing Complete ===${NC}\n"
echo -e "${YELLOW}Your A2A agent is working! It uses JSON-RPC 2.0 protocol.${NC}\n"
echo -e "To use the A2A Inspector visual tool:"
echo -e "  1. Run: ${GREEN}./deploy/setup_inspector.sh${NC}"
echo -e "  2. Start: ${GREEN}cd ~/a2a-inspector && bash scripts/run.sh${NC}"
echo -e "  3. Open: ${GREEN}http://127.0.0.1:5001${NC} and connect to ${GREEN}http://localhost:$PORT${NC}\n"
