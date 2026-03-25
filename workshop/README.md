# AI Creative Studio — Workshop

## Google Codelab: Building a Multi-Agent AI Creative Studio

This directory contains the source for the workshop codelab.

### Files

| File | Purpose |
|---|---|
| `codelab.md` | Codelab source in `claat` Markdown format |

### Build & Serve the Codelab

Install the `claat` tool and serve locally:

```bash
# Install claat
go install github.com/googlecodelabs/tools/claat@latest
# or download from https://github.com/googlecodelabs/tools/releases

# Export to HTML
claat export codelab.md

# Serve locally
claat serve
# Opens: http://localhost:9090/ai-creative-studio-adk-a2a
```

### Workshop Details

| | |
|---|---|
| **Duration** | ~2.5 hours |
| **Level** | Intermediate |
| **Environment** | GCP Cloud Shell |
| **Topics** | Google ADK, A2A Protocol, Cloud Run, Agent Engine, MCP |

### Prerequisites for Participants

- Google Cloud project with billing enabled
- Owner or Editor IAM role
- Gemini API key from [aistudio.google.com](https://aistudio.google.com/app/apikey)
