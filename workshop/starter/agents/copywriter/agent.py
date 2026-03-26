import logging
import os

from google.adk.agents import Agent

logger = logging.getLogger("ai_creative_studio.copywriter")

# TODO: Define SYSTEM_INSTRUCTION
# The Copywriter creates Instagram captions. It should:
#   - Read Brand Strategist insights from the conversation history (passed by the orchestrator)
#   - Create 3-5 caption variations with different tones
#   - Include 5-10 relevant hashtags per caption
#   - Suggest a CTA (call-to-action) for each caption
#   - Keep captions under 2,200 characters (Instagram limit)
#
# Output format:
#   - Caption title/theme
#   - Full caption text
#   - Hashtags list
#   - Suggested CTA
#
# Tip: Remind the agent that it will find Brand Strategist insights
# in the conversation history above its message.
SYSTEM_INSTRUCTION = """
# TODO: Write the Copywriter system instruction here
"""

# =============================================================================
# PROVIDED — do not modify
#
# Same Agent pattern you used in Step 4. The only difference between
# specialist agents is the name, description, and instruction.
# =============================================================================
root_agent = Agent(
    name="copywriter",
    model="gemini-2.5-flash",
    instruction=SYSTEM_INSTRUCTION,
    description="Expert social media copywriter for creating engaging captions and copy",
)

logger.info("Copywriter agent created")


if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv
    from google.adk.a2a.utils.agent_to_a2a import to_a2a

    load_dotenv()

    PORT = int(os.getenv("PORT", "8080"))
    HOST = os.getenv("HOST", "0.0.0.0")
    PUBLIC_HOST = os.getenv("PUBLIC_HOST", "localhost")
    PUBLIC_PORT = int(os.getenv("PUBLIC_PORT", str(PORT)))
    PROTOCOL = os.getenv("PROTOCOL", "http")

    a2a_app = to_a2a(root_agent, host=PUBLIC_HOST, port=PUBLIC_PORT, protocol=PROTOCOL)

    logger.info(f"Starting Copywriter on {PROTOCOL}://{HOST}:{PORT}")
    logger.info(f"Agent card: {PROTOCOL}://{HOST}:{PORT}/.well-known/agent.json")

    uvicorn.run(a2a_app, host=HOST, port=PORT)
