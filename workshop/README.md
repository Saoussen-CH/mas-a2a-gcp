# AI Creative Studio — Workshop

## Google Codelab: Building a Multi-Agent AI Creative Studio with ADK and A2A

This directory contains all the materials for the hands-on workshop codelab.

### Directory Structure

```
workshop/
├── codelab.md              # Codelab source (claat Markdown format)
├── diagrams/               # Screenshots and GIFs used in the codelab
├── starter/                # Starter code given to participants
│   ├── agents/             # Agent stubs with TODO comments
│   └── deploy/             # Deployment scripts
├── ai-creative-studio-adk-a2a/   # Exported HTML codelab (generated)
├── PUBLISH.md              # Instructions for publishing to codelabs.developers.google.com
└── conference-submission.md
```

### What Participants Build

A distributed multi-agent system for social media campaign generation:

| Agent | Platform | Role |
|---|---|---|
| Brand Strategist | Cloud Run | Market research with Google Search |
| Copywriter | Cloud Run | Instagram posts and captions |
| Designer | Cloud Run | Image generation prompts |
| Critic | Cloud Run | Quality review and feedback |
| Project Manager | Cloud Run | Timeline and tasks via Notion MCP |
| Creative Director | Vertex AI Agent Engine | Orchestrator — routes tasks via A2A |

### Workshop Details

| | |
|---|---|
| **Duration** | ~2.5 hours |
| **Level** | Intermediate |
| **Environment** | GCP Cloud Shell |
| **Topics** | Google ADK, A2A Protocol, MCP, Cloud Run, Vertex AI Agent Engine |

### Prerequisites for Participants

- Google Cloud project with billing enabled
- Owner or Editor IAM role
- Gemini API key from [aistudio.google.com](https://aistudio.google.com/app/apikey)
- (Optional) Notion account for MCP integration

### Build & Serve the Codelab Locally

```bash
# Install claat
go install github.com/googlecodelabs/tools/claat@latest
# or download from https://github.com/googlecodelabs/tools/releases

# Export to HTML (run from workshop/ directory)
claat export codelab.md

# Serve locally
claat serve
# Opens: http://localhost:9090/ai-creative-studio-adk-a2a
```

### Starter Code

The `starter/` directory contains the code participants start from:

- Agent files have `# TODO` comments guiding participants through implementation
- Deploy scripts are fully functional — participants only implement agent logic
- A reference solution is in the root `agents/` directory

### Publishing

See [PUBLISH.md](PUBLISH.md) for instructions on publishing to [codelabs.developers.google.com](https://codelabs.developers.google.com).
