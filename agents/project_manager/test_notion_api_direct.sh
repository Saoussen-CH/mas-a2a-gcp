#!/bin/bash
# Test Notion API directly

source ../../.env

echo "Testing Notion API..."
echo "API Key: ${NOTION_API_KEY:0:10}..."
echo "Database ID: $NOTION_DATABASE_ID"
echo ""

# Test 1: Get current user (verifies API key)
echo "Test 1: Verifying API key..."
curl -s -X GET 'https://api.notion.com/v1/users/me' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H 'Notion-Version: 2022-06-28' | jq '.'

echo -e "\nTest 2: Retrieving database info..."
curl -s -X GET "https://api.notion.com/v1/databases/$NOTION_DATABASE_ID" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H 'Notion-Version: 2022-06-28' | jq '.'
