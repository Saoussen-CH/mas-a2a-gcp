import datetime
import logging
import os

from google.adk.agents import Agent
from dotenv import load_dotenv
try:
    from .retry import GENERATE_CONTENT_CONFIG
except ImportError:
    from retry import GENERATE_CONTENT_CONFIG

load_dotenv()

logger = logging.getLogger("ai_creative_studio.project_manager")


def get_system_instruction(project_database_id=None, tasks_database_id=None):
    # notion_section is empty when Notion is not configured, so the agent
    # receives no tool instructions for capabilities it doesn't have.
    notion_section = (
        f"""
Projects database ID: {project_database_id}
Tasks database ID: {tasks_database_id}

Also persist the project and tasks to these Notion databases.
Use the available Notion tools to discover the schema and decide how to proceed.
Tool names follow the pattern `API-<operation>` - use exact hyphenated names from the tool manifest
(e.g., `API-retrieve-a-database`, `API-post-page`). Never shorten or reformat them.
Call tools directly - never wrap in `print()` or prefix with `default_api.`

Notion constraints:
- When creating a page inside a database, always use `"parent": {{"database_id": "<id>"}}` — never `page_id`
- Never set properties of type "people" or "person" (e.g., Owner, Assignee) - the Notion API does
  not allow integration tokens to assign users; skip these properties entirely
- Use only property names and values that actually exist in the schema you discover
- If any Notion call fails, continue - the text timeline is the primary deliverable

Write your complete response AFTER all Notion operations are done (or have failed).
"""
        if project_database_id
        else ""
    )

    # TODO: Write the system instruction for the Project Manager.
    # It should:
    #   - Use today's date as the starting point for all timelines
    #   - Break campaigns into phases: Strategy, Creation, Review, Launch
    #   - Create tasks with owners and deadlines
    #   - ALWAYS provide a text timeline first (primary deliverable)
    #   - Use {notion_section} to optionally include Notion guidance
    #
    # Required text output format:
    #   **Project Timeline:** [phases with dates from today]
    #   **Task List:** [Task | Owner | Deadline | Status]
    #   **Budget Breakdown:** [by category]
    #   **Milestones:** [key checkpoints]
    #   **Notion Status:** ["Project created..." or "Notion not configured - text timeline only"]
    #
    # Today's date: {datetime.date.today().strftime("%B %d, %Y")}
    return f"""
# TODO: Write the Project Manager system instruction here

Today's date: {datetime.date.today().strftime("%B %d, %Y")}
{notion_section}
"""


def create_project_manager_agent():
    """Create the Project Manager agent, with Notion MCP if credentials are set."""
    notion_token           = os.getenv("NOTION_TOKEN")
    notion_project_db_id   = os.getenv("NOTION_PROJECT_DATABASE_ID")
    notion_tasks_db_id     = os.getenv("NOTION_TASKS_DATABASE_ID")

    if not notion_token or not notion_project_db_id or not notion_tasks_db_id:
        logger.warning("Notion credentials not set — running without Notion integration")

        # TODO: Create and return an Agent without tools
        # Use name="project_manager", model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        return Agent(
            name="project_manager",
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            generate_content_config=GENERATE_CONTENT_CONFIG,
            # TODO: add instruction=get_system_instruction()
            # TODO: add description=
        )

    else:
        logger.info(f"Notion configured — projects database: {notion_project_db_id}, tasks database: {notion_tasks_db_id}")

        # TODO: Create the MCP toolset for Notion
        # Hint: import McpToolset, StdioConnectionParams from google.adk.tools.mcp_tool
        #       import StdioServerParameters from mcp
        #
        # server_params = StdioServerParameters(
        #     command="notion-mcp-server",
        #     env={"NOTION_TOKEN": notion_token, "PATH": os.environ.get("PATH", "")}
        # )
        # notion_toolset = McpToolset(
        #     connection_params=StdioConnectionParams(server_params=server_params, timeout=30.0)
        # )

        # TODO: Create and return an Agent WITH the notion_toolset
        return Agent(
            name="project_manager",
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            generate_content_config=GENERATE_CONTENT_CONFIG,
            # TODO: add instruction=get_system_instruction(project_database_id=notion_project_db_id, tasks_database_id=notion_tasks_db_id)
            # TODO: add description=
            # TODO: add tools=[notion_toolset]
        )


root_agent = create_project_manager_agent()
logger.info("Project Manager agent created")


if __name__ == "__main__":
    import uvicorn
    from google.adk.a2a.utils.agent_to_a2a import to_a2a

    PORT = int(os.getenv("PORT", "8080"))
    HOST = os.getenv("HOST", "0.0.0.0")
    PUBLIC_HOST = os.getenv("PUBLIC_HOST", "localhost")
    PUBLIC_PORT = int(os.getenv("PUBLIC_PORT", str(PORT)))
    PROTOCOL = os.getenv("PROTOCOL", "http")

    a2a_app = to_a2a(root_agent, host=PUBLIC_HOST, port=PUBLIC_PORT, protocol=PROTOCOL)

    logger.info(f"Starting Project Manager on {PROTOCOL}://{HOST}:{PORT}")
    logger.info(f"Agent card: {PROTOCOL}://{HOST}:{PORT}/.well-known/agent.json")

    uvicorn.run(a2a_app, host=HOST, port=PORT)
