#!/bin/bash

# GCP Deployment Script for AI Creative Studio Agents
# Deploys a single agent to Cloud Run (can be run multiple times)
#
# Usage: ./deploy.sh <agent_name>
# Example: ./deploy.sh brand_strategist

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_DIR="$SCRIPT_DIR/.."
PROJECT_ROOT="$SCRIPT_DIR/../.."

# Agent configuration mapping
# Format: "agent_name|directory_name|service_name|service_account_name|display_name"
declare -A AGENT_CONFIG=(
    ["brand_strategist"]="brand_strategist|brand-strategist|brand-strategist-sa|Brand Strategist"
    ["brand-strategist"]="brand_strategist|brand-strategist|brand-strategist-sa|Brand Strategist"
    ["copywriter"]="copywriter|copywriter|copywriter-sa|Copywriter"
    ["designer"]="designer|designer|designer-sa|Designer"
    ["critic"]="critic|critic|critic-sa|Critic"
    ["project_manager"]="project_manager|project-manager|project-manager-sa|Project Manager"
    ["project-manager"]="project_manager|project-manager|project-manager-sa|Project Manager"
)

# Show usage
show_usage() {
    echo -e "${BLUE}=== AI Creative Studio - Single Agent Deployment ===${NC}\n"
    echo -e "${YELLOW}Usage:${NC}"
    echo -e "  ./deploy.sh <agent_name>\n"
    echo -e "${YELLOW}Available agents:${NC}"
    echo -e "  • brand_strategist  (or brand-strategist)"
    echo -e "  • copywriter"
    echo -e "  • designer"
    echo -e "  • critic"
    echo -e "  • project_manager   (or project-manager)\n"
    echo -e "${YELLOW}Example:${NC}"
    echo -e "  ./deploy.sh copywriter\n"
    exit 1
}

# Check if agent name provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Agent name required${NC}\n"
    show_usage
fi

AGENT_NAME="$1"

# Validate agent name
if [ -z "${AGENT_CONFIG[$AGENT_NAME]}" ]; then
    echo -e "${RED}Error: Unknown agent '${AGENT_NAME}'${NC}\n"
    show_usage
fi

# Parse agent configuration
IFS='|' read -r AGENT_DIR SERVICE_NAME SERVICE_ACCOUNT_NAME DISPLAY_NAME <<< "${AGENT_CONFIG[$AGENT_NAME]}"

# Check if agent directory exists
AGENT_PATH="$AGENTS_DIR/$AGENT_DIR"
if [ ! -d "$AGENT_PATH" ]; then
    echo -e "${RED}Error: Agent directory not found: $AGENT_PATH${NC}"
    exit 1
fi

echo -e "${GREEN}=== Deploying ${DISPLAY_NAME} Agent ===${NC}\n"

# Load environment variables from .env files
# Priority: Project root .env (lowest) -> Agent-specific .env (highest) -> Environment variables (highest)

# 1. Try to load from project root .env first
ROOT_ENV_FILE="$PROJECT_ROOT/.env"
if [ -f "$ROOT_ENV_FILE" ]; then
    echo -e "${GREEN}Loading environment variables from project root .env...${NC}"
    set -a
    source <(grep -v '^#' "$ROOT_ENV_FILE" | grep -v '^[[:space:]]*$' | sed 's/\r$//')
    set +a
    echo -e "${GREEN}Project .env loaded: $ROOT_ENV_FILE${NC}\n"
fi

# 2. Then load agent-specific .env (if exists) to allow overrides
AGENT_ENV_FILE="$AGENT_PATH/.env"
if [ -f "$AGENT_ENV_FILE" ]; then
    echo -e "${GREEN}Loading agent-specific environment variables...${NC}"
    set -a
    source <(grep -v '^#' "$AGENT_ENV_FILE" | grep -v '^[[:space:]]*$' | sed 's/\r$//')
    set +a
    echo -e "${GREEN}Agent .env loaded: $AGENT_ENV_FILE${NC}\n"
fi

# Configuration variables with fallback support for both naming conventions
# Support both PROJECT_ID and GCP_PROJECT_ID
PROJECT_ID="${PROJECT_ID:-${GCP_PROJECT_ID:-}}"

# Support both LOCATION and GCP_REGION (default to us-central1)
REGION="${LOCATION:-${GCP_REGION:-us-central1}}"

# Allow override from .env if service name is specified there
SERVICE_NAME="${GCP_SERVICE_NAME:-$SERVICE_NAME}"
SERVICE_ACCOUNT_NAME="${GCP_SERVICE_ACCOUNT_NAME:-$SERVICE_ACCOUNT_NAME}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Prompt for project ID if not set
if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}Enter your GCP Project ID:${NC}"
    read -r PROJECT_ID
fi

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: Project ID is required${NC}"
    exit 1
fi

echo -e "${GREEN}Configuration:${NC}"
echo -e "  Agent: ${DISPLAY_NAME}"
echo -e "  Directory: ${AGENT_DIR}"
echo -e "  Project ID: ${PROJECT_ID}"
echo -e "  Region: ${REGION}"
echo -e "  Service Name: ${SERVICE_NAME}"
echo -e "  Service Account: ${SERVICE_ACCOUNT_NAME}\n"

# Set the project
gcloud config set project "$PROJECT_ID" --quiet

# Check if service account exists
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
if ! gcloud iam service-accounts describe "$SERVICE_ACCOUNT_EMAIL" --project="$PROJECT_ID" &>/dev/null; then
    echo -e "${YELLOW}Warning: Service account ${SERVICE_ACCOUNT_NAME} does not exist${NC}"
    echo -e "${YELLOW}Creating service account...${NC}"

    # Create service account
    gcloud iam service-accounts create "$SERVICE_ACCOUNT_NAME" \
        --display-name="${DISPLAY_NAME} Agent Service Account" \
        --project="$PROJECT_ID"

    # Grant IAM roles
    echo -e "${YELLOW}Granting IAM roles...${NC}"
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
        --role="roles/aiplatform.user" \
        --quiet

    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
        --role="roles/run.invoker" \
        --quiet

    echo -e "${GREEN}Service account created and configured${NC}\n"
fi

# Deploy to Cloud Run
echo -e "${YELLOW}Deploying to Cloud Run...${NC}"
echo -e "${YELLOW}This may take several minutes...${NC}\n"

cd "$AGENT_PATH"

gcloud run deploy "$SERVICE_NAME" \
    --source=. \
    --port=8080 \
    --platform=managed \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --service-account="$SERVICE_ACCOUNT_EMAIL" \
    --no-allow-unauthenticated \
    --set-env-vars=GOOGLE_GENAI_USE_VERTEXAI=true,GOOGLE_CLOUD_PROJECT="$PROJECT_ID",GOOGLE_CLOUD_LOCATION="$REGION" \
    --memory=1Gi \
    --cpu=1 \
    --timeout=300 \
    --max-instances=10 \
    --min-instances=0

echo -e "\n${GREEN}Deployment successful!${NC}"

# Get service URL and project number
echo -e "\n${YELLOW}Retrieving service URL...${NC}"
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --platform=managed \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --format='value(status.url)')

PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
PUBLIC_HOST="${SERVICE_NAME}-${PROJECT_NUMBER}.${REGION}.run.app"

echo -e "${GREEN}Service URL: ${SERVICE_URL}${NC}"
echo -e "${GREEN}Public Host: ${PUBLIC_HOST}${NC}"

# Update A2A configuration environment variables
echo -e "\n${YELLOW}Updating A2A configuration...${NC}"

# Build environment variables update command
ENV_VARS_UPDATE="PUBLIC_HOST=$PUBLIC_HOST,PUBLIC_PORT=443,PROTOCOL=https"

# Add Notion credentials for project_manager agent
if [[ "$SERVICE_NAME" == "project-manager" ]]; then
    if [[ -n "$NOTION_API_KEY" ]] && [[ -n "$NOTION_DATABASE_ID" ]]; then
        echo -e "${GREEN}Adding Notion MCP credentials to project_manager...${NC}"
        ENV_VARS_UPDATE="$ENV_VARS_UPDATE,NOTION_API_KEY=$NOTION_API_KEY,NOTION_DATABASE_ID=$NOTION_DATABASE_ID"
    else
        echo -e "${YELLOW}Warning: NOTION_API_KEY or NOTION_DATABASE_ID not set - project_manager will work without Notion integration${NC}"
    fi
fi

gcloud run services update "$SERVICE_NAME" \
    --platform=managed \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --update-env-vars="$ENV_VARS_UPDATE" \
    --quiet

echo -e "${GREEN}A2A configuration updated${NC}"

# Grant allUsers permission to invoke the service (required for A2A communication)
echo -e "\n${YELLOW}Granting invoke permissions for A2A communication...${NC}"
gcloud run services add-iam-policy-binding "$SERVICE_NAME" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --member="allUsers" \
    --role="roles/run.invoker" \
    --quiet

echo -e "${GREEN}Invoke permissions granted${NC}"

# Display testing instructions
echo -e "\n${GREEN}=== Deployment Complete ===${NC}\n"
echo -e "Service URL: ${SERVICE_URL}\n"

# Save URL to environment variable format
ENV_VAR_NAME=$(echo "${AGENT_DIR}" | tr '[:lower:]' '[:upper:]' | tr '_' '_')
case "$AGENT_DIR" in
    "brand_strategist")
        ENV_VAR_NAME="STRATEGIST_AGENT_URL"
        ;;
    "copywriter")
        ENV_VAR_NAME="COPYWRITER_AGENT_URL"
        ;;
    "designer")
        ENV_VAR_NAME="DESIGNER_AGENT_URL"
        ;;
    "critic")
        ENV_VAR_NAME="CRITIC_AGENT_URL"
        ;;
    "project_manager")
        ENV_VAR_NAME="PM_AGENT_URL"
        ;;
esac

echo -e "${YELLOW}Add this to your .env file for orchestrator deployment:${NC}"
echo -e "${ENV_VAR_NAME}=\"${SERVICE_URL}\"\n"

echo -e "${YELLOW}To test the agent card:${NC}"
echo -e "  export TOKEN=\$(gcloud auth print-identity-token)"
echo -e "  curl -H \"Authorization: Bearer \$TOKEN\" ${SERVICE_URL}/.well-known/agent-card.json | jq\n"

echo -e "${YELLOW}To test with A2A Inspector:${NC}"
echo -e "  cd ~/a2a-inspector && bash scripts/run.sh"
echo -e "  # Open http://localhost:5001"
echo -e "  # Connect to: ${SERVICE_URL}"
echo -e "  # Add header: Authorization: Bearer \$TOKEN\n"

echo -e "${YELLOW}To view logs:${NC}"
echo -e "  gcloud run services logs tail ${SERVICE_NAME} --region=${REGION}\n"

echo -e "${GREEN}Deployment complete!${NC}"
