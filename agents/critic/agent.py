"""
Critic Agent
Reviews campaign outputs and suggests improvements
Uses Gemini API directly (no MCP needed)
"""

import logging
from google.adk.agents import Agent

# Get logger for this agent
logger = logging.getLogger("ai_creative_studio.critic")

SYSTEM_INSTRUCTION = """You are a Creative Critic with expertise in social media marketing and brand communication.

Your role is to review campaign materials and provide constructive feedback.

Evaluation criteria:
- **Message Clarity**: Is the message clear and compelling?
- **Brand Alignment**: Does it match the brand voice and values?
- **Audience Fit**: Will it resonate with the target audience?
- **Platform Optimization**: Is it optimized for the platform (Instagram, TikTok, etc.)?
- **Visual-Copy Harmony**: Do visuals and copy work together?
- **Call-to-Action**: Is the CTA clear and motivating?
- **Engagement Potential**: Will this drive likes, comments, shares?

When reviewing materials:
1. Acknowledge what works well
2. Identify specific issues or weaknesses
3. Provide actionable suggestions for improvement
4. Rate overall quality (1-10)
5. Recommend whether to approve, revise, or restart

Format your feedback as:
**What Works Well:**
[Positive elements]

**Areas for Improvement:**
[Specific issues and why they matter]

**Suggestions:**
[Concrete recommendations]

**Overall Rating:** [X/10]
**Recommendation:** [Approve / Minor Revisions / Major Revisions]
"""

def create_critic_agent():
    """Create the Critic agent"""
    logger.info("Creating Critic agent with Gemini 2.5 Flash")
    agent = Agent(
        name="critic",
        model="gemini-2.5-flash",
        instruction=SYSTEM_INSTRUCTION,
        description="Creative critic for reviewing campaign materials and providing constructive feedback"
    )
    logger.info("Critic agent created successfully")
    return agent


# Create root_agent for A2A deployment
root_agent = create_critic_agent()


if __name__ == "__main__":
    import os
    import uvicorn
    from google.adk.a2a.utils.agent_to_a2a import to_a2a
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    # Server listening configuration
    PORT = int(os.getenv("PORT", "8080"))
    HOST = os.getenv("HOST", "0.0.0.0")

    # Public-facing configuration for A2A agent card
    PUBLIC_HOST = os.getenv("PUBLIC_HOST", "localhost")
    PUBLIC_PORT = int(os.getenv("PUBLIC_PORT", str(PORT)))
    PROTOCOL = os.getenv("PROTOCOL", "http")

    # Convert agent to A2A application
    a2a_app = to_a2a(root_agent, host=PUBLIC_HOST, port=PUBLIC_PORT, protocol=PROTOCOL)

    # Start server
    logger.info(f"🚀 Starting Critic A2A Server on {PROTOCOL}://{HOST}:{PORT}")
    logger.info(f"📋 Agent card available at: {PROTOCOL}://{HOST}:{PORT}/.well-known/agent-card.json")
    logger.info(f"🌐 Public URL: {PROTOCOL}://{PUBLIC_HOST}:{PUBLIC_PORT}")

    uvicorn.run(a2a_app, host=HOST, port=PORT)
