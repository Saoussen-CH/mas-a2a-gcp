#!/usr/bin/env python3
"""
Test calling project_manager directly via RemoteA2aAgent
"""
import asyncio
import os
from dotenv import load_dotenv
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv("../../.env")

PM_URL = os.getenv("PM_AGENT_URL")

async def test():
    print(f"Testing PM Agent: {PM_URL}\n")

    # Create remote agent
    pm_agent = RemoteA2aAgent(
        name="project_manager",
        description="Test PM",
        agent_card=f"{PM_URL}/.well-known/agent.json"
    )

    # Create runner
    session_service = InMemorySessionService()
    runner = Runner(
        app_name="test",
        agent=pm_agent,
        session_service=session_service
    )

    session_id = "test_pm"
    user_id = "test_user"

    await session_service.create_session(
        app_name="test",
        user_id=user_id,
        session_id=session_id
    )

    query = """Create a project timeline for a 2-week campaign:
- Budget: $5,000
- Deliverables: 5 Instagram posts
- Team: Copywriter, Designer"""

    print("Sending query...")
    print("=" * 70)

    response_text = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(parts=[types.Part(text=query)])
    ):
        if hasattr(event, 'text') and event.text:
            response_text.append(event.text)
            print(event.text, end='', flush=True)
        elif hasattr(event, 'content') and event.content:
            if hasattr(event.content, 'parts'):
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        response_text.append(part.text)
                        print(part.text, end='', flush=True)

    print("\n" + "=" * 70)

    full_response = "".join(response_text)
    print(f"\nTotal response length: {len(full_response)} chars")

    if len(full_response) == 0:
        print("❌ EMPTY RESPONSE!")
    else:
        print("✅ Got response")

    await runner.close()

if __name__ == "__main__":
    asyncio.run(test())
