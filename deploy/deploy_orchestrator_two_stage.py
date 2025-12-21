#!/usr/bin/env python3
"""
Two-Stage Deployment for Creative Director Agent Engine
========================================================
This approach:
1. Creates Agent Engine resource first (gets ID)
2. Deploys agent code with environment variables

This allows the agent to access AGENT_ENGINE_ID and other runtime config.

Usage:
    # Deploy Agent Engine
    python3 deploy_orchestrator_two_stage.py --action deploy

    # Test deployment
    python3 deploy_orchestrator_two_stage.py --action test --resource_name <resource_name>

    # Cleanup (delete Agent Engine)
    python3 deploy_orchestrator_two_stage.py --action cleanup --resource_name <resource_name>
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import vertexai
from vertexai import agent_engines, Client

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

# Configuration - support both LOCATION and REGION naming conventions
PROJECT_ID = os.getenv("PROJECT_ID", "devfestahlen")
LOCATION = os.getenv("LOCATION") or os.getenv("REGION", "us-central1")
STAGING_BUCKET = f"gs://{PROJECT_ID}-agent-staging"
DISPLAY_NAME = "Creative Director"

# Agent URLs
COPYWRITER_URL = os.getenv("COPYWRITER_AGENT_URL", "")
DESIGNER_URL = os.getenv("DESIGNER_AGENT_URL", "")
STRATEGIST_URL = os.getenv("STRATEGIST_AGENT_URL", "")
CRITIC_URL = os.getenv("CRITIC_AGENT_URL", "")
PM_URL = os.getenv("PM_AGENT_URL", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")


def init_vertex_ai():
    """Initialize Vertex AI SDK."""
    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=STAGING_BUCKET,
    )
    print(f"✓ Initialized Vertex AI")
    print(f"  Project: {PROJECT_ID}")
    print(f"  Location: {LOCATION}")
    print(f"  Staging: {STAGING_BUCKET}")


def deploy_two_stage(auto_deploy_specialists=False):
    """Deploy using two-stage approach.

    Args:
        auto_deploy_specialists: If True, deploy all specialist agents first
    """

    # NEW: Auto-deploy specialists first if requested
    if auto_deploy_specialists:
        print("\n" + "=" * 70)
        print("AUTO-DEPLOY: Deploying all specialist agents first...")
        print("=" * 70)

        # Import specialist deployment module
        sys.path.insert(0, str(project_root / 'agents' / 'common'))
        from deploy_all_specialists import deploy_all_agents
        import env_utils

        # Run specialist deployment
        print("\n⏳ Deploying all 5 specialist agents to Cloud Run...")
        agent_urls = asyncio.run(deploy_all_agents(PROJECT_ID, LOCATION))

        if not agent_urls:
            print("\n❌ ERROR: Failed to deploy specialist agents")
            print("   Cannot proceed with orchestrator deployment without agent URLs")
            sys.exit(1)

        # Update global environment variables with collected URLs
        env_vars_update = env_utils.format_env_vars_for_orchestrator(agent_urls)
        os.environ.update(env_vars_update)

        # Also update the module-level variables
        global COPYWRITER_URL, DESIGNER_URL, STRATEGIST_URL, CRITIC_URL, PM_URL
        COPYWRITER_URL = env_vars_update.get("COPYWRITER_AGENT_URL", "")
        DESIGNER_URL = env_vars_update.get("DESIGNER_AGENT_URL", "")
        STRATEGIST_URL = env_vars_update.get("STRATEGIST_AGENT_URL", "")
        CRITIC_URL = env_vars_update.get("CRITIC_AGENT_URL", "")
        PM_URL = env_vars_update.get("PM_AGENT_URL", "")

        print("\n✓ All specialist agents deployed!")
        print("\nCollected URLs:")
        for name, url in agent_urls.items():
            print(f"  • {name}: {url}")

        print("\n" + "=" * 70)

    print("\n" + "=" * 70)
    print("TWO-STAGE DEPLOYMENT: Creative Director Agent Engine")
    print("=" * 70)

    init_vertex_ai()

    # Initialize client
    client = Client(project=PROJECT_ID, location=LOCATION)

    # =========================================================================
    # STAGE 1: Create Agent Engine Resource (No Code Yet)
    # =========================================================================
    print("\n⏳ STAGE 1: Creating Agent Engine resource...")
    print("   (This creates the resource and gets the ID)")

    agent_engine_resource = client.agent_engines.create(
        config={
            "display_name": DISPLAY_NAME,
        }
    )

    # Extract resource name and ID
    resource_name = agent_engine_resource.api_resource.name
    agent_engine_id = resource_name.split("/")[-1]

    print(f"\n✓ Agent Engine resource created!")
    print(f"  Resource: {resource_name}")
    print(f"  ID: {agent_engine_id}")

    # =========================================================================
    # STAGE 2: Deploy Agent Code with Environment Variables
    # =========================================================================
    print(f"\n⏳ STAGE 2: Deploying agent code to existing resource...")
    print(f"   (Setting environment variables for runtime)")

    # Import the app from agent.py
    # The actual app (with agent + compaction config) will be created on first use,
    # reading env vars at runtime
    sys.path.insert(0, str(project_root / 'agents'))
    from creative_director.agent import root_agent  # Actually an App object now

    # Wrap App in AdkApp for Agent Engine deployment
    # root_agent is actually an App with compaction config, not just an Agent
    adk_app = agent_engines.AdkApp(
        app=root_agent,  # Pass as 'app' parameter since it's an App object
        enable_tracing=True,
    )

    # Deploy agent code to the existing resource WITH env vars
    print(f"\n  Deploying with requirements:")
    print(f"    - google-cloud-aiplatform[agent_engines]>=1.112")
    print(f"    - google-adk[a2a]==1.20.0")
    print(f"    - google-genai>=1.51.0")
    print(f"    - python-dotenv>=1.0.0")

    remote_app = agent_engines.update(
        resource_name=resource_name,
        agent_engine=adk_app,
        requirements=[
            "google-cloud-aiplatform[agent_engines]>=1.112",
            "google-adk[a2a]==1.20.0",
            "google-genai>=1.51.0",
            "python-dotenv>=1.0.0",
        ],
        # Note: extra_packages not needed - agent is pickled with cloudpickle
        # IMPORTANT: Don't set GOOGLE_API_KEY - Agent Engine provides auth via project/location
        env_vars={
            "AGENT_ENGINE_ID": agent_engine_id,
            "COPYWRITER_AGENT_URL": COPYWRITER_URL,
            "DESIGNER_AGENT_URL": DESIGNER_URL,
            "STRATEGIST_AGENT_URL": STRATEGIST_URL,
            "CRITIC_AGENT_URL": CRITIC_URL,
            "PM_AGENT_URL": PM_URL,
            # Note: GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION are auto-set by Agent Engine
        },
    )

    print(f"\n✓ Agent code deployed!")
    print(f"  Environment variables set:")
    print(f"    - AGENT_ENGINE_ID={agent_engine_id}")
    print(f"    - COPYWRITER_AGENT_URL={COPYWRITER_URL or '(not set)'}")
    print(f"    - DESIGNER_AGENT_URL={DESIGNER_URL or '(not set)'}")
    print(f"    - STRATEGIST_AGENT_URL={STRATEGIST_URL or '(not set)'}")
    print(f"    - CRITIC_AGENT_URL={CRITIC_URL or '(not set)'}")
    print(f"    - PM_AGENT_URL={PM_URL or '(not set)'}")
    print(f"  Auto-set by Agent Engine:")
    print(f"    - GOOGLE_CLOUD_PROJECT (for authentication)")
    print(f"    - GOOGLE_CLOUD_LOCATION (for authentication)")

    # =========================================================================
    # SUCCESS
    # =========================================================================
    print("\n" + "=" * 70)
    print("✅ TWO-STAGE DEPLOYMENT SUCCESSFUL!")
    print("=" * 70)

    print(f"\nResource Name: {resource_name}")
    print(f"Agent Engine ID: {agent_engine_id}")

    print(f"\n✓ RemoteA2aAgent will work at runtime!")
    print(f"  - Agent URLs are set as environment variables")
    print(f"  - No AGENT_ENGINE_DEPLOYMENT flag at runtime")
    print(f"  - Full orchestration capabilities enabled")

    print(f"\nUpdate your .env file with:")
    print(f'AGENT_ENGINE_RESOURCE_NAME="{resource_name}"')
    print(f'AGENT_ENGINE_ID="{agent_engine_id}"')

    print(f"\nView in Cloud Console:")
    print(f"https://console.cloud.google.com/vertex-ai/reasoning-engines?project={PROJECT_ID}")

    return remote_app, resource_name


# =============================================================================
# TESTING
# =============================================================================

async def test_deployed_agent(resource_name: str):
    """Test the deployed agent."""
    print("\n" + "=" * 70)
    print("TESTING DEPLOYED AGENT")
    print("=" * 70)

    init_vertex_ai()

    # Connect to deployed agent
    remote_app = agent_engines.get(resource_name)
    print(f"✓ Connected to: {resource_name}")

    # Create session
    session = await remote_app.async_create_session(user_id="test_user")
    print(f"✓ Created session: {session['id']}")

    # Test query
    test_query = """Create a social media campaign for:
    - Product: Eco-friendly coffee brand "GreenBrew"
    - Target Audience: Gen-Z, environmentally conscious, 18-25 years old
    - Platform: Instagram
    - Goal: Brand awareness and drive website traffic
    """
    print(f"\n{'─' * 70}")
    print(f"USER: {test_query}")
    print(f"{'─' * 70}\n")

    response_count = 0
    async for event in remote_app.async_stream_query(
        user_id="test_user",
        session_id=session["id"],
        message=test_query,
    ):
        response_count += 1
        print(f"Event {response_count}: {event}")  # Debug: show all events
        content = event.get("content", {})
        parts = content.get("parts", [])
        for part in parts:
            if part.get("text") and not part.get("function_call"):
                print(f"AGENT: {part['text']}")
            elif part.get("function_call"):
                print(f"FUNCTION CALL: {part.get('function_call')}")

    print("\n" + "=" * 70)
    print("✓ Test complete!")
    print("=" * 70)


# =============================================================================
# CLEANUP
# =============================================================================

def cleanup_agent_engine(resource_name: str):
    """Delete the deployed Agent Engine resource."""
    print("\n" + "=" * 70)
    print("CLEANUP: Deleting Agent Engine")
    print("=" * 70)

    init_vertex_ai()

    print(f"\n⚠️  WARNING: This will DELETE the following resource:")
    print(f"   {resource_name}")
    print()

    # Confirm deletion
    confirmation = input("⚠️  Are you SURE you want to delete this Agent Engine? (yes/no): ")
    if confirmation.lower() != "yes":
        print("\n❌ Cleanup cancelled.")
        return

    print(f"\n🗑️  Deleting Agent Engine: {resource_name}")

    try:
        # Initialize client
        client = Client(project=PROJECT_ID, location=LOCATION)

        # Delete the agent engine
        client.agent_engines.delete(resource_name=resource_name)

        print("\n" + "=" * 70)
        print("✅ AGENT ENGINE DELETED SUCCESSFULLY!")
        print("=" * 70)
        print(f"\n✓ Deleted: {resource_name}")
        print(f"\n💡 Don't forget to:")
        print(f"   - Remove AGENT_ENGINE_RESOURCE_NAME from your .env file")
        print(f"   - Remove AGENT_ENGINE_ID from your .env file")

    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ CLEANUP FAILED!")
        print("=" * 70)
        print(f"\nError: {str(e)}")
        print(f"\nYou can also delete the Agent Engine manually from:")
        print(f"https://console.cloud.google.com/vertex-ai/reasoning-engines?project={PROJECT_ID}")
        raise


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Two-Stage Deployment for Creative Director Agent Engine"
    )
    parser.add_argument(
        "--action",
        choices=["deploy", "test", "cleanup"],
        default="deploy",
        help="Action to perform: deploy (create Agent Engine), test (test deployment), cleanup (delete Agent Engine)"
    )
    parser.add_argument(
        "--resource_name",
        type=str,
        help="Resource name for test/cleanup actions (e.g., projects/.../reasoningEngines/...)"
    )
    # NEW: Add auto-deploy flag
    parser.add_argument(
        "--auto-deploy-specialists",
        action="store_true",
        help="Automatically deploy all specialist agents to Cloud Run before deploying orchestrator"
    )

    args = parser.parse_args()

    if args.action == "deploy":
        remote_app, resource_name = deploy_two_stage(
            auto_deploy_specialists=args.auto_deploy_specialists
        )
        print(f"\n💡 To test the deployment, run:")
        print(f'python3 {__file__} --action test --resource_name "{resource_name}"')
        print(f"\n💡 To delete the deployment, run:")
        print(f'python3 {__file__} --action cleanup --resource_name "{resource_name}"')

    elif args.action == "test":
        if not args.resource_name:
            # Try to get from env
            args.resource_name = os.getenv("AGENT_ENGINE_RESOURCE_NAME")
            if not args.resource_name:
                print("ERROR: --resource_name required for test")
                print("   Or set AGENT_ENGINE_RESOURCE_NAME in .env")
                return
        asyncio.run(test_deployed_agent(args.resource_name))

    elif args.action == "cleanup":
        if not args.resource_name:
            # Try to get from env
            args.resource_name = os.getenv("AGENT_ENGINE_RESOURCE_NAME")
            if not args.resource_name:
                print("ERROR: --resource_name required for cleanup")
                print("   Or set AGENT_ENGINE_RESOURCE_NAME in .env")
                print("\nUsage:")
                print(f'  python3 {__file__} --action cleanup --resource_name "projects/.../reasoningEngines/..."')
                return
        cleanup_agent_engine(args.resource_name)


if __name__ == "__main__":
    main()
