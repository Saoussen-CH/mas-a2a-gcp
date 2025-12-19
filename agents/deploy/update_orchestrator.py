#!/usr/bin/env python3
"""
Update existing Creative Director Agent Engine with new code
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import vertexai
from vertexai import agent_engines

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv("../../.env")

PROJECT_ID = os.getenv("PROJECT_ID", "devfestahlen")
LOCATION = os.getenv("LOCATION", "us-central1")
RESOURCE_NAME = os.getenv("AGENT_ENGINE_RESOURCE_NAME")
STAGING_BUCKET = f"gs://{PROJECT_ID}-agent-staging"

# Agent URLs
COPYWRITER_URL = os.getenv("COPYWRITER_AGENT_URL", "")
DESIGNER_URL = os.getenv("DESIGNER_AGENT_URL", "")
STRATEGIST_URL = os.getenv("STRATEGIST_AGENT_URL", "")
CRITIC_URL = os.getenv("CRITIC_AGENT_URL", "")
PM_URL = os.getenv("PM_AGENT_URL", "")

print("=" * 70)
print("Updating Creative Director Agent Engine with New Code")
print("=" * 70)
print(f"\nProject: {PROJECT_ID}")
print(f"Location: {LOCATION}")
print(f"Resource: {RESOURCE_NAME}")
print()

if not RESOURCE_NAME:
    print("ERROR: AGENT_ENGINE_RESOURCE_NAME not set in .env")
    sys.exit(1)

# Initialize Vertex AI
vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)

# Import the agent
sys.path.insert(0, str(project_root / 'agents'))
from creative_director.agent import root_agent

print("⏳ Updating agent code on Agent Engine...")

# Wrap agent in AdkApp
adk_app = agent_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

# Update existing Agent Engine
agent_engine_id = RESOURCE_NAME.split("/")[-1]

remote_app = agent_engines.update(
    resource_name=RESOURCE_NAME,
    agent_engine=adk_app,
    requirements=[
        "google-cloud-aiplatform[agent_engines]>=1.112",
        "google-adk[a2a]==1.20.0",
        "google-genai>=1.51.0",
        "python-dotenv>=1.0.0",
    ],
    env_vars={
        "AGENT_ENGINE_ID": agent_engine_id,
        "COPYWRITER_AGENT_URL": COPYWRITER_URL,
        "DESIGNER_AGENT_URL": DESIGNER_URL,
        "STRATEGIST_AGENT_URL": STRATEGIST_URL,
        "CRITIC_AGENT_URL": CRITIC_URL,
        "PM_AGENT_URL": PM_URL,
    },
)

print("\n" + "=" * 70)
print("✅ AGENT ENGINE UPDATED SUCCESSFULLY!")
print("=" * 70)
print(f"\nResource: {RESOURCE_NAME}")
print(f"\nNew features:")
print("  ✓ Comprehensive logging for all agent calls and responses")
print("  ✓ Structured log data for analysis")
print("  ✓ Cloud Logging integration")
print()
print("View logs:")
print(f"  ./fetch_orchestrator_logs.sh")
print()
