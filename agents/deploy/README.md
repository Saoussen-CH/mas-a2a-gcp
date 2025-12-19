# AI Creative Studio - Deployment Guide

Complete deployment guide for the AI Creative Studio multi-agent system.

## Architecture

The system consists of:
- **5 Specialist Agents** (Cloud Run): Brand Strategist, Copywriter, Designer, Critic, Project Manager
- **1 Orchestrator Agent** (Agent Engine): Creative Director that coordinates all specialists

## Quick Start

### 1. Setup GCP Infrastructure

Create all service accounts and grant permissions:

```bash
cd agents/deploy
./setup_all_specialists.sh
```

This will:
- Enable required GCP APIs (Cloud Run, Vertex AI, etc.)
- Create service accounts for all 5 specialists
- Grant necessary IAM roles
- Grant you permission to deploy services

### 2. Deploy All Agents

Deploy all specialists and the orchestrator in one command:

```bash
./deploy_complete_system.sh
```

This will:
- Deploy all 5 specialist agents to Cloud Run (parallel)
- Collect their URLs
- Deploy Creative Director to Agent Engine with agent URLs

**Expected time**: 10-15 minutes

### 3. Configure Authentication

Allow agent-to-agent communication:

```bash
./allow_unauthenticated.sh
```

This enables the Creative Director to call specialist agents via A2A protocol.

### 4. Test Deployment

Run the complete test suite:

```bash
./test_agents.sh
```

See [TESTING.md](TESTING.md) for detailed testing documentation.

## Deployment Scripts

### Setup Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `setup_all_specialists.sh` | Create service accounts and grant IAM permissions | First-time setup |
| `setup_specialists_batch.sh` | Batch service account creation with propagation wait | Alternative setup method |
| `fix_iam_permissions.sh` | Fix permission issues for existing service accounts | If deployment fails with IAM errors |

### Deployment Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `deploy_complete_system.sh` | Deploy everything (specialists + orchestrator) | Complete deployment |
| `deploy_orchestrator_two_stage.py` | Deploy only Creative Director to Agent Engine | Update orchestrator only |

**Orchestrator deployment options**:
```bash
# Deploy with auto-deploy specialists
python3 deploy_orchestrator_two_stage.py --action deploy --auto-deploy-specialists

# Deploy orchestrator only (assumes specialists already deployed)
python3 deploy_orchestrator_two_stage.py --action deploy

# Test deployed orchestrator
python3 deploy_orchestrator_two_stage.py --action test --resource_name <resource_name>

# Delete orchestrator
python3 deploy_orchestrator_two_stage.py --action cleanup --resource_name <resource_name>
```

### Authentication Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `allow_unauthenticated.sh` | Allow public access to specialist agents | Testing and development (recommended) |
| `configure_agent_auth.sh` | Configure service account authentication | Production deployment (experimental) |

### Testing Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `test_agents.sh` | Run test suite | After deployment to verify everything works |
| `test_deployed_agents.py` | Python test script with detailed options | Advanced testing scenarios |

## Step-by-Step Deployment

### First-Time Deployment

1. **Setup GCP Project**
   ```bash
   ./setup_all_specialists.sh
   ```
   - Creates service accounts
   - Grants IAM permissions
   - Enables required APIs

2. **Deploy Specialists to Cloud Run**
   ```bash
   ./deploy_complete_system.sh
   ```
   - Builds and deploys all 5 specialist agents
   - Collects Cloud Run URLs
   - Deploys Creative Director orchestrator

3. **Configure Authentication**
   ```bash
   ./allow_unauthenticated.sh
   ```
   - Enables A2A communication between agents

4. **Test Everything**
   ```bash
   ./test_agents.sh
   ```
   - Verifies all agents are working
   - Tests orchestration workflow

### Update Orchestrator Only

If you only need to update the Creative Director:

```bash
python3 deploy_orchestrator_two_stage.py --action deploy
```

This deploys the orchestrator without redeploying specialists.

### Update Individual Specialists

To update a single specialist agent:

```bash
cd agents/[agent_name]
./deploy/deploy.sh
```

For example:
```bash
cd agents/copywriter
./deploy/deploy.sh
```

## Configuration Files

### Environment Variables (.env)

Required in project root:

```bash
# Google Cloud
PROJECT_ID=your-project-id
LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=true

# Specialist Agent URLs (auto-populated by deployment)
STRATEGIST_AGENT_URL=https://brand-strategist-xxx.a.run.app
COPYWRITER_AGENT_URL=https://copywriter-xxx.a.run.app
DESIGNER_AGENT_URL=https://designer-xxx.a.run.app
CRITIC_AGENT_URL=https://critic-xxx.a.run.app
PM_AGENT_URL=https://project-manager-xxx.a.run.app

# Orchestrator (auto-populated by deployment)
AGENT_ENGINE_RESOURCE_NAME=projects/.../reasoningEngines/...

# Optional: Notion integration for Project Manager
NOTION_API_KEY=your-notion-key
NOTION_DATABASE_ID=your-database-id
```

## Troubleshooting

### Deployment Fails with IAM Errors

**Error**: `Permission 'iam.serviceaccounts.actAs' denied`

**Solution**:
```bash
./setup_all_specialists.sh
```

This creates service accounts and grants you permission to impersonate them.

### Service Account Propagation Issues

**Error**: `Service account does not exist` immediately after creation

**Solution**: Use the batch setup script with built-in propagation wait:
```bash
./setup_specialists_batch.sh
```

### Authentication Errors During Testing

**Error**: "The request was not authenticated"

**Solution**:
```bash
./allow_unauthenticated.sh
```

See [TESTING.md](TESTING.md) for more troubleshooting.

### Import Error in Orchestrator

**Error**: `ModuleNotFoundError: No module named 'creative_director.app'`

**Fix**: This was fixed in `deploy_orchestrator_two_stage.py:151` to import from `creative_director.agent` instead.

## Architecture Details

### Specialist Agents (Cloud Run)

Each specialist is deployed as a separate Cloud Run service:

- **Brand Strategist**: Market research and trend analysis
- **Copywriter**: Social media copy and captions
- **Designer**: Visual concepts and image prompts
- **Critic**: Creative work review and feedback
- **Project Manager**: Timeline and task management

**Features**:
- A2A protocol endpoints at `/.well-known/agent.json`
- Vertex AI authentication
- Auto-scaling (0-10 instances)
- 1GB memory, 1 CPU per instance
- 5-minute timeout

### Creative Director (Agent Engine)

Orchestrator deployed to Vertex AI Agent Engine:

- Coordinates all 5 specialist agents
- Uses A2A protocol for agent-to-agent communication
- State management via Agent Engine
- Full conversation history

**Features**:
- RemoteA2aAgent connections to specialists
- Sequential task execution with verification
- Error handling and retry logic
- Complete campaign generation workflow

## Monitoring and Logs

### A2A Protocol Logging

**New!** Comprehensive logging for all Agent-to-Agent interactions:

```bash
# Fetch A2A logs with time filter
cd agents/deploy
./fetch_orchestrator_logs.sh 1h    # Last hour
./fetch_orchestrator_logs.sh 24h   # Last 24 hours

# Analyze logs for patterns
python3 analyze_agent_logs.py /tmp/orchestrator_logs_*.txt
```

**Features**:
- Agent call tracking with timestamps
- Response size and status monitoring
- Error detection and flagging
- Workflow sequence analysis

**📖 Complete Guide**: See [A2A_LOGGING_GUIDE.md](A2A_LOGGING_GUIDE.md) for:
- How to view A2A logs
- Log analysis techniques
- Debugging A2A issues
- Performance monitoring

### View Cloud Run Logs

```bash
# View specialist agent logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=brand-strategist" \
  --project=devfestahlen \
  --limit=50 \
  --format="table(timestamp,severity,textPayload)"
```

### View Agent Engine Logs

Via Cloud Console:
https://console.cloud.google.com/vertex-ai/reasoning-engines?project=devfestahlen

Or use the fetch script:
```bash
./fetch_orchestrator_logs.sh
```

### Check Service Status

```bash
# List all Cloud Run services
gcloud run services list \
  --project=devfestahlen \
  --region=us-central1 \
  --format="table(name,status,url)"

# Check specific service
gcloud run services describe brand-strategist \
  --project=devfestahlen \
  --region=us-central1
```

## Cost Optimization

### Cloud Run

- Scales to zero when not in use
- First 2 million requests/month are free
- Pay only for CPU/memory during request processing

### Agent Engine

- Charged per prediction request
- Model: Gemini 2.5 Flash (cost-effective)
- No idle costs when not in use

## Security Best Practices

### For Development/Testing
```bash
./allow_unauthenticated.sh
```
- URLs are private (not indexed)
- Good for rapid iteration
- Easy to lock down later

### For Production
```bash
./configure_agent_auth.sh
```
- Service account authentication
- Principle of least privilege
- Audit logging enabled

### Lock Down Access
```bash
# Remove public access
for agent in brand-strategist copywriter designer critic project-manager; do
  gcloud run services remove-iam-policy-binding $agent \
    --region=us-central1 \
    --project=devfestahlen \
    --member="allUsers" \
    --role="roles/run.invoker"
done
```

## Cleanup

### Delete Orchestrator Only
```bash
python3 deploy_orchestrator_two_stage.py --action cleanup \
  --resource_name "projects/.../reasoningEngines/..."
```

### Delete Everything
```bash
cd agents/deploy
./teardown_gcp.sh
```

This removes:
- All Cloud Run services
- Agent Engine deployments
- Service accounts
- IAM bindings

**Warning**: This is destructive and cannot be undone.

## Additional Resources

- [TESTING.md](TESTING.md) - Complete testing guide
- [A2A Protocol Docs](https://github.com/google/genai-agent-to-agent-protocol) - Agent-to-agent communication
- [Agent Engine Docs](https://cloud.google.com/vertex-ai/docs/agent-builder) - Vertex AI Agent Engine
- [Cloud Run Docs](https://cloud.google.com/run/docs) - Cloud Run deployment

## Support

For issues or questions:
1. Check [TESTING.md](TESTING.md) troubleshooting section
2. Review Cloud Run logs
3. Check Agent Engine status in Cloud Console
4. Verify `.env` configuration
