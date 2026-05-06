# AI Creative Studio: Workshop

## Build a Multi-Agent Creative Studio with Google's Agent Stack: ADK, A2A, MCP on Cloud Run & Agent Runtime

This directory contains all the materials for the hands-on workshop codelab.

### Directory Structure

```
workshop/
├── diagrams/               # Screenshots and GIFs used in the codelab
├── starter/                # Starter code given to participants
│   ├── agents/             # Agent stubs with TODO comments
│   └── deploy/             # Deployment scripts
└── docs/                   # Published codelab (codelab.json + index.html)
```

### What Participants Build

A distributed multimodal multi-agent system for Instagram campaign generation:

| Agent | Platform | Role |
|---|---|---|
| Brand Strategist | Cloud Run | Market research with Google Search |
| Copywriter | Cloud Run | Instagram captions using ADK Skills |
| Designer | Cloud Run | Visual concepts + real image generation via Gemini |
| Critic | Cloud Run | Quality review and structured feedback |
| Project Manager | Cloud Run | Timeline, tasks, and Notion sync via MCP |
| Creative Director | Gemini Enterprise Agent Platform Runtime | Orchestrator that routes tasks via A2A |

### Workshop Details

| | |
|---|---|
| **Duration** | ~2.5 hours |
| **Level** | Intermediate |
| **Environment** | GCP Cloud Shell |
| **Topics** | Google ADK, ADK Skills, A2A Protocol, MCP, Multimodal, Cloud Run, Gemini Enterprise Agent Platform Runtime |

### Prerequisites for Participants

- Google Cloud project with billing enabled
- Owner or Editor IAM role
- (Optional) Notion account for MCP integration

### Starter Code

The `starter/` directory contains the code participants start from:

- Agent files have numbered `# TODO` comments guiding participants through each implementation step
- Deploy scripts are fully functional — participants only implement agent logic
- Pre-written infrastructure includes retry config, error handling callbacks, and MCP toolset setup

### Published Codelab

The official codelab is published at [codelabs.developers.google.com/ai-creative-studio-adk-a2a](https://codelabs.developers.google.com/ai-creative-studio-adk-a2a).

The `docs/` directory is the GitHub Pages source. Commit changes there to publish updates.
