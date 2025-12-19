#!/bin/bash
#
# Allow Unauthenticated Access to Specialist Agents
# This makes the A2A endpoints publicly accessible for testing
#

set -e

PROJECT_ID="${PROJECT_ID:-devfestahlen}"
REGION="${REGION:-us-central1}"

AGENTS=(
    "brand-strategist"
    "copywriter"
    "designer"
    "critic"
    "project-manager"
)

echo "=== Allowing Unauthenticated Access to Specialists ==="
echo ""
echo "⚠️  This will make your agent endpoints publicly accessible."
echo "   Anyone with the URL can call them."
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

echo ""
for agent in "${AGENTS[@]}"; do
    echo "→ Setting policy for $agent..."
    gcloud run services add-iam-policy-binding "$agent" \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --member="allUsers" \
        --role="roles/run.invoker" \
        --quiet
    echo "  ✓ Done"
done

echo ""
echo "✓ All specialist agents now accept unauthenticated requests"
echo ""
echo "Test again with:"
echo "  ./test_agents.sh orchestrator"
echo ""
