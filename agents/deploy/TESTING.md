# Testing Your Deployed Agents

This guide explains how to test your deployed AI Creative Studio agents.

## Quick Start

```bash
cd agents/deploy
./test_agents.sh
```

This runs the complete test suite for all agents.

## What Gets Tested

### Specialist Agents (Cloud Run)
- **Brand Strategist**: Market research and competitor analysis
- **Copywriter**: Social media copy creation
- **Designer**: Visual concept generation
- **Critic**: Creative work review
- **Project Manager**: Timeline and task planning

### Orchestrator (Agent Engine)
- **Creative Director**: Full campaign orchestration using all specialists

## Test Options

### Test Everything
```bash
./test_agents.sh all
# or simply
./test_agents.sh
```

### Test Only Specialists (Cloud Run)
```bash
./test_agents.sh specialists
```

### Test Only Creative Director (Agent Engine)
```bash
./test_agents.sh orchestrator
```

### Test Individual Agents
```bash
./test_agents.sh strategist      # Brand Strategist
./test_agents.sh copywriter       # Copywriter
./test_agents.sh designer         # Designer
./test_agents.sh critic           # Critic
./test_agents.sh pm               # Project Manager
```

## Using Python Directly

For more control, use the Python script directly:

```bash
# Test all agents
python3 test_deployed_agents.py --test all

# Test specialists only
python3 test_deployed_agents.py --test specialists

# Test orchestrator only
python3 test_deployed_agents.py --test orchestrator

# Test specific agent
python3 test_deployed_agents.py --agent "Brand Strategist"
```

## First-Time Setup: Fix Authentication

**IMPORTANT**: Before running tests, you need to configure authentication for agent-to-agent communication.

### Quick Fix (Recommended)

Allow unauthenticated access to specialist agents:

```bash
cd agents/deploy
./allow_unauthenticated.sh
```

This makes the A2A endpoints publicly accessible (anyone with the URL can call them). This is fine for testing and development since the URLs are not discoverable.

### Production Fix (Optional)

Configure proper service account authentication:

```bash
./configure_agent_auth.sh
```

This grants the Agent Engine's service account permission to invoke specialist services. Note: A2A authentication with service accounts is still experimental.

### Why This Is Needed

- Specialist agents are deployed with `--no-allow-unauthenticated` by default
- The Creative Director orchestrator needs permission to call them via A2A protocol
- Without this, you'll see "request was not authenticated" errors

## Understanding Test Results

### Success Output
```
✓ PASS: Brand Strategist
✓ PASS: Copywriter
✓ PASS: Designer
...
🎉 All tests passed!
```

### Failure Output
```
✗ FAIL: Copywriter
  ❌ Error: Connection timeout
...
⚠️  1 test(s) failed
```

## What Each Test Does

### Specialist Agent Tests
Each specialist receives a relevant query:

- **Brand Strategist**: Analyze eco-friendly water bottle market
- **Copywriter**: Write 3 Instagram captions for coffee brand
- **Designer**: Create visual concepts for sustainable fashion
- **Critic**: Review a social media post
- **Project Manager**: Create 2-week campaign timeline

### Orchestrator Test
The Creative Director receives a complete campaign brief and should:
1. Call Brand Strategist for research
2. Call Copywriter for post copy
3. Call Designer for visual concepts
4. Call Critic for quality review
5. Call Project Manager for timeline
6. Present complete campaign

## Troubleshooting

### "Request was not authenticated" Error
**Problem**: Specialist agents are rejecting calls from Creative Director

**Symptoms**:
- Orchestrator test shows "Error in Brand Strategist: I received an empty response"
- Cloud Run logs show "The request was not authenticated"

**Solution**: Run the authentication fix script:
```bash
./allow_unauthenticated.sh
```

This allows the Creative Director to call specialist agents via A2A protocol.

### "No URL configured" Error
**Problem**: Agent URL missing from `.env`

**Solution**: Check your `.env` file has all agent URLs:
```bash
STRATEGIST_AGENT_URL=https://brand-strategist-xxx.a.run.app
COPYWRITER_AGENT_URL=https://copywriter-xxx.a.run.app
DESIGNER_AGENT_URL=https://designer-xxx.a.run.app
CRITIC_AGENT_URL=https://critic-xxx.a.run.app
PM_AGENT_URL=https://project-manager-xxx.a.run.app
```

### "Connection Error" or "Permission Denied"
**Problem**: Authentication or network issues

**Solutions**:
1. Authenticate with gcloud:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

2. Verify service is running:
   ```bash
   gcloud run services list --project=devfestahlen --region=us-central1
   ```

3. Check if authentication is configured:
   ```bash
   ./allow_unauthenticated.sh
   ```

### "Agent Engine not found"
**Problem**: Missing `AGENT_ENGINE_RESOURCE_NAME` in `.env`

**Solution**: Add the resource name from deployment:
```bash
AGENT_ENGINE_RESOURCE_NAME=projects/xxx/locations/us-central1/reasoningEngines/xxx
```

### Agent Takes Too Long
**Problem**: First request cold start

**Explanation**: Cloud Run services have cold starts (10-30 seconds). This is normal for the first request. Subsequent requests will be faster.

## Manual Testing via Cloud Console

### Test Specialist Agents
1. Go to: https://console.cloud.google.com/run?project=devfestahlen
2. Click on an agent service (e.g., `brand-strategist`)
3. Click "Test" tab
4. Send a POST request to `/.well-known/agent.json` to verify A2A protocol

### Test Creative Director
1. Go to: https://console.cloud.google.com/vertex-ai/reasoning-engines?project=devfestahlen
2. Click on "Creative Director"
3. Use the "Test" interface to send queries

## Advanced: Custom Test Queries

Modify `test_deployed_agents.py` to add your own test queries:

```python
SPECIALIST_TESTS = {
    "Brand Strategist": "Your custom query here...",
    # ... more tests
}
```

## Monitoring and Logs

### A2A Protocol Logging

**NEW!** Comprehensive logging for all Agent-to-Agent interactions:

```bash
# Fetch A2A logs from Creative Director
./fetch_orchestrator_logs.sh 1h    # Last hour
./fetch_orchestrator_logs.sh 24h   # Last 24 hours

# Analyze logs for patterns
python3 analyze_agent_logs.py /tmp/orchestrator_logs_*.txt
```

**Features:**
- Logs every agent call with timestamps
- Response tracking with success/error detection
- Agent usage breakdown
- Workflow sequence analysis

**📖 Complete Guide**: See [A2A_LOGGING_GUIDE.md](A2A_LOGGING_GUIDE.md) for detailed documentation on viewing, analyzing, and debugging A2A protocol interactions.

### View Agent Logs
```bash
# Specialist agent logs (Cloud Run)
gcloud run services logs read brand-strategist \
  --project=devfestahlen \
  --region=us-central1 \
  --limit=50

# Creative Director logs (Agent Engine)
# View in Cloud Console:
# https://console.cloud.google.com/vertex-ai/reasoning-engines
```

### Check Agent Health
```bash
# List all Cloud Run services
gcloud run services list \
  --project=devfestahlen \
  --region=us-central1 \
  --format="table(name,status,url)"
```

## Security Considerations

### Public vs Authenticated Access

**Development/Testing** (`./allow_unauthenticated.sh`):
- ✓ Works immediately with A2A protocol
- ✓ URLs are still private (not indexed)
- ⚠️  Anyone with URL can call agents
- ✓ Good for testing and demos

**Production** (`./configure_agent_auth.sh`):
- ✓ Proper service account authentication
- ✓ Only authorized services can call agents
- ⚠️  A2A auth support is experimental
- ✓ Better for production deployments

### Switching Between Modes

To lock down public access later:
```bash
# Remove public access
for agent in brand-strategist copywriter designer critic project-manager; do
  gcloud run services remove-iam-policy-binding $agent \
    --region=us-central1 \
    --project=devfestahlen \
    --member="allUsers" \
    --role="roles/run.invoker"
done

# Then configure service account auth
./configure_agent_auth.sh
```

## Next Steps

After successful testing:
1. Integrate with frontend application
2. Set up monitoring and alerts
3. Configure rate limiting
4. Add custom logging
5. Review security settings
6. Deploy to production environment

## Getting Help

If tests fail consistently:
1. Check deployment logs
2. Verify environment variables
3. Confirm IAM permissions
4. Review Cloud Run service status
5. Check Vertex AI quotas
