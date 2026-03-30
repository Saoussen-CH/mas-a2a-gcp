import datetime
import logging
import os

from google.adk.agents import Agent
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("ai_creative_studio.project_manager")


def get_system_instruction(database_id=None):
    """Generate system instruction with current date and optional Notion database ID."""
    db_info = (
        f"The Notion database ID is: {database_id}"
        if database_id
        else "No Notion database configured. Provide text-based timelines only."
    )

    # TODO: Write the system instruction for the Project Manager.
    # It should:
    #   - Use today's date as the starting point for all timelines
    #   - Break campaigns into phases: Strategy, Creation, Review, Launch
    #   - Create tasks with owners and deadlines
    #   - ALWAYS provide a text timeline first (primary deliverable)
    #   - Optionally create Notion pages using the MCP tools if configured
    #
    # Required text output format:
    #   **Project Timeline:** [phases with dates from today]
    #   **Task List:** [Task | Owner | Deadline | Status]
    #   **Budget Breakdown:** [by category]
    #   **Milestones:** [key checkpoints]
    #   **Notion Status:** [report on Notion operations, or "No Notion configured"]
    #
    # When Notion IS configured:
    #   - Use the available Notion tools to discover the schema and persist the project and tasks
    #   - Tool names follow the pattern API-<operation> — use exact hyphenated names from the
    #     tool manifest (e.g., API-retrieve-a-database, API-post-page); never shorten them
    #   - Call tools directly — never wrap in print() or prefix with default_api.
    #   - NEVER set properties of type "people" or "person" — the Notion API does not allow
    #     integration tokens to assign users; skip these properties entirely
    #   - If any Notion operation fails, continue — the text timeline is the primary deliverable
    #
    # Today's date: {datetime.date.today().strftime("%B %d, %Y")}
    return f"""
# TODO: Write the Project Manager system instruction here

Today's date: {datetime.date.today().strftime("%B %d, %Y")}
{db_info}
"""


def create_project_manager_agent():
    """Create the Project Manager agent, with Notion MCP if credentials are set."""
    notion_api_key = os.getenv("NOTION_API_KEY")
    notion_database_id = os.getenv("NOTION_PROJECT_DATABASE_ID")

    if not notion_api_key or not notion_database_id:
        logger.warning("Notion credentials not set — running without Notion integration")

        # TODO: Create and return an Agent without tools
        # Use name="project_manager", model="gemini-2.5-pro"
        return Agent(
            name="project_manager",
            model="gemini-2.5-flash",
            # TODO: add instruction=get_system_instruction()
            # TODO: add description=
        )

    else:
        logger.info(f"Notion configured — database: {notion_database_id}")

        # TODO: Create the MCP toolset for Notion
        # Hint: import McpToolset, StdioConnectionParams from google.adk.tools.mcp_tool
        #       import StdioServerParameters from mcp
        #
        # server_params = StdioServerParameters(
        #     command="notion-mcp-server",
        #     env={"NOTION_TOKEN": notion_api_key, "PATH": os.environ.get("PATH", "")}
        # )
        # notion_toolset = McpToolset(
        #     connection_params=StdioConnectionParams(server_params=server_params, timeout=30.0)
        # )

        # TODO: Create and return an Agent WITH the notion_toolset
        return Agent(
            name="project_manager",
            model="gemini-2.5-flash",
            # TODO: add instruction=get_system_instruction(database_id=notion_database_id)
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
