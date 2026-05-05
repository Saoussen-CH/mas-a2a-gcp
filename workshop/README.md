# AI Creative Studio — Workshop

## From Prompt to Production: Build a Complete Multi-Model AI Agent System on Google Cloud

This directory contains all the materials for the hands-on workshop codelab.

### Directory Structure

```
workshop/
├── index.lab.md            # Codelab source (claat Markdown format)
├── export.sh               # Regenerates docs/ from index.lab.md
├── inject_about.py         # Injects "About this codelab" card into index.html
├── diagrams/               # Screenshots and GIFs used in the codelab
├── starter/                # Starter code given to participants
│   ├── agents/             # Agent stubs with TODO comments
│   └── deploy/             # Deployment scripts
└── docs/                   # Published codelab (codelab.json + index.html)
```

### What Participants Build

A distributed multimodal multi-agent system for social media campaign generation:

| Agent | Platform | Role |
|---|---|---|
| Brand Strategist | Cloud Run | Market research with Google Search |
| Copywriter | Cloud Run | Instagram captions using ADK Skills |
| Designer | Cloud Run | Visual concepts + real image generation via Gemini |
| Critic | Cloud Run | Quality review and structured feedback |
| Project Manager | Cloud Run | Timeline, tasks, and Notion sync via MCP |
| Creative Director | Gemini Enterprise Agent Platform Runtime | Orchestrator — routes tasks via A2A |

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

### Build & Export the Codelab

```bash
# Install Go + claat (once)
sudo apt-get install golang-go
go install github.com/googlecodelabs/tools/claat@latest
export PATH=$PATH:$(go env GOPATH)/bin

# Export after every edit to index.lab.md
cd workshop
bash export.sh
```

Output is written to `docs/`. Commit `docs/` to publish via GitHub Pages.

### Starter Code

The `starter/` directory contains the code participants start from:

- Agent files have `# TODO` comments guiding participants through implementation
- Deploy scripts are fully functional — participants only implement agent logic
- Pre-written infrastructure includes retry config, error handling callbacks, and MCP toolset setup

### Publishing

See [PUBLISH.md](PUBLISH.md) for instructions on publishing to [codelabs.developers.google.com](https://codelabs.developers.google.com).
