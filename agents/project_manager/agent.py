# Copyright 2026 Saoussen Chaabnia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Project Manager Agent
Creates project timelines and tasks with Notion integration
"""

import datetime
import logging
import os

from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

# Get logger for this agent
logger = logging.getLogger("ai_creative_studio.project_manager")


def get_system_instruction(database_id=None, tasks_database_id=None):
    """Generate system instruction with current date and Notion database IDs."""
    db_info = (
        f"Projects database ID: {database_id}\nTasks database ID: {tasks_database_id}"
        if database_id
        else "No Notion database configured."
    )

    return f"""You are a Project Manager specializing in creative campaign execution.

Today's date is {datetime.date.today().strftime("%B %d, %Y")}.

{db_info}

Create a complete project plan: phases, tasks with deadlines, budget breakdown, milestones.

If Notion tools are available, use them to persist the project and tasks to the databases.
Tool names follow the pattern `API-<operation>` — always use the exact hyphenated names from the tool manifest (e.g., `API-retrieve-a-database`, `API-post-page`). Never shorten or reformat them.
Call tools directly — never wrap them in `print()` and never prefix with `default_api.`

Constraints:
- Never set properties of type "people" or "person" (e.g., Owner, Assignee) — the Notion API rejects bot assignments; skip these properties entirely
- Use only property names and values that actually exist in the schema you discover
- If any Notion operation fails, continue — the text plan is always the primary deliverable

Write your full response only after any Notion operations have completed:

**Project Timeline:**
[phases with dates starting from today]

**Task List:**
| Task | Owner | Deadline | Status |
[tasks with deadlines; set Owner to TBD]

**Budget Breakdown:**
[cost allocation by category]

**Milestones:**
[key checkpoints with dates]

**Notion Status:**
["Project created (ID: xxx), N tasks linked" — or "Notion not configured — text timeline only"]
Do not repeat the timeline here.
"""


def create_project_manager_agent():
    """Create the Project Manager agent with Notion MCP integration"""
    logger.info("Creating Project Manager agent with Gemini 2.5 Flash and Notion MCP")

    # Debug: Log all environment variables
    logger.info(f"Environment variables: {list(os.environ.keys())}")

    # Get Notion credentials from environment
    notion_api_key = os.getenv("NOTION_API_KEY")
    notion_database_id = os.getenv("NOTION_PROJECT_DATABASE_ID")
    notion_tasks_db_id = os.getenv("NOTION_TASKS_DATABASE_ID")

    if not notion_api_key or not notion_database_id:
        logger.warning(
            "NOTION_API_KEY or NOTION_PROJECT_DATABASE_ID not set - running without Notion integration"
        )
        agent = Agent(
            name="project_manager",
            model="gemini-2.5-pro",
            instruction=get_system_instruction(),
            description="Project manager for creating timelines, tasks, and organizing campaign deliverables",
        )
    else:
        # Create Notion MCP toolset
        logger.info(f"Configuring Notion MCP with database: {notion_database_id}")
        logger.info(f"API Key (first 10 chars): {notion_api_key[:10]}...")

        mcp_env = {
            "NOTION_TOKEN": notion_api_key,
            "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        }

        server_params = StdioServerParameters(
            command="notion-mcp-server",
            args=[],
            env=mcp_env,
        )

        notion_toolset = McpToolset(
            connection_params=StdioConnectionParams(
                server_params=server_params,
                timeout=30.0,
            )
        )

        # Use Pro for reliable multi-step tool calling with MCP
        agent = Agent(
            name="project_manager",
            model="gemini-2.5-pro",
            instruction=get_system_instruction(
                database_id=notion_database_id,
                tasks_database_id=notion_tasks_db_id,
            ),
            description="Project manager for creating timelines, tasks, and organizing campaign deliverables with Notion integration",
            tools=[notion_toolset],
        )

        logger.info("Project Manager agent created with Notion MCP integration")

    return agent


# Create root_agent for A2A deployment
root_agent = create_project_manager_agent()


if __name__ == "__main__":
    import os

    import uvicorn
    from dotenv import load_dotenv
    from google.adk.a2a.utils.agent_to_a2a import to_a2a

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
    logger.info(f"🚀 Starting Project Manager A2A Server on {PROTOCOL}://{HOST}:{PORT}")
    logger.info(
        f"📋 Agent card available at: {PROTOCOL}://{HOST}:{PORT}/.well-known/agent-card.json"
    )
    logger.info(f"🌐 Public URL: {PROTOCOL}://{PUBLIC_HOST}:{PUBLIC_PORT}")

    uvicorn.run(a2a_app, host=HOST, port=PORT)
