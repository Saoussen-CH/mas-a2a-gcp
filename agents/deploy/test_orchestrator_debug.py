#!/usr/bin/env python3
"""
Debug test to see full orchestrator response with all event details
"""
import asyncio
import os
from dotenv import load_dotenv
import vertexai
from vertexai import agent_engines

load_dotenv("../../.env")

PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
RESOURCE_NAME = os.getenv("AGENT_ENGINE_RESOURCE_NAME")

async def test():
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    remote_app = agent_engines.get(RESOURCE_NAME)
    print(f"Connected to: {RESOURCE_NAME}\n")

    session = await remote_app.async_create_session(user_id="debug_user")
    print(f"Session: {session['id']}\n")

    query = """Create a complete social media campaign for:
- Product: Eco-friendly coffee brand "GreenBrew"
- Target Audience: Gen-Z, environmentally conscious, 18-25 years old
- Platform: Instagram
- Goal: Brand awareness and drive website traffic
- Budget: $5,000
- Timeline: Launch in 2 weeks
- Brand Voice: Authentic, playful, educational

Create: market research, 3 posts with copy, visual concepts, and project timeline."""

    print("=" * 70)
    print("STREAMING RESPONSE (with debug info)")
    print("=" * 70)

    event_count = 0
    text_parts = 0
    tool_calls = 0

    async for event in remote_app.async_stream_query(
        user_id="debug_user",
        session_id=session["id"],
        message=query,
    ):
        event_count += 1
        print(f"\n--- Event {event_count} ---")

        # Check for finish reason
        if "candidates" in event:
            for candidate in event["candidates"]:
                if "finishReason" in candidate:
                    print(f"🛑 FINISH REASON: {candidate['finishReason']}")

        content = event.get("content", {})
        parts = content.get("parts", [])

        for part in parts:
            if part.get("text") and not part.get("function_call"):
                text_parts += 1
                text = part["text"]
                print(f"📝 Text (part {text_parts}, {len(text)} chars): {text[:100]}...")
            elif part.get("function_call"):
                tool_calls += 1
                func_name = part.get("function_call", {}).get("name", "unknown")
                print(f"🔧 Tool call {tool_calls}: {func_name}")

    print("\n" + "=" * 70)
    print(f"SUMMARY:")
    print(f"  Total events: {event_count}")
    print(f"  Text parts: {text_parts}")
    print(f"  Tool calls: {tool_calls}")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test())
