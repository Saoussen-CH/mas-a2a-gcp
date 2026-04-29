import datetime
import logging
import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.google_search_tool import google_search
from retry import GENERATE_CONTENT_CONFIG

load_dotenv()

logger = logging.getLogger("ai_creative_studio.brand_strategist")

# TODO: Define SYSTEM_INSTRUCTION
# The Brand Strategist is a RESEARCH-ONLY agent. It should:
#   - Search for target audience insights (use google_search with current year)
#   - Analyze 2-3 competitor brands
#   - Identify 3-5 trending topics in the product category
#   - Return structured output with sections:
#       **Audience Insights:** ...
#       **Competitive Analysis:** ...
#       **Trending Topics:** ...
#       **Key Strategic Insights:** ...
#
# Important constraints to include in the instruction:
#   - DO NOT create captions, copy, or designs
#   - RESEARCH ONLY — the Creative Director coordinates next steps
#   - Always include the current year in search queries
#   - Today's date is: {datetime.date.today().strftime("%B %d, %Y")}
SYSTEM_INSTRUCTION = """
# TODO: Write the Brand Strategist system instruction here
"""

# TODO: Create the root_agent
# Use:
#   name="brand_strategist"
#   model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
#   tools=[google_search]
root_agent = Agent(
    name="brand_strategist",
    model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    generate_content_config=GENERATE_CONTENT_CONFIG,
    # TODO: add instruction=SYSTEM_INSTRUCTION
    # TODO: add description=
    # TODO: add tools=
)

logger.info("Brand Strategist agent created")


if __name__ == "__main__":
    import uvicorn
    from google.adk.a2a.utils.agent_to_a2a import to_a2a

    PORT = int(os.getenv("PORT", "8082"))
    HOST = os.getenv("HOST", "0.0.0.0")
    PUBLIC_HOST = os.getenv("PUBLIC_HOST", "localhost")
    PUBLIC_PORT = int(os.getenv("PUBLIC_PORT", str(PORT)))
    PROTOCOL = os.getenv("PROTOCOL", "http")

    a2a_app = to_a2a(root_agent, host=PUBLIC_HOST, port=PUBLIC_PORT, protocol=PROTOCOL)

    logger.info(f"Starting Brand Strategist on {PROTOCOL}://{HOST}:{PORT}")
    logger.info(f"Agent card: {PROTOCOL}://{HOST}:{PORT}/.well-known/agent.json")

    uvicorn.run(a2a_app, host=HOST, port=PORT)
