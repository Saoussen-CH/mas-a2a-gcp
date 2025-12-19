"""
A2A Server for Designer Agent
Exposes the agent via Agent-to-Agent protocol
"""

import os
from agent import create_designer_agent
from agent_to_a2a import to_a2a

# Create the designer agent
agent = create_designer_agent()

# Get configuration from environment
port = int(os.getenv("PORT", 8080))  # Internal container port for uvicorn
# PUBLIC_URL should be set by Cloud Run deployment (e.g., https://service-name-xxx.region.run.app)
public_url = os.getenv("PUBLIC_URL", "http://localhost:8080")

# Convert to A2A-compatible ASGI app
# Use custom to_a2a with public_url parameter for Cloud Run compatibility
app = to_a2a(agent, public_url=public_url)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
