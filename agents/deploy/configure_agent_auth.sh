#!/bin/bash
#
# Configure Authenticated Access Between Agents
# Grants Agent Engine permission to invoke specialist Cloud Run services
#

set -e

PROJECT_ID="${PROJECT_ID:-devfestahlen}"
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
REGION="${REGION:-us-central1}"

# Agent Engine uses the Vertex AI service agent by default
AGENT_ENGINE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

AGENTS=(
    "brand-strategist"
    "copywriter"
    "designer"
    "critic"
    "project-manager"
)

echo "=== Configure Authenticated Access for Agent Engine ==="
echo ""
echo "Project: $PROJECT_ID"
echo "Project Number: $PROJECT_NUMBER"
echo "Agent Engine SA: $AGENT_ENGINE_SA"
echo ""
echo "This will grant the Agent Engine service account permission"
echo "to invoke all specialist Cloud Run services."
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

echo ""
for agent in "${AGENTS[@]}"; do
    echo "→ Granting access to $agent..."
    gcloud run services add-iam-policy-binding "$agent" \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --member="serviceAccount:$AGENT_ENGINE_SA" \
        --role="roles/run.invoker" \
        --quiet
    echo "  ✓ Done"
done

echo ""
echo "✓ Agent Engine can now invoke all specialist services"
echo ""
echo "Note: A2A protocol authentication with service accounts"
echo "is still experimental. If this doesn't work, use:"
echo "  ./allow_unauthenticated.sh"
echo ""
echo "Test again with:"
echo "  ./test_agents.sh orchestrator"
echo ""
