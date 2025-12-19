#!/usr/bin/env python3
"""
Test designer agent directly to see response length
"""
import asyncio
import os
from dotenv import load_dotenv
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv("../../.env")

DESIGNER_URL = os.getenv("DESIGNER_AGENT_URL")

async def test():
    print(f"Testing Designer: {DESIGNER_URL}\n")

    designer_agent = RemoteA2aAgent(
        name="designer",
        description="Test designer",
        agent_card=f"{DESIGNER_URL}/.well-known/agent.json"
    )

    session_service = InMemorySessionService()
    runner = Runner(
        app_name="test",
        agent=designer_agent,
        session_service=session_service
    )

    session_id = "test_designer"
    user_id = "test_user"

    await session_service.create_session(
        app_name="test",
        user_id=user_id,
        session_id=session_id
    )

    query = """Create visual concepts for 3 Instagram posts promoting GreenBrew eco-friendly coffee:
- Post 1: "Sustainable Sourcing" theme
- Post 2: "Morning Ritual" theme
- Post 3: "Eco-Innovation" theme

Target audience: Gen-Z, eco-conscious, 18-25 years old
Style: modern, minimalist, earth tones"""

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
    print(f"Token estimate: ~{len(full_response) // 4} tokens")

    await runner.close()

if __name__ == "__main__":
    asyncio.run(test())
