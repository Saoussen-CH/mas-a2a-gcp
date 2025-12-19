#!/bin/bash
#
# Batch GCP Setup for All Specialist Agents
# Uses a 3-phase approach: Create -> Wait -> Grant Permissions
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Load environment
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../../.env"

if [ -f "$ENV_FILE" ]; then
    echo -e "${GREEN}Loading .env...${NC}"
    set -a
    source <(grep -v '^#' "$ENV_FILE" | grep -v '^[[:space:]]*$' | sed 's/\r$//')
    set +a
fi

PROJECT_ID="${PROJECT_ID:-devfestahlen}"
REGION="${REGION:-us-central1}"
USER_EMAIL="${USER_EMAIL:-arfaamalg@gmail.com}"

echo -e "\n${GREEN}=== 3-Phase Batch Setup for All Specialists ===${NC}\n"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "User: $USER_EMAIL"
echo ""

# Service accounts to create
declare -A SA_MAP=(
    ["copywriter-sa"]="Copywriter Agent"
    ["designer-sa"]="Designer Agent"
    ["critic-sa"]="Critic Agent"
    ["project-manager-sa"]="Project Manager Agent"
)

read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# ============================================================================
# PHASE 1: Create ALL Service Accounts
# ============================================================================
echo -e "\n${YELLOW}PHASE 1: Creating all service accounts...${NC}\n"

CREATED_COUNT=0
for SA_NAME in "${!SA_MAP[@]}"; do
    SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

    if gcloud iam service-accounts describe "$SA_EMAIL" --project="$PROJECT_ID" &>/dev/null; then
        echo "  • ${SA_NAME}: Already exists"
    else
        echo "  • ${SA_NAME}: Creating..."
        gcloud iam service-accounts create "$SA_NAME" \
            --display-name="${SA_MAP[$SA_NAME]}" \
            --project="$PROJECT_ID" \
            --quiet
        echo "    ✓ Created"
        CREATED_COUNT=$((CREATED_COUNT + 1))
    fi
done

# ============================================================================
# PHASE 2: Wait for Propagation
# ============================================================================
if [ $CREATED_COUNT -gt 0 ]; then
    echo -e "\n${YELLOW}PHASE 2: Waiting for GCP propagation...${NC}"
    echo "  Created $CREATED_COUNT new service accounts"
    echo "  Waiting 30 seconds for full propagation across GCP..."

    for i in {30..1}; do
        echo -ne "  ⏳ $i seconds remaining...\r"
        sleep 1
    done
    echo -e "\n  ✓ Propagation complete"
else
    echo -e "\n${YELLOW}PHASE 2: Skipped (all service accounts already exist)${NC}"
fi

# ============================================================================
# PHASE 3: Grant ALL Permissions
# ============================================================================
echo -e "\n${YELLOW}PHASE 3: Granting IAM permissions...${NC}\n"

for SA_NAME in "${!SA_MAP[@]}"; do
    SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
    echo "  ${SA_NAME}:"

    # Grant Vertex AI User to service account
    echo "    → Vertex AI User..."
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SA_EMAIL" \
        --role="roles/aiplatform.user" \
        --quiet 2>&1 | grep -v "Updated IAM policy" || true

    # Grant Secret Manager to service account
    echo "    → Secret Manager Accessor..."
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SA_EMAIL" \
        --role="roles/secretmanager.secretAccessor" \
        --quiet 2>&1 | grep -v "Updated IAM policy" || true

    # Grant user impersonation permission
    echo "    → Service Account User (for ${USER_EMAIL})..."
    gcloud iam service-accounts add-iam-policy-binding "$SA_EMAIL" \
        --member="user:$USER_EMAIL" \
        --role="roles/iam.serviceAccountUser" \
        --project="$PROJECT_ID" \
        --quiet 2>&1 | grep -v "Updated IAM policy" || true

    echo -e "    ${GREEN}✓ Complete${NC}"
done

# ============================================================================
# Summary
# ============================================================================
echo -e "\n${GREEN}=========================================="
echo "=== Setup Complete! ===${NC}"
echo -e "${GREEN}==========================================${NC}\n"

echo "Service Accounts Ready:"
for SA_NAME in "${!SA_MAP[@]}"; do
    echo "  ✓ ${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
done

# Also check brand-strategist (already deployed)
if gcloud iam service-accounts describe "brand-strategist-sa@${PROJECT_ID}.iam.gserviceaccount.com" --project="$PROJECT_ID" &>/dev/null; then
    echo "  ✓ brand-strategist-sa@${PROJECT_ID}.iam.gserviceaccount.com (already deployed)"
fi

echo ""
echo -e "${GREEN}Next step:${NC}"
echo "  cd agents/deploy"
echo "  ./deploy_complete_system.sh"
echo ""
