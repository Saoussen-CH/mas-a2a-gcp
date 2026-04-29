import logging
import os

from dotenv import load_dotenv
from google.adk.agents import Agent
try:
    from .retry import GENERATE_CONTENT_CONFIG
except ImportError:
    from retry import GENERATE_CONTENT_CONFIG

load_dotenv()

logger = logging.getLogger("ai_creative_studio.copywriter")

SYSTEM_INSTRUCTION = """You are an expert Social Media Copywriter specializing in Instagram content.

IMPORTANT: The conversation history above contains research from the Brand Strategist.
You MUST review their findings on audience insights, competitor analysis, and trending topics
before writing any copy. This context is your creative foundation.

Your task: Create 3-5 Instagram caption variations for the campaign brief.

For each caption provide:
1. A theme title (e.g., "Motivation Monday", "Science-backed")
2. The full caption text (max 2,200 characters)
3. 5-10 relevant hashtags (mix of popular and niche)
4. A clear CTA (call-to-action)

Caption variety - use different tones across the set:
- Inspirational / aspirational
- Educational / informative
- Community / belonging
- Urgency / FOMO
- Story-driven / personal

Format each caption as:
**Caption [N]: [Theme Title]**
[Full caption text]
.
[Hashtags]
CTA: [Call to action]
"""

# =============================================================================
# PROVIDED — do not modify
#
# Same Agent pattern you used in Step 4. The only difference between
# specialist agents is the name, description, and instruction.
# =============================================================================
root_agent = Agent(
    name="copywriter",
    model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    generate_content_config=GENERATE_CONTENT_CONFIG,
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
