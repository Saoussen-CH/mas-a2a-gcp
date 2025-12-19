# AI Creative Studio - Comprehensive Deployment Guide

Complete guide for deploying the AI Creative Studio multi-agent system to Google Cloud.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [First-Time Setup](#first-time-setup)
3. [Deployment Methods](#deployment-methods)
4. [Verification & Testing](#verification--testing)
5. [Troubleshooting](#troubleshooting)
6. [Rollback Procedures](#rollback-procedures)
7. [Cost Optimization](#cost-optimization)

---

## Prerequisites

### Required Tools

- **Python 3.11+**: Check with `python3 --version`
- **Google Cloud CLI**: Install from https://cloud.google.com/sdk/docs/install
- **Git**: For cloning the repository

### Google Cloud Requirements

1. **GCP Project** with billing enabled
2. **APIs Enabled**:
   - Cloud Run API
   - Cloud Build API
   - Vertex AI API
   - Secret Manager API (optional)

3. **Permissions Required**:
   - Cloud Run Admin
   - Service Account Admin
   - Vertex AI User
   - IAM Security Admin (for service accounts)

### API Keys

- **Gemini API Key**: Get from [Google AI Studio](https://aistudio.google.com/app/apikey)

---

## First-Time Setup

### Step 1: Clone Repository and Install Dependencies

```bash
# Clone repository
git clone <your-repo-url>
cd ai-creative-studio

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (optional, for local testing)
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your credentials
nano .env  # or use your preferred editor
```

**Required `.env` variables:**

```bash
GCP_PROJECT_ID=your-gcp-project-id
GCP_REGION=us-central1
GOOGLE_API_KEY=your-gemini-api-key
```

### Step 3: Authenticate with Google Cloud

```bash
# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project your-gcp-project-id

# Get application default credentials (for local testing)
gcloud auth application-default login
```

### Step 4: Enable Required APIs

The deployment scripts will attempt to enable these automatically, but you can do it manually:

```bash
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    aiplatform.googleapis.com \
    secretmanager.googleapis.com
```

### Step 5: Create Service Accounts (Optional - First Time Only)

Service accounts are created automatically during deployment, but you can pre-create them:

```bash
cd agents/common
python3 setup_service_accounts.py
```

This creates 5 service accounts (one for each specialist agent) with necessary IAM roles.

---

## Deployment Methods

### Method 1: Single-Command Deployment (Recommended)

**Easiest and fastest** - deploys everything in one command:

```bash
cd agents/deploy
./deploy_complete_system.sh
```

**What it does:**
1. Validates prerequisites (gcloud, python3)
2. Checks for .env file
3. Deploys all 5 specialist agents to Cloud Run (parallel)
4. Collects agent URLs automatically
5. Deploys Creative Director to Vertex AI Agent Engine
6. Outputs configuration details

**Time:** ~10-15 minutes

---

### Method 2: Python Script with Auto-Deploy

**More verbose output** - good for debugging:

```bash
cd agents/deploy
python3 deploy_orchestrator_two_stage.py --action deploy --auto-deploy-specialists
```

Same as Method 1, but with detailed Python output for each step.

---

### Method 3: Manual Two-Stage Deployment

**Maximum control** - deploy specialists and orchestrator separately:

#### Stage 1: Deploy Specialist Agents

```bash
cd agents/common
python3 deploy_all_specialists.py
```

**Output:**
- Deploys all 5 agents in parallel
- Shows progress for each agent
- Saves URLs to `.env.specialists` file

#### Stage 2: Deploy Orchestrator

After specialists are deployed:

```bash
cd ../deploy

# Copy URLs from .env.specialists to your main .env file
# Or let the script read environment variables

python3 deploy_orchestrator_two_stage.py --action deploy
```

**Output:**
- Creates Agent Engine resource
- Uploads agent code with URLs as environment variables
- Outputs resource name for future operations

---

### Method 4: Deploy Individual Agents (Testing/Updates)

For testing a single agent or updating one agent:

#### Using Existing deploy.sh (Single Agent)

```bash
cd agents/brand_strategist  # or any other agent directory
../deploy/deploy.sh
```

The script will use the .env file in the agent directory.

#### Using gcloud Directly

```bash
cd agents/copywriter  # example

gcloud run deploy copywriter \
    --source=. \
    --port=8080 \
    --region=us-central1 \
    --platform=managed \
    --no-allow-unauthenticated \
    --service-account=copywriter-sa@PROJECT_ID.iam.gserviceaccount.com
```

---

## Verification & Testing

### Verify Specialist Agent Deployments

#### Check Cloud Run Services

```bash
gcloud run services list --region=us-central1
```

Expected output: 5 services (brand-strategist, copywriter, designer, critic, project-manager)

#### Test Individual Agent A2A Endpoint

```bash
# Get authentication token
export TOKEN=$(gcloud auth print-identity-token)

# Test agent card endpoint
curl -H "Authorization: Bearer $TOKEN" \
    https://brand-strategist-xxxxx.us-central1.run.app/.well-known/agent-card.json

# Should return JSON with agent metadata
```

#### Verify Agent is Responding

```bash
# Create a test session
curl -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -X POST \
    https://brand-strategist-xxxxx.us-central1.run.app/sessions \
    -d '{}'
```

---

### Verify Agent Engine Deployment

#### List Agent Engines

```bash
gcloud ai reasoning-engines list \
    --region=us-central1 \
    --project=your-project-id
```

#### Test Creative Director Orchestrator

```bash
cd agents/deploy

# Test with resource name
python3 deploy_orchestrator_two_stage.py \
    --action test \
    --resource_name "projects/.../reasoningEngines/..."
```

Or use the test script if available:

```bash
cd ../..  # back to project root
python test_orchestrator.py
```

---

## Troubleshooting

### Common Issues

#### 1. "gcloud: command not found"

**Problem:** Google Cloud SDK not installed or not in PATH

**Solution:**
```bash
# Install gcloud
# MacOS
brew install --cask google-cloud-sdk

# Linux
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Verify installation
gcloud version
```

---

#### 2. "Permission Denied" Errors

**Problem:** Insufficient IAM permissions

**Solution:**
```bash
# Check your current permissions
gcloud projects get-iam-policy your-project-id \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:YOUR_EMAIL"

# Required roles:
# - roles/run.admin
# - roles/iam.serviceAccountAdmin
# - roles/aiplatform.user
```

Ask your GCP admin to grant these roles if missing.

---

#### 3. "Service Account Does Not Exist"

**Problem:** Service accounts not created

**Solution:**
```bash
# Create service accounts manually
cd agents/common
python3 setup_service_accounts.py

# Or create one service account manually
gcloud iam service-accounts create brand-strategist-sa \
    --display-name="Brand Strategist Agent SA"

# Grant necessary roles
gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:brand-strategist-sa@your-project-id.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"
```

---

#### 4. "API Not Enabled" Error

**Problem:** Required GCP APIs not enabled

**Solution:**
```bash
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    aiplatform.googleapis.com
```

---

#### 5. Agent Deployment Fails with "Quota Exceeded"

**Problem:** Cloud Run or Vertex AI quota limits reached

**Solution:**
```bash
# Check quotas
gcloud compute project-info describe --project=your-project-id

# Request quota increase:
# https://console.cloud.google.com/iam-admin/quotas
```

For Gemini API rate limits, consider using Vertex AI instead (automatic in our deployment).

---

#### 6. "Cannot Connect to Agent" After Deployment

**Problem:** Agent URLs incorrect or A2A configuration wrong

**Solution:**
```bash
# Verify agent URL is correct
gcloud run services describe brand-strategist \
    --region=us-central1 \
    --format='value(status.url)'

# Check environment variables on Cloud Run service
gcloud run services describe brand-strategist \
    --region=us-central1 \
    --format='value(spec.template.spec.containers[0].env)'

# Should show:
# PUBLIC_HOST=brand-strategist-xxxxx.us-central1.run.app
# PUBLIC_PORT=443
# PROTOCOL=https
```

---

#### 7. Orchestrator Can't Find Specialist Agents

**Problem:** Agent URLs not set in orchestrator environment

**Solution:**
```bash
# Check Agent Engine environment variables
gcloud ai reasoning-engines describe REASONING_ENGINE_ID \
    --region=us-central1 \
    --format=yaml

# Should show all 5 agent URLs
# If missing, redeploy orchestrator:
python3 deploy_orchestrator_two_stage.py --action deploy
```

---

### Viewing Logs

#### A2A Protocol Logging

**NEW!** Comprehensive logging for all Agent-to-Agent interactions:

```bash
cd agents/deploy

# Fetch A2A logs from Creative Director
./fetch_orchestrator_logs.sh 1h    # Last hour
./fetch_orchestrator_logs.sh 24h   # Last 24 hours

# Analyze logs for patterns
python3 analyze_agent_logs.py /tmp/orchestrator_logs_*.txt
```

**Features:**
- Logs every agent call with timestamps and protocol details
- Response tracking with success/error detection
- Agent usage breakdown and performance metrics
- Workflow sequence analysis

**📖 Complete Guide**: See [A2A_LOGGING_GUIDE.md](A2A_LOGGING_GUIDE.md) for:
- Detailed log viewing techniques
- Debugging A2A issues
- Performance monitoring
- Log analysis examples

#### Cloud Run Logs

```bash
# View logs for specific service
gcloud run services logs read brand-strategist \
    --region=us-central1 \
    --limit=50

# Stream logs in real-time
gcloud run services logs tail brand-strategist \
    --region=us-central1
```

#### Agent Engine Logs

```bash
# View Agent Engine logs
gcloud logging read \
    "resource.type=aiplatform.googleapis.com/ReasoningEngine" \
    --limit=50 \
    --format=json
```

---

## Rollback Procedures

### Rollback Single Agent Deployment

#### Option 1: Redeploy Previous Version

```bash
# List previous revisions
gcloud run revisions list \
    --service=brand-strategist \
    --region=us-central1

# Route traffic to previous revision
gcloud run services update-traffic brand-strategist \
    --region=us-central1 \
    --to-revisions=REVISION_NAME=100
```

#### Option 2: Delete and Redeploy

```bash
# Delete service
gcloud run services delete brand-strategist \
    --region=us-central1

# Redeploy from source
cd agents/brand_strategist
gcloud run deploy brand-strategist --source=.
```

---

### Rollback Orchestrator Deployment

#### Delete Agent Engine

```bash
python3 deploy_orchestrator_two_stage.py \
    --action cleanup \
    --resource_name "projects/.../reasoningEngines/..."
```

Or manually:

```bash
gcloud ai reasoning-engines delete REASONING_ENGINE_ID \
    --region=us-central1
```

Then redeploy with correct configuration.

---

### Complete System Rollback

```bash
# 1. Delete all Cloud Run services
for service in brand-strategist copywriter designer critic project-manager; do
    gcloud run services delete $service \
        --region=us-central1 \
        --quiet
done

# 2. Delete Agent Engine
python3 deploy_orchestrator_two_stage.py \
    --action cleanup \
    --resource_name "YOUR_RESOURCE_NAME"

# 3. Clean up service accounts (optional)
for agent in brand-strategist copywriter designer critic project-manager; do
    gcloud iam service-accounts delete ${agent}-sa@PROJECT_ID.iam.gserviceaccount.com \
        --quiet
done

# 4. Redeploy from scratch
./deploy_complete_system.sh
```

---

## Cost Optimization

### Understanding Costs

**Cloud Run** (per agent):
- Min instances: 0 (no idle cost)
- Charged per request + CPU/memory usage
- ~$0.01-0.10 per 1000 requests (estimate)

**Vertex AI Agent Engine**:
- Charged per query
- ~$0.01-0.05 per query (estimate)

**Gemini API** (via Vertex AI):
- Included in Vertex AI costs
- No separate API key quota limits

### Cost Optimization Tips

1. **Set min-instances=0** for Cloud Run (default in our deployment):
   ```bash
   --min-instances=0  # No idle cost
   ```

2. **Use Vertex AI instead of API key** (automatic in deployment):
   ```bash
   GOOGLE_GENAI_USE_VERTEXAI=true
   ```

3. **Monitor usage**:
   ```bash
   # View Cloud Run metrics
   gcloud run services describe brand-strategist \
       --region=us-central1 \
       --format='table(status.traffic)'
   ```

4. **Delete unused deployments**:
   ```bash
   # If not using, delete to avoid any charges
   ./deploy_orchestrator_two_stage.py --action cleanup --resource_name=...
   ```

---

## Next Steps

After successful deployment:

1. **Update `.env` file** with AGENT_ENGINE_RESOURCE_NAME
2. **Test the system** with sample campaign briefs
3. **Monitor logs** for any issues
4. **Set up monitoring/alerting** (optional)
5. **Create backup/disaster recovery plan** (optional)

For testing:
```bash
python test_orchestrator.py
```

For production use, integrate with your application or use the Agent Engine API directly.

---

## Support

For issues:
1. Check troubleshooting section above
2. Review logs (Cloud Run and Agent Engine)
3. Verify all environment variables are set correctly
4. Consult main README.md for architecture details

---

**End of Deployment Guide**
