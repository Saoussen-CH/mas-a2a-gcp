# A2A Inspector Testing Guide

Complete guide for testing AI Creative Studio agents using the A2A Inspector tool, both locally and on Cloud Run.

---

## Table of Contents

1. [What is A2A Inspector?](#what-is-a2a-inspector)
2. [Installation](#installation)
3. [Testing Agents Locally](#testing-agents-locally)
4. [Testing Cloud Run Deployments](#testing-cloud-run-deployments)
5. [Understanding Inspector Output](#understanding-inspector-output)
6. [Common Test Scenarios](#common-test-scenarios)
7. [Troubleshooting](#troubleshooting)

---

## What is A2A Inspector?

The **A2A Inspector** is an interactive web tool for testing and debugging agents that implement the [Agent-to-Agent (A2A) protocol](https://github.com/google/A2A).

**Key Features:**
- 🔍 Validates A2A protocol compliance
- 💬 Interactive chat interface for testing agents
- 📋 Inspects agent cards (`/.well-known/agent-card.json`)
- 🔐 Supports authentication (for Cloud Run)
- 📊 Shows request/response details
- 🐛 Debug mode for detailed logging

**Why Use It?**
- Verify your agent is A2A-compliant before deployment
- Test agent responses interactively
- Debug issues with agent communication
- Validate agent card configuration

---

## Installation

### Method 1: Automated Setup (Recommended)

Use the provided setup script:

```bash
cd agents/deploy
./setup_inspector.sh
```

**What it does:**
1. Checks prerequisites (git, Node.js, npm)
2. Clones A2A Inspector repository to `~/a2a-inspector`
3. Installs backend dependencies (Python)
4. Installs frontend dependencies (npm)

**Time:** ~2-3 minutes

---

### Method 2: Manual Installation

If you prefer manual setup:

```bash
# Clone repository
cd ~
git clone https://github.com/a2aproject/a2a-inspector.git
cd a2a-inspector

# Install backend dependencies
pip install -e .
# Or with uv (faster):
uv sync

# Install frontend dependencies
cd frontend
npm install
```

---

### Method 3: Docker (Alternative)

```bash
cd ~/a2a-inspector
docker build -t a2a-inspector .
docker run -p 5001:5001 a2a-inspector
```

---

### Prerequisites

Before installation, ensure you have:

- **Git**: `git --version`
- **Node.js 18+**: `node --version`
- **npm**: `npm --version`
- **Python 3.11+**: `python3 --version`
- **pip**: `pip --version`

---

## Testing Agents Locally

### Step 1: Start Your Local Agent

Pick an agent to test (e.g., Brand Strategist):

```bash
cd agents/brand_strategist

# Create/activate virtual environment (if not already done)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (if not exists)
cp .env.example .env

# Start the agent A2A server
python agent.py
```

**Expected output:**
```
🚀 Starting Brand Strategist A2A Server on http://0.0.0.0:8080
📋 Agent card available at: http://0.0.0.0:8080/.well-known/agent-card.json
🌐 Public URL: http://localhost:8080
```

**Agent is now running on:** `http://localhost:8080`

---

### Step 2: Start A2A Inspector

In a **new terminal**:

```bash
cd ~/a2a-inspector
bash scripts/run.sh
```

**Expected output:**
```
Starting A2A Inspector...
Backend: http://0.0.0.0:8000
Frontend: http://localhost:5001
```

**Inspector is now running on:** `http://localhost:5001`

---

### Step 3: Connect Inspector to Local Agent

1. **Open your browser** to `http://localhost:5001`

2. **Enter agent URL** in the connection field:
   ```
   http://localhost:8080
   ```

3. **Click "Connect"**

4. **Inspector validates the agent:**
   - ✅ Checks for agent card at `/.well-known/agent-card.json`
   - ✅ Validates agent card schema
   - ✅ Shows agent capabilities

---

### Step 4: Test Agent Interaction

Once connected, you can:

1. **View Agent Card:**
   - Agent name, description, version
   - Available skills/capabilities
   - Input/output schemas

2. **Start a Chat Session:**
   - Click "New Session"
   - Type a test message (e.g., "Research eco-friendly water bottles")
   - See agent's response in real-time

3. **Inspect Messages:**
   - View raw JSON requests/responses
   - Check message structure
   - Debug any issues

---

### Example Test Conversation (Brand Strategist)

**You:** "Research the market for eco-friendly water bottles targeting millennials"

**Agent Response:**
```
**Audience Insights:**
Millennials (ages 25-40) prioritize sustainability and are willing to pay
premium prices for eco-friendly products...

**Competitive Analysis:**
1. Hydro Flask - Strong brand recognition...
2. S'well - Premium positioning...

**Trending Topics:**
- Zero-waste lifestyle
- Reusable everything
- Plastic-free living
...
```

---

## Testing Cloud Run Deployments

Testing deployed agents requires authentication tokens since Cloud Run services are protected.

### Step 1: Deploy Agent to Cloud Run

```bash
# Deploy a single agent (example: brand_strategist)
cd agents/deploy
python3 deploy_all_specialists.py

# Or deploy all agents
cd ../common
python3 deploy_all_specialists.py
```

**Note the service URL** from deployment output:
```
Service URL: https://brand-strategist-xxxxx.us-central1.run.app
```

---

### Step 2: Get Authentication Token

Cloud Run requires an identity token for authentication:

```bash
# Get your identity token
export TOKEN=$(gcloud auth print-identity-token)

# Verify token (should output a long JWT string)
echo $TOKEN
```

**Token expires after 1 hour** - regenerate if needed.

---

### Step 3: Test Agent Card Endpoint

Verify the agent is accessible:

```bash
# Test agent card endpoint
curl -H "Authorization: Bearer $TOKEN" \
    https://brand-strategist-xxxxx.us-central1.run.app/.well-known/agent-card.json | jq
```

**Expected output:**
```json
{
  "name": "brand_strategist",
  "description": "Brand strategist for market research...",
  "version": "1.0.0",
  "skills": [...]
}
```

---

### Step 4: Connect Inspector with Authentication

#### Option A: Using Inspector Web UI

1. **Start A2A Inspector locally:**
   ```bash
   cd ~/a2a-inspector
   bash scripts/run.sh
   ```

2. **Open** `http://localhost:5001`

3. **Enter Cloud Run URL:**
   ```
   https://brand-strategist-xxxxx.us-central1.run.app
   ```

4. **Add Authentication Header:**
   - Click "Advanced Settings" or "Headers"
   - Add header:
     - **Name:** `Authorization`
     - **Value:** `Bearer YOUR_TOKEN_HERE`

   Replace `YOUR_TOKEN_HERE` with your actual token from `gcloud auth print-identity-token`

5. **Click "Connect"**

---

#### Option B: Using Inspector CLI (npx)

For quick validation without running the full inspector:

```bash
# Get fresh token
export TOKEN=$(gcloud auth print-identity-token)

# Inspect agent (validates A2A compliance)
npx @a2aproject/a2a-inspector inspect \
    https://brand-strategist-xxxxx.us-central1.run.app \
    --auth-header "Authorization: Bearer $TOKEN"
```

**Expected output:**
```
✓ Agent card found
✓ Agent card is valid
✓ Agent supports skills: market_research
✓ A2A protocol compliant
```

---

### Step 5: Test Multiple Deployed Agents

Create a test script to validate all 5 agents:

```bash
#!/bin/bash
# test_all_agents.sh

TOKEN=$(gcloud auth print-identity-token)

AGENTS=(
    "https://brand-strategist-xxxxx.us-central1.run.app"
    "https://copywriter-xxxxx.us-central1.run.app"
    "https://designer-xxxxx.us-central1.run.app"
    "https://critic-xxxxx.us-central1.run.app"
    "https://project-manager-xxxxx.us-central1.run.app"
)

for url in "${AGENTS[@]}"; do
    echo "Testing: $url"
    curl -H "Authorization: Bearer $TOKEN" \
        "${url}/.well-known/agent-card.json" \
        -s -o /dev/null -w "  Status: %{http_code}\n"
done
```

Run it:
```bash
chmod +x test_all_agents.sh
./test_all_agents.sh
```

**Expected output:**
```
Testing: https://brand-strategist-xxxxx.us-central1.run.app
  Status: 200
Testing: https://copywriter-xxxxx.us-central1.run.app
  Status: 200
...
```

---

## Understanding Inspector Output

### Agent Card Validation

When you connect the inspector, it validates:

**✅ Valid Agent Card:**
```json
{
  "name": "brand_strategist",
  "description": "Brand strategist for market research",
  "version": "1.0.0",
  "url": "https://brand-strategist-xxxxx.run.app",
  "skills": [
    {
      "name": "market_research",
      "description": "Research market trends and competitors"
    }
  ]
}
```

**❌ Invalid Agent Card:**
```
Error: Agent card not found at /.well-known/agent-card.json
Error: Invalid agent card schema
Error: Missing required field: name
```

---

### Session Lifecycle

The inspector shows the complete session flow:

1. **Create Session:**
   ```
   POST /sessions
   Response: { "id": "session_123", "user_id": "user_456" }
   ```

2. **Send Message:**
   ```
   POST /sessions/session_123/messages
   Body: { "message": "Research eco water bottles" }
   ```

3. **Receive Response:**
   ```
   SSE Stream: data: {"text": "**Audience Insights:**..."}
   ```

4. **End Session:**
   ```
   DELETE /sessions/session_123
   ```

---

### Request/Response Inspector

The inspector shows detailed request/response data:

**Request (sent to agent):**
```json
{
  "method": "POST",
  "url": "/sessions/abc123/messages",
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Bearer ..."
  },
  "body": {
    "message": "Research eco-friendly water bottles"
  }
}
```

**Response (from agent):**
```json
{
  "status": 200,
  "headers": {
    "Content-Type": "text/event-stream"
  },
  "body": {
    "text": "**Audience Insights:**\nMillennials prioritize...",
    "metadata": {
      "agent": "brand_strategist",
      "model": "gemini-2.5-flash"
    }
  }
}
```

---

## Common Test Scenarios

### Scenario 1: Validate All Agents Locally

Test all 5 agents are working locally:

```bash
# Terminal 1: Start Brand Strategist
cd agents/brand_strategist
python agent.py  # Runs on port 8080

# Terminal 2: Start Copywriter (change port)
cd agents/copywriter
PORT=8081 python agent.py  # Runs on port 8081

# Terminal 3: Start Designer
cd agents/designer
PORT=8082 python agent.py  # Runs on port 8082

# ... and so on for Critic (8083) and Project Manager (8084)
```

Test each with inspector:
- `http://localhost:8080` (Brand Strategist)
- `http://localhost:8081` (Copywriter)
- `http://localhost:8082` (Designer)
- etc.

---

### Scenario 2: Test Agent After Code Changes

After modifying an agent:

```bash
# 1. Restart local agent
cd agents/copywriter
python agent.py

# 2. Connect inspector
cd ~/a2a-inspector
bash scripts/run.sh

# 3. Test in browser: http://localhost:5001
# Connect to: http://localhost:8080

# 4. Send test messages and verify behavior
```

---

### Scenario 3: Pre-Deployment Validation

Before deploying to Cloud Run, validate locally:

```bash
# 1. Run agent locally
cd agents/brand_strategist
python agent.py

# 2. Use CLI inspector for quick validation
npx @a2aproject/a2a-inspector inspect http://localhost:8080

# 3. If validation passes, deploy
cd ../deploy
python3 deploy_all_specialists.py
```

---

### Scenario 4: Debug Cloud Run Issues

If agent is deployed but not working:

```bash
# 1. Check agent is accessible
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
    https://brand-strategist-xxxxx.run.app/.well-known/agent-card.json

# 2. View Cloud Run logs
gcloud run services logs read brand-strategist \
    --region=us-central1 \
    --limit=50

# 3. Test with inspector UI for detailed debugging
# Add auth header: Authorization: Bearer <token>
```

---

## Troubleshooting

### Issue 1: "Cannot connect to agent"

**Symptoms:**
- Inspector shows "Connection failed"
- "Agent card not found"

**Solutions:**

**For Local Agents:**
```bash
# Check agent is running
curl http://localhost:8080/.well-known/agent-card.json

# Verify port is correct
lsof -i :8080  # Should show python process

# Check agent logs for errors
# Look at terminal where agent is running
```

**For Cloud Run:**
```bash
# Verify service is deployed
gcloud run services list --region=us-central1

# Check service URL
gcloud run services describe brand-strategist \
    --region=us-central1 \
    --format='value(status.url)'

# Test with curl
TOKEN=$(gcloud auth print-identity-token)
curl -H "Authorization: Bearer $TOKEN" \
    <service-url>/.well-known/agent-card.json
```

---

### Issue 2: "401 Unauthorized" (Cloud Run)

**Symptoms:**
- Inspector shows "401 Unauthorized"
- Works locally but not on Cloud Run

**Solutions:**

```bash
# 1. Regenerate token (tokens expire after 1 hour)
export TOKEN=$(gcloud auth print-identity-token)
echo $TOKEN

# 2. Verify you're authenticated
gcloud auth list

# 3. Check service IAM permissions
gcloud run services get-iam-policy brand-strategist \
    --region=us-central1

# 4. Add yourself as invoker if needed
gcloud run services add-iam-policy-binding brand-strategist \
    --region=us-central1 \
    --member="user:YOUR_EMAIL@gmail.com" \
    --role="roles/run.invoker"
```

---

### Issue 3: "Invalid Agent Card"

**Symptoms:**
- Inspector shows "Invalid agent card schema"
- Agent card JSON is malformed

**Solutions:**

```bash
# 1. Fetch and validate agent card JSON
curl http://localhost:8080/.well-known/agent-card.json | jq

# 2. Check required fields are present:
# Required: name, description, url

# 3. Validate JSON syntax
curl http://localhost:8080/.well-known/agent-card.json | python -m json.tool

# 4. Check agent.py configuration
# Ensure agent name matches agent card
```

---

### Issue 4: "No response from agent"

**Symptoms:**
- Inspector connects but agent doesn't respond to messages
- Hangs or times out

**Solutions:**

```bash
# 1. Check agent logs
# Local: Look at terminal output
# Cloud Run:
gcloud run services logs tail brand-strategist --region=us-central1

# 2. Verify agent model is working
# Check GOOGLE_API_KEY or GOOGLE_GENAI_USE_VERTEXAI

# 3. Test agent directly (bypass inspector)
# Send test request with curl:
curl -X POST http://localhost:8080/sessions \
    -H "Content-Type: application/json" \
    -d '{}'

# 4. Check for Python errors in agent code
# Look for import errors, missing dependencies
```

---

### Issue 5: Inspector won't start

**Symptoms:**
- `bash scripts/run.sh` fails
- Port conflicts

**Solutions:**

```bash
# 1. Check if ports are already in use
lsof -i :5001  # Inspector frontend
lsof -i :8000  # Inspector backend

# 2. Kill conflicting processes
kill -9 <PID>

# 3. Reinstall dependencies
cd ~/a2a-inspector
rm -rf node_modules frontend/node_modules
npm install
cd frontend && npm install

# 4. Try Docker instead
cd ~/a2a-inspector
docker build -t a2a-inspector .
docker run -p 5001:5001 a2a-inspector
```

---

### Issue 6: CORS Errors

**Symptoms:**
- Inspector shows CORS policy errors in browser console
- "Access-Control-Allow-Origin" errors

**Solutions:**

This shouldn't happen with the A2A protocol implementation, but if it does:

```bash
# 1. For local testing, use same-origin
# Inspector: http://localhost:5001
# Agent: http://localhost:8080

# 2. Check agent's CORS configuration
# ADK's to_a2a() handles CORS automatically

# 3. Try CLI inspector instead (no CORS issues)
npx @a2aproject/a2a-inspector inspect http://localhost:8080
```

---

## Quick Reference

### Common Commands

```bash
# Setup Inspector
cd agents/deploy && ./setup_inspector.sh

# Run Inspector
cd ~/a2a-inspector && bash scripts/run.sh

# Start Local Agent
cd agents/brand_strategist && python agent.py

# Get Cloud Run Token
export TOKEN=$(gcloud auth print-identity-token)

# CLI Validation (Local)
npx @a2aproject/a2a-inspector inspect http://localhost:8080

# CLI Validation (Cloud Run)
npx @a2aproject/a2a-inspector inspect \
    https://brand-strategist-xxxxx.run.app \
    --auth-header "Authorization: Bearer $TOKEN"

# Test Agent Card (Local)
curl http://localhost:8080/.well-known/agent-card.json | jq

# Test Agent Card (Cloud Run)
curl -H "Authorization: Bearer $TOKEN" \
    https://brand-strategist-xxxxx.run.app/.well-known/agent-card.json | jq
```

---

### Port Reference

| Service | Port | URL |
|---------|------|-----|
| Inspector Frontend | 5001 | http://localhost:5001 |
| Inspector Backend | 8000 | http://localhost:8000 |
| Brand Strategist | 8080 | http://localhost:8080 |
| Copywriter | 8081 | http://localhost:8081 |
| Designer | 8082 | http://localhost:8082 |
| Critic | 8083 | http://localhost:8083 |
| Project Manager | 8084 | http://localhost:8084 |

---

### Checklist: Before Deployment

Use this checklist to validate agents before deploying to Cloud Run:

- [ ] Agent starts without errors locally
- [ ] Agent card accessible at `/.well-known/agent-card.json`
- [ ] Agent card validates with inspector CLI
- [ ] Can create session via inspector UI
- [ ] Agent responds to test messages
- [ ] No Python errors in agent logs
- [ ] Environment variables correctly set
- [ ] All dependencies installed

If all checks pass ✅, deploy to Cloud Run!

---

## Additional Resources

- **A2A Protocol Spec**: https://github.com/google/A2A
- **A2A Inspector Repo**: https://github.com/a2aproject/a2a-inspector
- **Google ADK Docs**: https://google.github.io/adk-docs/
- **Cloud Run Docs**: https://cloud.google.com/run/docs

---

**Happy Testing! 🎉**
