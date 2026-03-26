import logging
import os

from google.adk.agents import Agent

logger = logging.getLogger("ai_creative_studio.critic")

# TODO: Define SYSTEM_INSTRUCTION
# The Critic reviews campaign materials and returns STRUCTURED feedback.
# This structure is critical — the orchestrator parses it to decide revisions.
#
# Required output format (use this EXACTLY):
#
#   **POSTS REVIEW:**
#   - Score: [X/10]
#   - Status: [APPROVED | NEEDS_REVISION]
#   - What Works: ...
#   - Issues: ...
#   - Suggestions: ...
#
#   **VISUALS REVIEW:**
#   - Score: [X/10]
#   - Status: [APPROVED | NEEDS_REVISION]
#   - What Works: ...
#   - Issues: ...
#   - Suggestions: ...
#
#   **OVERALL ASSESSMENT:**
#   - All Approved: [YES | NO]
#   - Priority Revisions: ...
#   - Overall Score: [X/10]
#
# Scoring guide:
#   9-10 → APPROVED    (publish as-is)
#   7-8  → APPROVED    (minor issues, acceptable)
#   5-6  → NEEDS_REVISION
#   1-4  → NEEDS_REVISION
#
# Evaluation criteria: clarity, brand alignment, audience fit,
# platform optimization, visual-copy harmony, CTA strength, engagement potential
SYSTEM_INSTRUCTION = """
# TODO: Write the Critic system instruction here
"""

# =============================================================================
# PROVIDED — do not modify
#
# Same Agent pattern you used in Step 4. The only difference between
# specialist agents is the name, description, and instruction.
# =============================================================================
root_agent = Agent(
    name="critic",
    model="gemini-2.5-flash",
    instruction=SYSTEM_INSTRUCTION,
    description="Creative critic for reviewing campaign materials and providing constructive feedback",
)

logger.info("Critic agent created")


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

    logger.info(f"Starting Critic on {PROTOCOL}://{HOST}:{PORT}")
    logger.info(f"Agent card: {PROTOCOL}://{HOST}:{PORT}/.well-known/agent.json")

    uvicorn.run(a2a_app, host=HOST, port=PORT)
