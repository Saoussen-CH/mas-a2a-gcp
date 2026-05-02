# AI Creative Studio - ADK Multi-Agent Workshop

A hands-on codelab for building a multi-agent AI system using **Google Agent Development Kit (ADK)** and **Agent-to-Agent (A2A)** protocol. Participants build a complete Instagram campaign generator from scratch, deploying five specialist agents that collaborate through A2A communication.

## What You Build

A multi-agent creative studio where specialized AI agents collaborate to produce full social media campaigns:

| Agent | Role |
|---|---|
| **Brand Strategist** | Market research, competitor analysis, audience insights |
| **Copywriter** | 3 Instagram caption variations using ADK Skills |
| **Designer** | Visual concepts + real image generation via Gemini |
| **Critic** | Quality review with structured APPROVED / NEEDS_REVISION scores |
| **Project Manager** | Campaign timeline, tasks, and optional Notion integration |

Coordinated by a **Creative Director** orchestrator that sequences the agents, handles errors, and compiles the final campaign.

## Key Concepts Covered

- Building ADK agents with tools, callbacks, and system instructions
- **ADK Skills** - packaging reusable knowledge into modular files loaded on demand
- **A2A protocol** - agents communicating over HTTP as independent services
- Multimodal image generation with Gemini and GCS upload
- MCP toolsets - connecting agents to external services (Notion)
- Deploying agents to Cloud Run and Agent Engine (Vertex AI)

## Repository Structure

```
workshop/
  starter/          ← participant starting point (TODOs to fill in)
    agents/
      brand_strategist/
      copywriter/         ← includes ADK Skills (instagram-copywriting)
      designer/           ← includes Gemini image generation tool
      critic/
      project_manager/    ← optional Notion MCP integration
      creative_director/  ← orchestrator
    deploy/         ← Cloud Run + Agent Engine deployment scripts
  docs/             ← published codelab (codelab.json + index.html)
```

## Prerequisites

- Google Cloud project with billing enabled
- APIs: Vertex AI, Cloud Run, Cloud Storage, Secret Manager
- `gcloud` CLI authenticated

## Getting Started

```bash
git clone https://github.com/Saoussen-CH/ai-creative-studio-adk-a2a-mcp-vertexai-cloudrun.git
cd workshop/starter
uv sync
cp .env.example .env
# Fill in .env with your project values
uv run adk web agents --allow_origins='*'
```

Full step-by-step instructions are in the published codelab.

## Tech Stack

- [Google ADK](https://adk.dev) `1.31.1`
- [A2A Protocol](https://github.com/google/A2A)
- Gemini 2.5 Flash (text) + Gemini image generation
- Cloud Run, Vertex AI Agent Engine, Cloud Storage
- MCP (Model Context Protocol) for Notion integration
