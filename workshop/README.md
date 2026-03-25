# AI Creative Studio — Workshop

## GCP Cloud Shell Workshop Notebook

This directory contains the workshop materials for **Building a Multi-Agent AI Creative Studio with Google ADK and A2A Protocol**.

### How to Run

**Option 1 — GCP Cloud Shell (recommended)**

1. Open [console.cloud.google.com](https://console.cloud.google.com)
2. Click **Activate Cloud Shell** (`>_`) in the top toolbar
3. Click **Open Editor** → Upload `ai_creative_studio_workshop.ipynb`
4. Or clone the repo directly in Cloud Shell:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ai-creative-studio
   cd ai-creative-studio/workshop
   cloudshell edit ai_creative_studio_workshop.ipynb
   ```

**Option 2 — Google Colab**

1. Go to [colab.research.google.com](https://colab.research.google.com)
2. File → Open notebook → GitHub tab → paste the repo URL
3. Select `workshop/ai_creative_studio_workshop.ipynb`

### Prerequisites

- Google Cloud project with billing enabled
- Owner or Editor IAM role
- Gemini API key from [aistudio.google.com](https://aistudio.google.com/app/apikey)

### Workshop Duration

~2.5 hours (including deployment time)

### What You'll Build

A distributed multi-agent system with 6 AI agents:

| Agent | Role | Deployment |
|---|---|---|
| Brand Strategist | Market research + Google Search | Cloud Run |
| Copywriter | Instagram captions | Cloud Run |
| Designer | Imagen prompt generation | Cloud Run |
| Critic | Quality review loop | Cloud Run |
| Project Manager | Timeline + Notion MCP | Cloud Run |
| Creative Director | Orchestrator | Vertex AI Agent Engine |
