# A2A Protocol Logging Guide

## Overview

The Creative Director orchestrator now has comprehensive logging for all Agent-to-Agent (A2A) protocol interactions. The logging is implemented using:

1. **ADK's Built-in Tracing** (`enable_tracing=True`)
2. **Cloud Logging Integration** (automatic)
3. **Agent Engine's Native Logging** (built-in)

## What Gets Logged

Every A2A interaction between the orchestrator and specialist agents is logged with:

- **Agent name** (brand_strategist, copywriter, designer, critic, project_manager)
- **Request timestamp**
- **Request content** (query/prompt sent to the agent)
- **Response timestamp**
- **Response content** (agent's output)
- **Response status** (success/error)
- **Response size** (character count)
- **A2A protocol metadata**

## Viewing A2A Logs

### Method 1: Using the Fetch Script (Recommended)

```bash
cd agents/deploy
./fetch_orchestrator_logs.sh [time_range]
```

**Examples:**
```bash
# Last hour (default)
./fetch_orchestrator_logs.sh

# Last 24 hours
./fetch_orchestrator_logs.sh 24h

# Last 7 days
./fetch_orchestrator_logs.sh 7d
```

The script will:
- Fetch logs from Cloud Logging
- Filter by your Agent Engine ID
- Show A2A call summaries
- Highlight any errors
- Save to a timestamped file

### Method 2: Using gcloud CLI

```bash
# Get all logs for your Agent Engine
gcloud logging read \
  'resource.type="aiplatform.googleapis.com/ReasoningEngine" AND
   resource.labels.reasoning_engine_id="2070963136264929280"' \
  --project=devfestahlen \
  --limit=500 \
  --format="table(timestamp,textPayload)"
```

### Method 3: Cloud Console

1. Go to: https://console.cloud.google.com/logs
2. Select project: `devfestahlen`
3. Use this query:
   ```
   resource.type="aiplatform.googleapis.com/ReasoningEngine"
   resource.labels.reasoning_engine_id="2070963136264929280"
   ```

## Analyzing Logs

Use the log analyzer utility:

```bash
cd agents/deploy
./fetch_orchestrator_logs.sh 1h
python3 analyze_agent_logs.py /tmp/orchestrator_logs_*.txt
```

This will show:
- Total A2A calls made
- Agent usage breakdown
- Average response sizes
- Error detection
- Workflow sequence

## Example Log Output

```
======================================================================
🔧 A2A AGENT CALL: brand_strategist
   Timestamp: 2025-12-18T22:45:12.123456
   Protocol: Agent-to-Agent (A2A)
   Agent Type: RemoteA2aAgent
   Query length: 450 chars
   Query preview: Create market research for eco-friendly coffee...
======================================================================

======================================================================
📥 A2A AGENT RESPONSE: brand_strategist - ✅ SUCCESS
   Timestamp: 2025-12-18T22:45:19.654321
   Protocol: Agent-to-Agent (A2A)
   Response length: 2340 chars
   Response preview: **Audience Insights:**
   Gen Z (18-25) views coffee as a lifestyle choice...
======================================================================
```

## Monitoring Specific A2A Interactions

### Check for Errors

```bash
gcloud logging read \
  'resource.type="aiplatform.googleapis.com/ReasoningEngine" AND
   resource.labels.reasoning_engine_id="2070963136264929280" AND
   severity>=ERROR' \
  --project=devfestahlen \
  --limit=50
```

### Track Specific Agent

```bash
gcloud logging read \
  'resource.type="aiplatform.googleapis.com/ReasoningEngine" AND
   resource.labels.reasoning_engine_id="2070963136264929280" AND
   textPayload=~"project_manager"' \
  --project=devfestahlen \
  --limit=50
```

### Monitor Live

```bash
gcloud logging tail \
  'resource.type="aiplatform.googleapis.com/ReasoningEngine" AND
   resource.labels.reasoning_engine_id="2070963136264929280"' \
  --project=devfestahlen
```

## Structured Logging

All A2A interactions include structured JSON metadata:

```json
{
  "event": "a2a_agent_call",
  "protocol": "a2a",
  "timestamp": "2025-12-18T22:45:12.123456",
  "agent_name": "brand_strategist",
  "query_length": 450,
  "query_preview": "Create market research..."
}
```

## Debugging A2A Issues

If an agent call fails:

1. **Check the error logs:**
   ```bash
   ./fetch_orchestrator_logs.sh 1h | grep -A 5 "ERROR"
   ```

2. **Verify agent URLs:**
   ```bash
   echo $STRATEGIST_AGENT_URL
   echo $COPYWRITER_AGENT_URL
   # etc.
   ```

3. **Test agent directly:**
   ```bash
   cd agents/deploy
   python3 test_pm_direct.py  # or other agent test scripts
   ```

4. **Check Cloud Run logs for the failing agent:**
   ```bash
   gcloud logging read \
     'resource.type="cloud_run_revision" AND
      resource.labels.service_name="project-manager"' \
     --project=devfestahlen \
     --limit=50
   ```

## Performance Metrics

The logs can be used to analyze:

- **Agent response times** - Time between call and response
- **Response sizes** - Which agents produce verbose outputs
- **Error rates** - Frequency of failed A2A calls
- **Workflow patterns** - Typical agent call sequences

## Cloud Logging Retention

- Logs are retained for **30 days** by default
- Export to BigQuery for longer retention
- Set up log sinks for real-time analysis

## Additional Resources

- [Agent Engine Logging Docs](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/troubleshooting/deploy)
- [Cloud Logging Docs](https://cloud.google.com/logging/docs)
- [A2A Protocol Spec](https://github.com/google/agent-to-agent-protocol)
