import logging
import os

from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.plugins.logging_plugin import LoggingPlugin
from google.adk.tools.agent_tool import AgentTool

try:
    from .prompt import SYSTEM_INSTRUCTION_TEMPLATE
except ImportError:
    from prompt import SYSTEM_INSTRUCTION_TEMPLATE  # direct execution fallback

logger = logging.getLogger("ai_creative_studio.creative_director")
logger.setLevel(logging.INFO)


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
        model="gemini-2.5-pro",
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
