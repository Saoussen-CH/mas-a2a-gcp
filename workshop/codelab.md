summary: Building a Multi-Agent AI Creative Studio with Google ADK and A2A
id: ai-creative-studio-adk-a2a
categories: AI, Google Cloud, ADK
status: Published
authors: Saoussen Chaabnia
feedback link: https://github.com/YOUR_USERNAME/ai-creative-studio/issues
analytics account: UA-XXXXXXXXX-1

# Building a Multi-Agent AI Creative Studio with Google ADK and A2A

## Overview
Duration: 5:00

In this codelab you will build a **distributed multi-agent orchestration system** that creates complete social media campaigns from a single prompt.

You will write **5 specialist AI agents**, connect them via the **Agent-to-Agent (A2A) protocol**, and deploy everything to **Google Cloud**. A sixth agent — the **Creative Director** — orchestrates the entire workflow automatically.

### Architecture

```
                  ┌───────────────────────────────────────────┐
                  │        Vertex AI Agent Engine              │
  User ──────────►│         Creative Director                  │
                  │    (Orchestrator — delegates via A2A)      │
                  └───┬───────┬───────┬───────┬───────────────┘
                      │ A2A   │ A2A   │ A2A   │ A2A   │ A2A
                      ▼       ▼       ▼       ▼       ▼
              ┌──────────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌─────────┐
              │  Brand   │ │Copy- │ │Des-  │ │Critic│ │Project  │
              │Strategist│ │writer│ │igner │ │      │ │Manager  │
              │(+Search) │ │      │ │      │ │      │ │(+Notion)│
              └──────────┘ └──────┘ └──────┘ └──────┘ └─────────┘
               Cloud Run  Cloud Run Cloud Run Cloud Run Cloud Run
```

### What you'll learn

- Build LLM agents with **Google ADK** using `Agent`, tools, and system instructions
- Expose any agent as an **A2A (Agent-to-Agent) service** over HTTPS
- Orchestrate remote agents using `RemoteA2aAgent` + `AgentTool`
- Connect to external services with **MCP (Model Context Protocol)**
- Deploy containerized agents to **Cloud Run**
- Deploy the orchestrator to **Vertex AI Agent Engine**
- Handle long multi-agent workflows with **context compaction**
- Implement a **quality control loop** (Critic + automatic revision)

### What you'll need

- A **Google Cloud project** with billing enabled
- **Owner** or **Editor** IAM role
- A **Gemini API key** from [aistudio.google.com](https://aistudio.google.com/app/apikey)
- Basic Python knowledge

### Environment

> This codelab is designed for **GCP Cloud Shell**. All commands run directly in your browser — no local setup required.
>
> Open Cloud Shell: [console.cloud.google.com](https://console.cloud.google.com) → click **Activate Cloud Shell** (`>_`) in the top toolbar.

---

## Step 1: Set Up Your Environment
Duration: 5:00

### Authenticate and configure your project

Cloud Shell is pre-authenticated. Run these commands to configure your project:

```bash
# Confirm your active account
gcloud auth list

# Set your project
export PROJECT_ID="your-project-id"   # <-- CHANGE THIS
export REGION="us-central1"

gcloud config set project $PROJECT_ID
```

Expected output:
```
Updated property [core/project].
```

### Enable required GCP APIs

```bash
gcloud services enable \
    aiplatform.googleapis.com \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    generativelanguage.googleapis.com \
    iam.googleapis.com \
    cloudresourcemanager.googleapis.com
```

This takes about 2 minutes. You'll see `Operation finished successfully` when done.

---

## Step 2: Clone the Repository
Duration: 3:00

Clone the AI Creative Studio project to your Cloud Shell environment:

```bash
git clone https://github.com/YOUR_USERNAME/ai-creative-studio.git ~/ai-creative-studio
cd ~/ai-creative-studio
```

Explore the structure:

```bash
find . -name 'agent.py' | sort
```

Expected output:
```
./agents/brand_strategist/agent.py
./agents/copywriter/agent.py
./agents/creative_director/agent.py
./agents/critic/agent.py
./agents/designer/agent.py
./agents/project_manager/agent.py
```

Each agent is a self-contained Python service with its own `agent.py`, `requirements.txt`, and `Dockerfile`.

### Configure environment variables

```bash
cp .env.example .env
```

Open the `.env` file in the Cloud Shell Editor and fill in:

```bash
GCP_PROJECT_ID=your-project-id        # same as $PROJECT_ID
GCP_REGION=us-central1
GOOGLE_API_KEY=your-gemini-api-key    # from aistudio.google.com
```

Load the variables:

```bash
set -a && source .env && set +a
echo "Project: $GCP_PROJECT_ID"
echo "API key set: $([ -n '$GOOGLE_API_KEY' ] && echo Yes || echo No)"
```

---

## Step 3: Understand the A2A Protocol
Duration: 5:00

Before writing code, let's understand **A2A** — the communication backbone of this system.

### What is A2A?

The Agent-to-Agent (A2A) protocol is an open standard that lets AI agents from **any framework** communicate over HTTPS using JSON-RPC.

### Key concepts

**1. Agent Card** — Each agent self-describes at `/.well-known/agent.json`:

```json
{
  "name": "brand_strategist",
  "description": "Market research and competitive analysis",
  "url": "https://brand-strategist-xyz.run.app",
  "capabilities": { "streaming": true },
  "skills": [
    { "id": "market_research", "description": "Research markets and competitors" }
  ]
}
```

**2. Discovery** — The orchestrator fetches agent cards to learn what each agent can do.

**3. Invocation** — Agents communicate via JSON-RPC:

```bash
POST /a2a/brand_strategist
{
  "jsonrpc": "2.0",
  "method": "tasks/send",
  "params": {
    "message": {
      "role": "user",
      "parts": [{"text": "Research the eco-friendly water bottle market"}]
    }
  }
}
```

**4. ADK wrapping** — `to_a2a()` makes any ADK agent A2A-compliant in one line:

```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a

a2a_app = to_a2a(root_agent, host=PUBLIC_HOST, port=PUBLIC_PORT, protocol=PROTOCOL)
uvicorn.run(a2a_app, host=HOST, port=PORT)
```

### Why A2A?

| Benefit | Description |
|---|---|
| **Framework agnostic** | ADK, LangGraph, CrewAI agents all interoperate |
| **Discoverable** | Agents self-describe capabilities via agent cards |
| **Scalable** | Each agent is an independent HTTPS microservice |
| **Composable** | Mix and swap agents without changing the orchestrator |

---

## Step 4: The Brand Strategist Agent
Duration: 8:00

The Brand Strategist researches markets, competitors, and trends using **Google Search**.

Open the file:

```bash
cat agents/brand_strategist/agent.py
```

### Key code walkthrough

**1. Import the ADK Agent and Google Search tool:**

```python
from google.adk.agents import Agent
from google.adk.tools import google_search
```

**2. Define the agent with a focused system instruction:**

```python
root_agent = Agent(
    name="brand_strategist",
    model="gemini-2.5-flash",
    instruction=SYSTEM_INSTRUCTION,  # Defines role, output format, constraints
    description="Brand strategist for market research and competitive insights",
    tools=[google_search],           # Built-in Google Search tool
)
```

**3. Expose as A2A service in `__main__`:**

```python
# Two different URL configs:
# HOST/PORT      = where the container listens (e.g., 0.0.0.0:8080)
# PUBLIC_HOST/PORT = what the agent card advertises (e.g., Cloud Run URL on :443)

a2a_app = to_a2a(root_agent, host=PUBLIC_HOST, port=PUBLIC_PORT, protocol=PROTOCOL)
uvicorn.run(a2a_app, host=HOST, port=PORT)
```

> **Note:** The split between `HOST` (listen address) and `PUBLIC_HOST` (advertised address) is critical for Cloud Run. The container listens on `0.0.0.0:8080` but the agent card must advertise the public HTTPS URL.

### System instruction design

The Brand Strategist's instruction enforces strict boundaries:

```
DO NOT:
- Create captions, copy, or specific messaging
- Generate image concepts or designs
- Write TikTok scripts or Instagram posts

Your job is RESEARCH ONLY.
```

This keeps agents focused and prevents scope creep in multi-agent workflows.

---

## Step 5: The Copywriter, Designer, and Critic Agents
Duration: 10:00

The remaining three specialist agents follow the same pattern — no tools needed, just a well-crafted system instruction.

### Copywriter Agent

```bash
cat agents/copywriter/agent.py
```

The Copywriter reads prior context explicitly passed by the orchestrator:

```
IMPORTANT: You will receive strategic insights from the Brand Strategist
in the conversation history above. Review their research on audience insights,
competitive analysis, and trending topics to inform your copy.
```

> **Key insight:** Agents don't share memory. The orchestrator explicitly includes the Brand Strategist's output in the Copywriter's prompt. This is the standard pattern for sequential agent workflows.

### Designer Agent

```bash
cat agents/designer/agent.py
```

The Designer creates **Imagen-ready prompts** for each caption:

```
Format:
For Caption 1: "Every sip saves the planet"
Concept A: Minimalist Nature
  Prompt: Product shot against lush forest backdrop, morning mist,
          golden hour lighting, 1080x1080, photorealistic...
  Colors: Earth tones (forest green, warm brown, cream)
  Mood:   Serene, aspirational
```

In production these prompts feed directly into the Vertex AI Imagen API.

### Critic Agent — Structured output for machine-readable parsing

```bash
cat agents/critic/agent.py
```

The Critic uses a strict format that the orchestrator can parse programmatically:

```
POSTS REVIEW:
- Score: 6/10
- Status: NEEDS_REVISION    ← Orchestrator reads this field
- Suggestions: Strengthen CTAs, more professional tone

VISUALS REVIEW:
- Score: 8/10
- Status: APPROVED          ← Orchestrator skips designer revision

OVERALL ASSESSMENT:
- All Approved: NO          ← Triggers copywriter revision cycle
```

**Scoring guide:**

| Score | Status | Action |
|---|---|---|
| 9–10 | APPROVED | Publish as-is |
| 7–8 | APPROVED | Minor issues, acceptable |
| 5–6 | NEEDS_REVISION | Improve before proceeding |
| 1–4 | NEEDS_REVISION | Significant issues |

---

## Step 6: The Project Manager Agent with MCP
Duration: 8:00

The Project Manager introduces a new ADK concept: **MCP (Model Context Protocol)**.

```bash
cat agents/project_manager/agent.py
```

### What is MCP?

MCP lets agents connect to external services via **stdio servers** that expose tools the LLM can call. Think of it as a plugin system for agents.

### Notion MCP integration

```python
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

# Connect to the Notion MCP server via stdio
server_params = StdioServerParameters(
    command="notion-mcp-server",          # Installed in Dockerfile
    env={"NOTION_TOKEN": notion_api_key}
)

notion_toolset = McpToolset(
    connection_params=StdioConnectionParams(server_params=server_params)
)

# Agent automatically gets Notion API tools!
agent = Agent(
    name="project_manager",
    model="gemini-2.5-flash",
    instruction=get_system_instruction(database_id=notion_database_id),
    tools=[notion_toolset],
)
```

The Notion MCP server exposes these tools directly to the LLM:
- `API-retrieve-a-database` — discover database schema
- `API-post-page` — create pages
- `API-patch-page` — update pages
- `API-post-database-query` — query existing data

### Graceful degradation

```python
if not notion_api_key or not notion_database_id:
    # Create agent without Notion tools — still creates text timelines
    agent = Agent(name="project_manager", ...)
else:
    # Create agent with Notion MCP tools
    agent = Agent(name="project_manager", tools=[notion_toolset], ...)
```

> **Best practice:** Never hard-fail on optional integrations. The text timeline is always the primary deliverable; Notion is supplementary.

---

## Step 7: The Creative Director Orchestrator
Duration: 10:00

The Creative Director is the master orchestrator. It uses `RemoteA2aAgent` + `AgentTool` to delegate to specialists.

```bash
cat agents/creative_director/agent.py
```

### The `RemoteA2aAgent` + `AgentTool` pattern

```python
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.tools.agent_tool import AgentTool

# 1. Wrap a remote A2A service as a local agent object
strategist_agent = RemoteA2aAgent(
    name="brand_strategist",
    description="Market research and competitive insights",
    agent_card=f"{strategist_url}/.well-known/agent.json",  # Discover via agent card
)

# 2. Convert it to a tool the LLM can call
agent_tools.append(AgentTool(agent=strategist_agent))

# 3. Orchestrator decides when to call each tool based on the user request
orchestrator = Agent(
    name="creative_director",
    model="gemini-2.5-flash",
    instruction=system_instruction,   # Routing logic in the prompt
    tools=agent_tools,                # All 5 specialist tools
)
```

### Context compaction for long workflows

A 5-agent workflow accumulates a lot of tokens. ADK's `EventsCompactionConfig` handles this:

```python
from google.adk.apps import App
from google.adk.apps.app import EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer

compaction_config = EventsCompactionConfig(
    summarizer=LlmEventSummarizer(llm=Gemini(model_id="gemini-2.5-flash")),
    compaction_interval=3,   # Summarize after every 3 completed agents
    overlap_size=1,          # Keep the last agent's output in full
)

app = App(
    name="creative_director",
    root_agent=agent,
    events_compaction_config=compaction_config,
    plugins=[LoggingPlugin()],
)
```

For a 5-agent workflow:
- **Agents 1–3:** Full context preserved
- **After Agent 3:** Agents 1–2 summarized, Agent 3 kept in full
- **Agents 4–5:** See full recent context + summarized older context

### The revision loop

The orchestrator parses the Critic's structured output and triggers revisions automatically:

```
Critic says:  POSTS: NEEDS_REVISION → call Copywriter again with feedback
              VISUALS: APPROVED     → skip designer, proceed to PM
```

Maximum **1 revision per deliverable** prevents infinite loops and runaway costs.

---

## Step 8: Test Locally with ADK Web
Duration: 5:00

Before deploying to Cloud Run, test agents locally using the ADK web interface.

### Install dependencies

```bash
cd ~/ai-creative-studio
pip install -r agents/brand_strategist/requirements.txt
```

### Start ADK web UI for the Brand Strategist

```bash
cd agents/brand_strategist
adk web
```

In Cloud Shell, click **Web Preview** → **Preview on port 8000** to open the ADK UI in your browser.

Try these test prompts:
- `"Research the eco-friendly water bottle market for health-conscious millennials"`
- `"What are the top Instagram trends in the wellness space?"`

### Quick programmatic test

```bash
# From the project root
cd ~/ai-creative-studio

python3 - <<'EOF'
import asyncio, os, sys
sys.path.insert(0, "agents/brand_strategist")
os.chdir("agents/brand_strategist")

from dotenv import load_dotenv
load_dotenv("../../.env")

from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agent import root_agent

async def test():
    svc = InMemorySessionService()
    runner = Runner(app_name="test", agent=root_agent, session_service=svc)
    await svc.create_session(app_name="test", user_id="u1", session_id="s1")

    async for event in runner.run_async(
        user_id="u1", session_id="s1",
        new_message=types.Content(parts=[types.Part(
            text="In 3 bullet points, what are the top Instagram trends for eco-friendly brands in 2025?"
        )])
    ):
        if hasattr(event, "content") and event.content:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    print(part.text, end="", flush=True)
    await runner.close()

asyncio.run(test())
EOF
```

Expected output: A brief market research response with audience insights, competitor examples, and trending topics.

---

## Step 9: Deploy Specialists to Cloud Run
Duration: 15:00

Each specialist agent is deployed as an independent Cloud Run service. Cloud Run automatically builds a Docker container from source using Cloud Build.

### Deployment configuration

The `Dockerfile` for each specialist follows this pattern:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc curl

# Fast dependency install with uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

COPY . .
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

ENV PYTHONUNBUFFERED=1 PORT=8080 HOST=0.0.0.0
EXPOSE 8080
CMD ["python", "agent.py"]
```

### Deploy all 5 specialists in parallel

```bash
cd ~/ai-creative-studio
source .env

python deploy/deploy_all_specialists.py
```

This script deploys all 5 agents concurrently (~5–8 minutes total). When complete, it writes each agent's URL back to `.env`.

### What gets deployed per service

```bash
# Each service is deployed with these env vars:
gcloud run deploy brand-strategist-agent \
    --source agents/brand_strategist \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars "GOOGLE_API_KEY=${GOOGLE_API_KEY},PROTOCOL=https,PUBLIC_PORT=443"
```

The `PROTOCOL=https` and `PUBLIC_PORT=443` tell the agent to advertise its Cloud Run HTTPS URL in its agent card.

### Verify deployments

```bash
source .env

echo "Deployed URLs:"
echo "  Brand Strategist: $STRATEGIST_AGENT_URL"
echo "  Copywriter:       $COPYWRITER_AGENT_URL"
echo "  Designer:         $DESIGNER_AGENT_URL"
echo "  Critic:           $CRITIC_AGENT_URL"
echo "  Project Manager:  $PM_AGENT_URL"
```

---

## Step 10: Verify Agent Cards
Duration: 5:00

Each deployed agent exposes an agent card at `/.well-known/agent.json`. Fetch them to confirm everything is live:

```bash
source .env

for agent_url in $STRATEGIST_AGENT_URL $COPYWRITER_AGENT_URL $DESIGNER_AGENT_URL $CRITIC_AGENT_URL $PM_AGENT_URL; do
    echo "=== Agent Card: $agent_url ==="
    curl -s "${agent_url}/.well-known/agent.json" | python3 -m json.tool | grep -E '"name"|"url"|"description"'
    echo ""
done
```

Expected output for each agent:
```json
"name": "brand_strategist",
"url": "https://brand-strategist-agent-xxxx.run.app",
"description": "Brand strategist for market research and competitive insights"
```

### Quick A2A smoke test

Send a direct A2A message to the Brand Strategist:

```bash
source .env

curl -s -X POST "${STRATEGIST_AGENT_URL}/a2a/brand_strategist" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tasks/send",
    "id": "smoke-test-1",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"text": "In one sentence, describe what you do."}]
      }
    }
  }' | python3 -c "
import sys, json
r = json.load(sys.stdin)
parts = r.get('result', {}).get('status', {}).get('message', {}).get('parts', [])
for p in parts:
    if 'text' in p:
        print(p['text'])
"
```

---

## Step 11: Deploy the Creative Director to Agent Engine
Duration: 10:00

The orchestrator is deployed to **Vertex AI Agent Engine**, which provides managed session state, automatic scaling, and built-in tracing.

### How the deployment works

```python
import vertexai
from vertexai.preview import reasoning_engines

vertexai.init(project=PROJECT_ID, location=REGION)

# Package the App (not Agent — App has compaction + logging config)
remote_app = reasoning_engines.ReasoningEngine.create(
    reasoning_engines.AdkApp(app=root_app, enable_tracing=True),
    requirements=[
        "google-adk[a2a]==1.20.0",
        "google-genai>=1.51.0",
        "uvicorn[standard]>=0.25.0",
        "python-dotenv>=1.0.0",
    ],
    display_name="Creative Director",
)
```

### Verify specialist URLs before deploying

All 5 specialist URLs must be set before the orchestrator can connect to them:

```bash
source .env

for var in STRATEGIST_AGENT_URL COPYWRITER_AGENT_URL DESIGNER_AGENT_URL CRITIC_AGENT_URL PM_AGENT_URL; do
    val=$(eval echo "\$$var")
    if [ -z "$val" ]; then
        echo "MISSING: $var — complete Step 9 first"
    else
        echo "OK: $var"
    fi
done
```

### Deploy the orchestrator

```bash
cd ~/ai-creative-studio
source .env

python deploy/deploy_orchestrator.py --action deploy
```

This takes ~5–10 minutes. When complete, the `AGENT_ENGINE_ID` and `AGENT_ENGINE_RESOURCE_NAME` are saved to `.env`.

```bash
source .env
echo "Agent Engine ID: $AGENT_ENGINE_ID"
echo "Resource: $AGENT_ENGINE_RESOURCE_NAME"
```

---

## Step 12: Run an End-to-End Campaign
Duration: 10:00

The entire system is deployed. Let's create a complete campaign!

### Connect to Agent Engine

```python
import vertexai
from vertexai.preview import reasoning_engines
from dotenv import load_dotenv
import os

load_dotenv()

vertexai.init(
    project=os.getenv("PROJECT_ID"),
    location=os.getenv("LOCATION", "us-central1")
)

agent_engine = reasoning_engines.ReasoningEngine(
    f"projects/{os.getenv('PROJECT_ID')}/locations/us-central1/"
    f"reasoningEngines/{os.getenv('AGENT_ENGINE_ID')}"
)

session = agent_engine.create_session(user_id="workshop-user")
print(f"Session: {session['id']}")
```

### Send a full campaign brief

```python
campaign_brief = """
Create a complete Instagram campaign for:
- Product: EcoFlow Smart Water Bottle (tracks hydration, keeps drinks cold 24h)
- Target Audience: Health-conscious millennials, 25-35 years old
- Platform: Instagram
- Goal: Brand awareness + drive website traffic
- Brand Voice: Motivational, clean, science-backed
- Budget: $3,000
- Timeline: Launch in 2 weeks
"""

for event in agent_engine.stream_query(
    user_id="workshop-user",
    session_id=session["id"],
    message=campaign_brief,
):
    if "content" in event and "parts" in event["content"]:
        for part in event["content"]["parts"]:
            if "text" in part:
                print(part["text"], end="", flush=True)
```

The Creative Director will:
1. Announce its plan (5 steps)
2. Call Brand Strategist → confirm with "✓ Research complete"
3. Call Copywriter with strategist insights → confirm
4. Call Designer with copy → confirm
5. Call Critic → check for NEEDS_REVISION
6. (If needed) Revise copy or visuals
7. Call Project Manager → confirm
8. Present the complete campaign

### Test single-agent routing

```python
single_session = agent_engine.create_session(user_id="workshop-user")

for event in agent_engine.stream_query(
    user_id="workshop-user",
    session_id=single_session["id"],
    message="Research the luxury skincare market — top brands and trends in 2025",
):
    if "content" in event and "parts" in event["content"]:
        for part in event["content"]["parts"]:
            if "text" in part:
                print(part["text"], end="", flush=True)
```

Notice the Creative Director routes this to **only the Brand Strategist** — no Copywriter, Designer, Critic, or PM.

---

## Step 13: Observe the System in Action
Duration: 5:00

### View Cloud Run logs

While a campaign is running, stream logs from the Brand Strategist:

```bash
gcloud logging read \
    'resource.type="cloud_run_revision" AND resource.labels.service_name="brand-strategist-agent"' \
    --limit=20 \
    --format='value(timestamp, textPayload)' \
    --freshness=10m
```

### View deployed Cloud Run services

```bash
gcloud run services list \
    --region=us-central1 \
    --format='table(metadata.name,status.url,status.conditions[0].status)'
```

### Inspect Agent Engine tracing

1. Go to [console.cloud.google.com/vertex-ai/agents](https://console.cloud.google.com/vertex-ai/agents)
2. Select your Agent Engine
3. Click **Traces** to see the full execution tree of each campaign run

You'll see each agent call, its inputs/outputs, latency, and token usage.

---

## Step 14: (Optional) Enable Notion Integration
Duration: 10:00

Enable the Project Manager to create tasks directly in Notion.

### Set up a Notion integration

1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click **New Integration** → name it `AI Creative Studio`
3. Copy the **Internal Integration Token** (`ntn_...`)
4. Create TWO databases in Notion:

   **Projects database** (required properties):
   - Title property (e.g., "Project name")
   - Status property
   - Date range property (e.g., "Timeline")

   **Tasks database** (required properties):
   - Title property (e.g., "Task name")
   - Status property
   - Date property (e.g., "Due")
   - Relation property linked to Projects database

5. Share both databases with your integration (Share → Invite)
6. Copy the Projects database ID from the URL: `notion.so/{workspace}/{DATABASE_ID}?v=...`

### Add credentials to .env

```bash
echo "NOTION_API_KEY=ntn_your-token" >> .env      # <-- replace
echo "NOTION_DATABASE_ID=your-db-id" >> .env       # <-- replace
```

### Redeploy Project Manager with Notion

```bash
source .env

gcloud run deploy project-manager-agent \
    --source agents/project_manager \
    --region us-central1 \
    --allow-unauthenticated \
    --update-env-vars "NOTION_API_KEY=${NOTION_API_KEY},NOTION_DATABASE_ID=${NOTION_DATABASE_ID}"

echo "Project Manager redeployed with Notion!"
```

Run a new campaign and check your Notion workspace — a project and tasks will appear automatically.

### How schema discovery works

The Project Manager uses **dynamic schema discovery** — it never hardcodes Notion property names:

```
Step 1: Call API-retrieve-a-database to discover exact property names
Step 2: Read the "properties" object in the response
Step 3: Use ONLY discovered property names (case-sensitive) in API calls
Step 4: For select/status fields, use only values from the options array
```

This means the agent adapts to any Notion database structure automatically.

---

## Step 15: Clean Up
Duration: 5:00

Clean up GCP resources to avoid ongoing charges.

### Delete Cloud Run services

```bash
REGION="us-central1"

for svc in brand-strategist-agent copywriter-agent designer-agent critic-agent project-manager-agent; do
    gcloud run services delete $svc \
        --region=$REGION \
        --quiet \
        && echo "Deleted: $svc" \
        || echo "Not found: $svc"
done
```

### Delete the Agent Engine

```bash
source .env

python deploy/deploy_orchestrator.py --action cleanup
```

### Verify everything is removed

```bash
gcloud run services list --region=us-central1
```

Expected output: an empty list or only your own services.

---

## Summary
Duration: 2:00

Congratulations! You've built and deployed a **production-grade multi-agent AI system** on Google Cloud.

### What you built

| Agent | Capability | Deployment |
|---|---|---|
| Brand Strategist | Market research via Google Search | Cloud Run |
| Copywriter | Instagram caption creation | Cloud Run |
| Designer | Imagen prompt generation | Cloud Run |
| Critic | Quality review with scoring | Cloud Run |
| Project Manager | Timeline + Notion MCP | Cloud Run |
| Creative Director | Full orchestration via A2A | Vertex AI Agent Engine |

### Key patterns you learned

1. **ADK `Agent`** — define an LLM agent with an instruction + optional tools
2. **`to_a2a()`** — expose any ADK agent as an A2A-compliant HTTPS service
3. **`RemoteA2aAgent` + `AgentTool`** — orchestrate remote agents as callable tools
4. **`McpToolset`** — connect to external services via MCP stdio servers
5. **`EventsCompactionConfig`** — handle token limits in long multi-agent workflows
6. **Structured critic output** — machine-readable quality control with automatic revision
7. **Cloud Run** — deploy containerized agents at scale
8. **Vertex AI Agent Engine** — host orchestrators with managed sessions and tracing

### Next steps

- Add **Imagen API** calls to the Designer to generate actual images
- Add **IAM authentication** to Cloud Run services (remove `--allow-unauthenticated`)
- Replace one specialist with a **LangGraph or CrewAI** agent — A2A is framework agnostic
- Add **user feedback** as a tool so participants can rate and iterate on outputs
- Explore **Vertex AI Agent Engine tracing** in the Cloud Console

### Resources

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [A2A Protocol Specification](https://google.github.io/A2A/)
- [Vertex AI Agent Engine Docs](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
- [ADK Codelabs](https://codelabs.developers.google.com/?cat=aiml&text=adk)
