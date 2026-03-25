import logging
import os

from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.plugins.logging_plugin import LoggingPlugin
from google.adk.tools.agent_tool import AgentTool

logger = logging.getLogger("ai_creative_studio.creative_director")
logger.setLevel(logging.INFO)

# TODO: Define SYSTEM_INSTRUCTION_TEMPLATE
# The Creative Director orchestrates all specialist agents. It must:
#
# 1. CLASSIFY the request:
#    - Simple (e.g., "just research") → call ONE agent
#    - Complex (e.g., "full campaign") → call ALL 5 agents sequentially
#
# 2. PLAN before acting — announce the execution plan to the user:
#    "I'll coordinate our team. Here's my plan:
#     1. Brand Strategist will research...
#     2. Copywriter will create...
#     ..."
#
# 3. EXECUTE — for each agent:
#    a) Call the tool with full context (remote agents have no shared memory!)
#    b) Wait for tool_output
#    c) Verify success (check for errors)
#    d) Confirm to user: "✓ [Agent] complete."
#    e) If error: STOP and report — never continue after failure
#
# 4. REVISION LOOP — after the Critic:
#    - Parse Status: APPROVED or NEEDS_REVISION for posts and visuals
#    - If NEEDS_REVISION: call the relevant agent again with the critic's feedback
#    - Maximum 1 revision per deliverable (prevent infinite loops)
#    - Pass REVISED versions to the Project Manager
#
# 5. RULES:
#    - NEVER generate content yourself — always delegate to specialists
#    - NEVER skip agents in a planned workflow
#    - NEVER invent results — only report what tool_output actually contained
#    - ALWAYS pass prior agent outputs as context to the next agent
#
# The template uses {available_agents} which is injected at runtime
# with the list of configured specialist agents.
SYSTEM_INSTRUCTION_TEMPLATE = """
# TODO: Write the Creative Director system instruction here.
# Use {available_agents} as a placeholder where the agent list will be injected.

Available specialists:
{available_agents}
"""


def create_creative_director():
    """
    Create the Creative Director orchestrator.
    Reads specialist URLs from environment variables at runtime.
    """
    # Read specialist URLs from environment
    copywriter_url = os.getenv("COPYWRITER_AGENT_URL")
    designer_url = os.getenv("DESIGNER_AGENT_URL")
    strategist_url = os.getenv("STRATEGIST_AGENT_URL")
    critic_url = os.getenv("CRITIC_AGENT_URL")
    pm_url = os.getenv("PM_AGENT_URL")

    available_agents_list = []
    agent_tools = []

    # TODO: For each specialist URL that is set, create a RemoteA2aAgent
    # and wrap it in an AgentTool, then append to agent_tools.
    #
    # Pattern for each specialist:
    #
    # if strategist_url:
    #     available_agents_list.append(
    #         "- **brand_strategist**: Researches market trends, competitors, and audience insights"
    #     )
    #     strategist_agent = RemoteA2aAgent(
    #         name="brand_strategist",
    #         description="Brand strategist for market research and competitive insights",
    #         agent_card=f"{strategist_url}/.well-known/agent.json",
    #     )
    #     agent_tools.append(AgentTool(agent=strategist_agent))
    #
    # Repeat for: copywriter_url, designer_url, critic_url, pm_url

    available_agents_text = (
        "\n".join(available_agents_list)
        if available_agents_list
        else "No specialist agents configured. Set agent URLs in environment variables."
    )

    system_instruction = SYSTEM_INSTRUCTION_TEMPLATE.format(
        available_agents=available_agents_text
    )

    # TODO: Configure generation settings
    # Hint: use GenerateContentConfig(max_output_tokens=20000, temperature=0.2)
    from google.genai.types import GenerateContentConfig
    generation_config = GenerateContentConfig(
        max_output_tokens=20000,
        temperature=0.2,
    )

    agent = Agent(
        name="creative_director",
        model="gemini-2.5-flash",
        description="Creative Director orchestrator that coordinates specialist agents",
        instruction=system_instruction,
        tools=agent_tools,
        generate_content_config=generation_config,
    )

    # TODO: Wrap the agent in an App with EventsCompactionConfig
    # This prevents token limit failures in long 5-agent workflows.
    #
    # Hint:
    # from google.adk.apps import App
    # from google.adk.apps.app import EventsCompactionConfig
    # from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
    # from google.adk.models import Gemini
    #
    # compaction_config = EventsCompactionConfig(
    #     summarizer=LlmEventSummarizer(llm=Gemini(model_id="gemini-2.5-flash")),
    #     compaction_interval=3,
    #     overlap_size=1,
    # )
    # app = App(
    #     name="creative_director",
    #     root_agent=agent,
    #     events_compaction_config=compaction_config,
    #     plugins=[LoggingPlugin()],
    # )
    # return agent, app

    # Placeholder return until App is configured
    from google.adk.apps import App
    app = App(name="creative_director", root_agent=agent, plugins=[LoggingPlugin()])
    return agent, app


root_agent, root_app = create_creative_director()
