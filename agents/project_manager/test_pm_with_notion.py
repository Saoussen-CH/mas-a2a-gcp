"""
Test Project Manager agent with Notion integration
"""
import os
import asyncio
from dotenv import load_dotenv
from a2a_sdk.client import RemoteA2aAgent

# Load environment variables
load_dotenv(dotenv_path="../../.env")

PM_AGENT_URL = os.getenv("PM_AGENT_URL")

async def test_pm_with_notion():
    """Test Project Manager agent with Notion integration"""

    print(f"🧪 Testing Project Manager agent at: {PM_AGENT_URL}")
    print("=" * 70)

    # Create remote agent client
    pm_agent = RemoteA2aAgent(url=PM_AGENT_URL)

    # Test query: Create a project timeline
    query = """
    Create a project timeline for a simple product launch campaign:
    - Product: New eco-friendly water bottle
    - Timeline: 2 weeks
    - Budget: $3,000
    - Deliverables: 3 social media posts, 1 landing page

    Please create the timeline and save it to Notion.
    """

    print(f"📝 Query:\n{query}\n")
    print("⏳ Sending request...\n")

    try:
        # Send the query
        response = await pm_agent.send(query)

        print("=" * 70)
        print("✅ Response from Project Manager:")
        print("=" * 70)
        print(response)
        print("=" * 70)

        # Check if Notion was mentioned in the response
        if "notion" in response.lower():
            print("\n✅ SUCCESS: Project Manager used Notion!")
        else:
            print("\n⚠️  Warning: No mention of Notion in response")

    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pm_with_notion())
