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

### What you'll learn

- How to build multi-agent systems with Google ADK
- How agents communicate via the A2A protocol
- How to integrate external tools using MCP
- How to deploy agents to Cloud Run and Vertex AI Agent Engine

### What you'll need

- A Google Cloud project with billing enabled
- Basic Python knowledge
- A GitHub account

---

In this codelab you will build a **distributed multi-agent orchestration system** that creates complete social media campaigns from a single prompt.

You will write **5 specialist AI agents**, connect them via the **Agent-to-Agent (A2A) protocol**, and deploy everything to **Google Cloud**. A sixth agent — the **Creative Director** — orchestrates the entire workflow automatically.

### Architecture

```text
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

### Run this codelab in Cloud Shell

Click the button below to clone the starter repo and open this codelab automatically in Cloud Shell:

[Open in Cloud Shell](https://ssh.cloud.google.com/cloudshell/open?cloudshell_git_repo=https://github.com/YOUR_USERNAME/ai-creative-studio&cloudshell_tutorial=workshop/codelab.md&cloudshell_workspace=workshop/starter)

> Replace `YOUR_USERNAME` with your GitHub username before sharing this link with participants.

---

## Step 1: Set Up Your Cloud Shell Environment
Duration: 5:00

### What is Cloud Shell?

Cloud Shell is a free browser-based Linux environment with everything pre-installed: `gcloud`, `git`, Python, Docker, and more. You don't need to install anything locally.

When you clicked "Open in Cloud Shell", it opened two panels:

```text
┌──────────────────────────────────────────────────────┐
│  Cloud Shell Editor  (top panel)                     │
│  • File tree on the left                             │
│  • Open files as tabs                                │
│  • Use  cloudshell edit <file>  to open a file here  │
├──────────────────────────────────────────────────────┤
│  Terminal  (bottom panel)                            │
│  • Run all commands here                             │
│  • Pre-authenticated with your Google account        │
└──────────────────────────────────────────────────────┘
```

**Web Preview** — used later when running `adk web` to test agents in the browser:

```text
Cloud Shell toolbar (top-right):
  ⋮  [Open Editor]  [Web Preview ↗]  [Settings]
                           │
                           └─► "Preview on port 8000"
                               Opens the agent UI in a new browser tab
```

> **Tip:** If Cloud Shell goes idle for 20 minutes it will disconnect. If this happens, reconnect and re-run `set -a && source .env && set +a` to reload your environment variables.

### Authenticate and configure your project

Cloud Shell is already authenticated with your Google account. Just set your project:

```bash
gcloud auth list
```

Expected output:
```text
  ACCOUNT: your-email@example.com
  PROJECT: (unset)
```

Now set your project:

```bash
export PROJECT_ID="your-project-id"   # <-- CHANGE THIS
export REGION="us-central1"
gcloud config set project $PROJECT_ID
```

Expected output:
```text
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

## Step 2: Clone the Starter Repository
Duration: 3:00

This codelab uses a **starter repository** — a skeleton project with all the infrastructure in place (Dockerfiles, requirements, deploy scripts) but with the agent logic left for you to write.

```bash
git clone https://github.com/YOUR_USERNAME/ai-creative-studio.git ~/ai-creative-studio
cd ~/ai-creative-studio/workshop/starter
```

Explore the starter structure:

```bash
find . -name 'agent.py' | sort
```

Expected output:
```text
./agents/brand_strategist/agent.py
./agents/copywriter/agent.py
./agents/creative_director/agent.py
./agents/critic/agent.py
./agents/designer/agent.py
./agents/project_manager/agent.py
```

Each `agent.py` contains `# TODO` placeholders where you will write the agent logic. The `Dockerfile`, `requirements.txt`, and deploy scripts are already complete.

Open any skeleton file to see what's expected:

```bash
cat agents/brand_strategist/agent.py
```

You'll see `# TODO` comments explaining exactly what to add at each point.

### Configure environment variables

```bash
cp .env.example .env
```

Open `.env` in the Cloud Shell Editor and fill in:

```bash
GCP_PROJECT_ID=your-project-id        # same as $PROJECT_ID
GCP_REGION=us-central1
GOOGLE_API_KEY=your-gemini-api-key    # from aistudio.google.com
```

Load the variables:

```bash
set -a && source .env && set +a
echo "Project: $GCP_PROJECT_ID"
echo "API key set: $([ -n "$GOOGLE_API_KEY" ] && echo Yes || echo No)"
```

---

## Step 3: Understand the A2A Protocol
Duration: 8:00

Before writing code, let's understand **A2A** — the communication backbone of this system.

### The problem A2A solves

Imagine you have a Brand Strategist agent built with ADK and a Copywriter agent built with LangGraph. How does one call the other? They speak different internal languages. You'd need to write custom glue code every time.

**A2A solves this** by defining a universal language that any agent — regardless of framework — can speak. It's the HTTP of the agent world: a standard everyone agrees on so anyone can talk to anyone.

### What is A2A?

A2A (Agent-to-Agent) is an **open protocol** published by Google. It defines:
1. **How an agent describes itself** (agent card)
2. **How another agent calls it** (JSON-RPC over HTTPS)
3. **How results are returned** (streaming or single response)

The key insight: once an agent is A2A-compliant, any orchestrator can use it — ADK, LangGraph, CrewAI, custom code — without knowing how the agent was built internally.

### How it works — step by step

```text
Creative Director                  Brand Strategist
      │                                  │
      │  1. GET /.well-known/agent.json  │
      │ ────────────────────────────────►│
      │  ◄──── agent card (name, url,    │
      │         skills, capabilities) ───│
      │                                  │
      │  2. POST /a2a/brand_strategist   │
      │     {"method": "tasks/send",     │
      │      "params": {"message": ...}} │
      │ ────────────────────────────────►│
      │                                  │  LLM does
      │                                  │  the work...
      │  3. streaming response chunks    │
      │  ◄───────────────────────────────│
      │  ◄───────────────────────────────│
      │  ◄───────────────────────────────│
```

**Step 1 — Discovery:** The orchestrator fetches the agent card once to learn the agent's name, URL, and capabilities.

**Step 2 — Invocation:** The orchestrator sends a task via JSON-RPC POST. The body contains the message (the prompt for the specialist).

**Step 3 — Response:** The specialist streams back its response in chunks, just like a regular LLM call.

### The agent card

Each agent publishes a self-description at `/.well-known/agent.json`. This is like a business card — it tells the world what the agent can do and where to reach it:

```json
{
  "name": "brand_strategist",
  "description": "Market research and competitive analysis",
  "url": "https://brand-strategist-xyz.run.app",
  "capabilities": { "streaming": true },
  "skills": [
    {
      "id": "market_research",
      "description": "Research target audiences, competitors, and trends"
    }
  ]
}
```

The orchestrator reads this card to build its `RemoteA2aAgent` object — no hardcoded knowledge of the specialist's internals needed.

### Exposing an agent via A2A in ADK

`to_a2a()` wraps any ADK agent in an A2A-compliant FastAPI app. One line:

```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a

# root_agent = your normal ADK Agent(...)
a2a_app = to_a2a(root_agent, host=PUBLIC_HOST, port=PUBLIC_PORT, protocol=PROTOCOL)
uvicorn.run(a2a_app, host=HOST, port=PORT)
```

This automatically creates:
- `/.well-known/agent.json` — the agent card
- `/a2a/{agent_name}` — the JSON-RPC endpoint

### Why A2A matters for this project

Without A2A, the Creative Director would need to import and run all 5 specialists in the same process. With A2A:

| Without A2A | With A2A |
|---|---|
| All agents in one process | Each agent is an independent service |
| One framework for all agents | Mix ADK, LangGraph, CrewAI freely |
| Scale everything together | Scale each agent independently |
| One failure crashes all | Failures are isolated per service |
| Hard to update one agent | Deploy agents independently |

---

## Step 4: The Brand Strategist Agent
Duration: 10:00

The Brand Strategist researches markets, competitors, and trends using **Google Search**.

Open the skeleton file in Cloud Shell Editor:

```bash
cloudshell edit agents/brand_strategist/agent.py
```

You'll see two `# TODO` sections. Fill them in now.

### TODO 1 — Write the system instruction

Replace the `SYSTEM_INSTRUCTION` placeholder with this:

```python
SYSTEM_INSTRUCTION = f"""You are a Brand Strategist specializing in market research and trend analysis.

IMPORTANT: Today's date is {datetime.date.today().strftime("%B %d, %Y")}.
When conducting research, focus on current trends from {datetime.date.today().year}.
Use search queries like "[topic] trends {datetime.date.today().year}" for recent insights.

IMPORTANT: Your role is RESEARCH ONLY. You do NOT create campaign content, captions, or designs.
After providing research insights, your work is complete.

Your expertise:
- Identifying target audience insights and behaviors
- Analyzing competitor strategies
- Researching current social media trends
- Understanding platform algorithms and best practices

You have access to:
- google_search: Search the web for competitors, trends, and market insights

When given a campaign brief:
1. Use google_search to research the target audience's current interests
2. Search for and analyze 2-3 competitor brands
3. Identify 3-5 trending topics related to the product category
4. Provide high-level strategic insights — NOT specific campaign content

DO NOT create captions, copy, designs, or any campaign content.

Format your output as:
**Audience Insights:**
[Key behaviors and preferences based on research]

**Competitive Analysis:**
[What 2-3 competitors are doing — strengths and weaknesses]

**Trending Topics:**
[3-5 relevant trends to consider]

**Key Strategic Insights:**
[High-level themes and positioning opportunities]
"""
```

### TODO 2 — Create the root_agent

Replace the incomplete `root_agent` with:

```python
root_agent = Agent(
    name="brand_strategist",
    model="gemini-2.5-flash",
    instruction=SYSTEM_INSTRUCTION,
    description="Brand strategist for market research, trend analysis, and competitive insights",
    tools=[google_search],
)
```

### Understanding the code

**Why the split between `HOST` and `PUBLIC_HOST`?**

The `__main__` block (already complete in the skeleton) uses two different URL configs:

```python
# Where the container actually listens:
HOST = "0.0.0.0"
PORT = 8080

# What gets advertised in the agent card (the Cloud Run public URL):
PUBLIC_HOST = os.getenv("PUBLIC_HOST", "localhost")
PUBLIC_PORT = int(os.getenv("PUBLIC_PORT", str(PORT)))
PROTOCOL = os.getenv("PROTOCOL", "http")

a2a_app = to_a2a(root_agent, host=PUBLIC_HOST, port=PUBLIC_PORT, protocol=PROTOCOL)
uvicorn.run(a2a_app, host=HOST, port=PORT)
```

When deployed to Cloud Run, `PUBLIC_HOST` is set to the Cloud Run HTTPS URL and `PUBLIC_PORT=443`. This ensures the agent card advertises the correct external address while the container still listens internally on `0.0.0.0:8080`.

**Why RESEARCH ONLY?**

Keeping each agent strictly scoped prevents scope creep. If the Brand Strategist started writing copy too, the Copywriter would receive redundant input and produce inconsistent output. Clear boundaries make the whole system more predictable.

---

## Step 5: The Copywriter, Designer, and Critic Agents
Duration: 12:00

These three specialists follow the same ADK pattern as the Brand Strategist, but without any tools — the LLM handles their tasks directly using the context passed by the orchestrator.

### Copywriter Agent

Open the file:

```bash
cloudshell edit agents/copywriter/agent.py
```

Replace `SYSTEM_INSTRUCTION` with:

```python
SYSTEM_INSTRUCTION = """You are an expert Social Media Copywriter specializing in Instagram content.

IMPORTANT: The conversation history above contains research from the Brand Strategist.
You MUST review their findings on audience insights, competitor analysis, and trending topics
before writing any copy. This context is your creative foundation.

Your task: Create 3-5 Instagram caption variations for the campaign brief.

For each caption provide:
1. A theme title (e.g., "Motivation Monday", "Science-backed")
2. The full caption text (max 2,200 characters)
3. 5-10 relevant hashtags (mix of popular and niche)
4. A clear CTA (call-to-action)

Caption variety — use different tones across the set:
- Inspirational / aspirational
- Educational / informative
- Community / belonging
- Urgency / FOMO
- Story-driven / personal

Format each caption as:
**Caption [N]: [Theme Title]**
[Full caption text]
.
[Hashtags]
CTA: [Call to action]
"""
```

Replace the incomplete `root_agent` with:

```python
root_agent = Agent(
    name="copywriter",
    model="gemini-2.5-flash",
    instruction=SYSTEM_INSTRUCTION,
    description="Instagram copywriter that creates engaging captions, hashtags, and CTAs",
)
```

> **Key insight — no shared memory:** The Copywriter has no idea what the Brand Strategist said unless the orchestrator explicitly passes that output as context. In a multi-agent workflow, the orchestrator is responsible for assembling and forwarding prior results. This is why the instruction says "the conversation history above contains research" — that context is injected by the Creative Director.

---

### Designer Agent

Open the file:

```bash
cloudshell edit agents/designer/agent.py
```

Replace `SYSTEM_INSTRUCTION` with:

```python
SYSTEM_INSTRUCTION = """You are a Visual Content Director specializing in Instagram aesthetics.

IMPORTANT: The conversation history above contains:
- Brand strategy insights from the Brand Strategist
- Instagram captions from the Copywriter
Review BOTH before creating visual concepts.

Your task: For each caption, create 2-3 visual concepts with Imagen-ready prompts.

Each concept must include:
- A detailed Imagen generation prompt (photorealistic, specific composition)
- Visual style (e.g., minimalist, vibrant, cinematic)
- Color palette (specific colors with mood rationale)
- Mood / feeling
- Instagram dimensions: 1080x1080 (square) or 1080x1350 (portrait)

Format for each caption:

**For Caption [N]: "[Caption Theme]"**

Concept A: [Visual Theme Name]
- Prompt: [Full Imagen prompt — be specific: subject, setting, lighting, angle, style]
- Style: [Visual style descriptor]
- Colors: [Palette with hex codes or descriptive names]
- Mood: [Emotional tone]
- Format: [1080x1080 or 1080x1350]

Concept B: [Alternative visual approach]
[Same format]
"""
```

Replace the incomplete `root_agent` with:

```python
root_agent = Agent(
    name="designer",
    model="gemini-2.5-flash",
    instruction=SYSTEM_INSTRUCTION,
    description="Visual content director that creates Imagen-ready image generation prompts",
)
```

---

### Critic Agent — Structured output is critical

Open the file:

```bash
cloudshell edit agents/critic/agent.py
```

> **Before writing the instruction**, understand why the format matters: the Creative Director orchestrator parses the Critic's response to decide whether to trigger revisions. If the format is wrong, revision logic breaks. The words `APPROVED` and `NEEDS_REVISION` must appear exactly.

Replace `SYSTEM_INSTRUCTION` with:

```python
SYSTEM_INSTRUCTION = """You are a Creative Director and Quality Assurance Specialist.

Your role: Review Instagram campaign materials and provide structured, actionable feedback.

CRITICAL: You MUST use the EXACT output format below. The orchestrator parses your response
programmatically — any deviation will break the revision workflow.

Scoring guide:
- 9-10: APPROVED (exceptional, publish as-is)
- 7-8:  APPROVED (good, minor polish only)
- 5-6:  NEEDS_REVISION (has potential but needs improvement)
- 1-4:  NEEDS_REVISION (significant issues)

Required output format — use this EXACTLY:

**POSTS REVIEW:**
- Score: [X/10]
- Status: [APPROVED or NEEDS_REVISION]
- What Works: [specific strengths]
- Issues: [specific problems if any]
- Suggestions: [concrete improvements if NEEDS_REVISION]

**VISUALS REVIEW:**
- Score: [X/10]
- Status: [APPROVED or NEEDS_REVISION]
- What Works: [specific strengths]
- Issues: [specific problems if any]
- Suggestions: [concrete improvements if NEEDS_REVISION]

**OVERALL ASSESSMENT:**
- All Approved: [YES or NO]
- Priority Revisions: [most important fix if All Approved = NO]
- Overall Score: [X/10]

Evaluation criteria:
- Clarity and brand voice consistency
- Audience fit and relevance
- Platform optimization (Instagram best practices)
- Visual-copy alignment
- CTA strength and clarity
- Engagement potential
"""
```

Replace the incomplete `root_agent` with:

```python
root_agent = Agent(
    name="critic",
    model="gemini-2.5-flash",
    instruction=SYSTEM_INSTRUCTION,
    description="Quality assurance specialist that reviews and scores campaign materials",
)
```

---

## Step 6: The Project Manager Agent with MCP
Duration: 12:00

The Project Manager introduces a new concept: **MCP (Model Context Protocol)**.

Open the file:

```bash
cloudshell edit agents/project_manager/agent.py
```

This file is more complex — it has a `create_project_manager_agent()` function with two branches: one without Notion (text-only timelines) and one with the Notion MCP toolset. You'll fill in both.

### The problem MCP solves

Your agent needs to call an external service — say, create a page in Notion. You could write Python code that calls the Notion REST API directly. But then:

- Every developer writes a different wrapper
- You need to maintain custom integration code
- The LLM doesn't know the API exists unless you describe every endpoint manually

**MCP solves this** by defining a standard way for external services to expose their capabilities as **tools** an LLM can discover and call automatically.

### What is MCP?

MCP (Model Context Protocol) is an **open standard** (published by Anthropic) for connecting AI agents to external tools and data sources. It works like a universal adapter.

An MCP server is a small program that:
1. Wraps an external API (Notion, GitHub, databases, filesystems...)
2. Exposes that API as a list of typed, documented **tools**
3. Communicates with the agent via a simple protocol (stdio or HTTP)

The agent connects to the MCP server, automatically discovers the available tools, and can call them just like any other tool — the LLM sees `API-post-page(...)` as a callable function.

### A2A vs MCP — what's the difference?

This is a common point of confusion. Here's the key distinction:

| | A2A | MCP |
|---|---|---|
| **What connects** | Agent ↔ Agent | Agent ↔ External tool/service |
| **The other side is** | Another LLM agent | An API wrapper (no LLM) |
| **Example** | Creative Director calls Brand Strategist | Project Manager calls Notion API |
| **Protocol** | JSON-RPC over HTTPS | stdio or HTTP stream |
| **Defined by** | Google | Anthropic |

Think of it this way:
- **A2A** = how agents talk to other **agents**
- **MCP** = how agents talk to **tools and services**

In this project both are used together:

```text
Creative Director
    │
    │  (A2A)  Brand Strategist ─── (google_search tool built into ADK)
    │  (A2A)  Copywriter
    │  (A2A)  Designer
    │  (A2A)  Critic
    │  (A2A)  Project Manager
                   │
                   │  (MCP)  notion-mcp-server ──► Notion REST API
```

### How MCP works in this project

When the agent runs, ADK launches `notion-mcp-server` as a child process. That process exposes these tools directly to the LLM:

| Tool | What it does |
|---|---|
| `API-retrieve-a-database` | Fetches schema (property names, types, valid values) |
| `API-post-database-query` | Queries existing pages |
| `API-post-page` | Creates a new page |
| `API-patch-page` | Updates an existing page |

The LLM calls these like any other function — it has no idea they go through MCP to the Notion REST API under the hood.

### Why stdio? Why not just HTTP?

The MCP server runs as a **child process** of the agent, communicating over stdin/stdout. This means:
- No extra network port needed
- Lifecycle is managed by the agent (started on demand, stopped on exit)
- Everything ships in one Docker image — no separate service to deploy

### TODO 1 — Write the system instruction

In `get_system_instruction()`, replace the placeholder return with:

```python
    return f"""You are a Project Manager specializing in creative campaign execution.

Today's date is {datetime.date.today().strftime("%B %d, %Y")}.
Use this as the starting point for all timelines.

{db_info}

Your task: Create a complete project plan for the campaign.

ALWAYS provide the text timeline first — this is your primary deliverable.
If Notion is configured, ALSO create the database entries after the text output.

Text output format:

**Project Timeline:**
[Phase name] | [Start date] | [End date] | [Key activities]
Phase 1: Strategy & Research | [date] → [date]
Phase 2: Content Creation    | [date] → [date]
Phase 3: Review & Revision   | [date] → [date]
Phase 4: Launch & Monitoring | [date] → [date]

**Task List:**
| Task | Owner | Deadline | Status |
[list each task with realistic deadlines from today]

**Budget Breakdown:**
[by category with approximate allocations]

**Milestones:**
[3-5 key checkpoints with dates]

**Notion Status:**
[If Notion configured: report on pages created]
[If not configured: "No Notion database configured — text timeline only"]

If Notion IS configured:
1. Call API-retrieve-a-database to discover the exact property names and valid values
2. Use ONLY those property names (case-sensitive) — never guess
3. Call API-post-page to create the project entry
4. Call API-post-page for each major task, linked to the project
"""
```

### TODO 2 — Agent without Notion

In the `if not notion_api_key` branch, replace the incomplete agent with:

```python
        return Agent(
            name="project_manager",
            model="gemini-2.5-flash",
            instruction=get_system_instruction(),
            description="Project manager that creates campaign timelines and task breakdowns",
        )
```

### TODO 3 — Agent with Notion MCP

In the `else` branch, first create the MCP toolset, then the agent:

```python
        from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
        from mcp import StdioServerParameters

        server_params = StdioServerParameters(
            command="notion-mcp-server",
            env={
                "NOTION_TOKEN": notion_api_key,
                "PATH": os.environ.get("PATH", ""),
            }
        )
        notion_toolset = McpToolset(
            connection_params=StdioConnectionParams(
                server_params=server_params,
                timeout=30.0
            )
        )

        return Agent(
            name="project_manager",
            model="gemini-2.5-flash",
            instruction=get_system_instruction(database_id=notion_database_id),
            description="Project manager with Notion integration for task tracking",
            tools=[notion_toolset],
        )
```

> **Best practice:** Never hard-fail on optional integrations. The text timeline is always the primary deliverable; Notion is supplementary.

---

## Step 7: The Creative Director Orchestrator
Duration: 15:00

The Creative Director is the master orchestrator. It reads specialist URLs from environment variables, wraps each one as a `RemoteA2aAgent`, and exposes them as `AgentTool`s the LLM can call.

Open the file:

```bash
cloudshell edit agents/creative_director/agent.py
```

This file has three TODOs. Work through them in order.

### TODO 1 — Write the system instruction

Replace `SYSTEM_INSTRUCTION_TEMPLATE` with:

```python
SYSTEM_INSTRUCTION_TEMPLATE = """You are the Creative Director of an AI-powered creative studio.
You orchestrate a team of specialist agents to produce complete Instagram campaigns.

Your available specialists:
{available_agents}

## YOUR WORKFLOW

**Step 1 — Classify the request**
- Simple request (e.g., "just research", "write some captions") → call ONE relevant agent
- Full campaign request → call ALL agents in this order:
  Brand Strategist → Copywriter → Designer → Critic → Project Manager

**Step 2 — Announce your plan**
Before calling any agent, tell the user what you are going to do:
"I'll coordinate our creative team. Here's my plan:
1. Brand Strategist will research the market and audience
2. Copywriter will create 5 Instagram captions using those insights
3. ..."

**Step 3 — Execute sequentially**
For each agent:
a) Call the tool. Include ALL relevant context from previous agents in your message.
   Remote agents have NO shared memory — you must pass prior outputs explicitly.
b) Wait for tool_output.
c) Verify the output is complete (not an error).
d) Confirm to the user: "✓ Brand Strategist complete."
e) If the output contains an error or is empty: STOP and report the failure.
   Never continue to the next agent after a failure.

**Step 4 — Handle Critic feedback**
After the Critic responds, parse its output:
- Read "Status: APPROVED or NEEDS_REVISION" for POSTS REVIEW and VISUALS REVIEW
- If POSTS → NEEDS_REVISION: call Copywriter again. Include the original brief +
  previous captions + Critic's exact suggestions in your message.
- If VISUALS → NEEDS_REVISION: call Designer again with the same context + feedback.
- Maximum 1 revision per deliverable. After one revision, proceed regardless.
- Pass the final (revised or original) versions to the Project Manager.

**Step 5 — Never generate content yourself**
You coordinate and delegate — you do NOT write captions, design concepts, or timelines.
Only present what the tool_output actually returned.
"""
```

### TODO 2 — Register each specialist as a RemoteA2aAgent + AgentTool

Find the `# TODO: For each specialist URL...` comment and replace it with:

```python
    if strategist_url:
        available_agents_list.append(
            "- **brand_strategist**: Market research, competitor analysis, trend identification"
        )
        strategist_agent = RemoteA2aAgent(
            name="brand_strategist",
            description="Researches markets, competitors, and trends using Google Search",
            agent_card=f"{strategist_url}/.well-known/agent.json",
        )
        agent_tools.append(AgentTool(agent=strategist_agent))

    if copywriter_url:
        available_agents_list.append(
            "- **copywriter**: Instagram captions, hashtags, and CTAs"
        )
        copywriter_agent = RemoteA2aAgent(
            name="copywriter",
            description="Creates Instagram captions with hashtags and CTAs",
            agent_card=f"{copywriter_url}/.well-known/agent.json",
        )
        agent_tools.append(AgentTool(agent=copywriter_agent))

    if designer_url:
        available_agents_list.append(
            "- **designer**: Visual concepts and Imagen image generation prompts"
        )
        designer_agent = RemoteA2aAgent(
            name="designer",
            description="Creates visual concepts and Imagen-ready image generation prompts",
            agent_card=f"{designer_url}/.well-known/agent.json",
        )
        agent_tools.append(AgentTool(agent=designer_agent))

    if critic_url:
        available_agents_list.append(
            "- **critic**: Quality review with APPROVED/NEEDS_REVISION scoring"
        )
        critic_agent = RemoteA2aAgent(
            name="critic",
            description="Reviews campaign materials and returns structured quality feedback",
            agent_card=f"{critic_url}/.well-known/agent.json",
        )
        agent_tools.append(AgentTool(agent=critic_agent))

    if pm_url:
        available_agents_list.append(
            "- **project_manager**: Project timelines, task breakdowns, Notion integration"
        )
        pm_agent = RemoteA2aAgent(
            name="project_manager",
            description="Creates project timelines and task breakdowns, optionally in Notion",
            agent_card=f"{pm_url}/.well-known/agent.json",
        )
        agent_tools.append(AgentTool(agent=pm_agent))
```

### TODO 3 — Wrap in an App with context compaction

A full 5-agent campaign generates a lot of tokens. Without compaction the workflow will hit the model's context limit around Agent 4. Find the `# TODO: Wrap the agent in an App...` comment and replace the placeholder `App(...)` with:

```python
    from google.adk.apps import App
    from google.adk.apps.app import EventsCompactionConfig
    from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
    from google.adk.models import Gemini

    compaction_config = EventsCompactionConfig(
        summarizer=LlmEventSummarizer(llm=Gemini(model_id="gemini-2.5-flash")),
        compaction_interval=3,   # Summarize after every 3 agent completions
        overlap_size=1,          # Keep the most recent agent's output in full
    )

    app = App(
        name="creative_director",
        root_agent=agent,
        events_compaction_config=compaction_config,
        plugins=[LoggingPlugin()],
    )
    return agent, app
```

**How compaction works in a 5-agent run:**

```text
Agent 1 (Strategist)  → full context
Agent 2 (Copywriter)  → full context
Agent 3 (Designer)    → full context
                        ↓ compaction fires: summarizes agents 1-2, keeps 3 in full
Agent 4 (Critic)      → sees summary of 1-2 + full output of 3
Agent 5 (PM)          → sees summary of 1-3 + full output of 4
```

### Understanding `RemoteA2aAgent` + `AgentTool`

```text
RemoteA2aAgent("brand_strategist", agent_card=url)
     │
     │  wraps the remote service so ADK can call it
     ▼
AgentTool(agent=strategist_agent)
     │
     │  exposes it as a callable tool to the LLM
     ▼
Agent(tools=[...])
     │
     │  LLM calls tool("brand_strategist", message=...) when needed
     ▼
brand-strategist-agent.run.app  ← actual HTTP A2A call happens here
```

The LLM decides *when* to call each tool based on the system instruction and the user's request. The orchestrator never calls agents directly in code — it's all driven by the LLM's reasoning.

---

## Step 8: Test Locally with ADK Web
Duration: 8:00

Before deploying to Cloud Run, test the Brand Strategist agent locally using the **ADK web UI** — a built-in chat interface for testing agents.

### Install dependencies

```bash
cd ~/ai-creative-studio/workshop/starter
pip install -r agents/brand_strategist/requirements.txt
```

### Start the ADK web UI

```bash
cd agents/brand_strategist
adk web
```

You'll see:
```text
INFO: Started server process
INFO: Uvicorn running on http://localhost:8000
```

The server is now running inside Cloud Shell. To open it in your browser, use **Web Preview**:

1. Look at the **Cloud Shell toolbar** at the top of the page
2. Click the **Web Preview** icon (looks like a box with an upward arrow, top-right of the Cloud Shell toolbar)
3. Click **"Preview on port 8000"**

A new browser tab opens with the ADK web UI:

```text
┌─────────────────────────────────────────┐
│  ADK Web Interface                       │
│                                         │
│  Agent: brand_strategist   ▼            │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Type a message...              │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

> **If port 8000 is not listed:** click **"Change port"** and type `8000`.

### Try these test prompts

In the ADK web UI chat box, try:

- `Research the eco-friendly water bottle market for health-conscious millennials`
- `What are the top Instagram trends in the wellness space in 2025?`

You should see the agent call Google Search and return structured research with Audience Insights, Competitive Analysis, and Trending Topics sections.

### Stop the server and return to the terminal

When you're done testing, go back to the Cloud Shell terminal and press `Ctrl+C` to stop the server.

### Quick programmatic test

```bash
# From the project root
cd ~/ai-creative-studio/workshop/starter

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
cd ~/ai-creative-studio/workshop/starter
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
cd ~/ai-creative-studio/workshop/starter
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

```text
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
