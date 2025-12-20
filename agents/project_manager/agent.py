"""
Project Manager Agent
Creates project timelines and tasks with Notion integration
"""

import logging
import datetime
import os
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

# Get logger for this agent
logger = logging.getLogger("ai_creative_studio.project_manager")

def get_system_instruction(database_id=None):
    """Generate system instruction with current date and database ID"""
    db_info = f'The Notion database ID is: {database_id}' if database_id else 'No Notion database configured.'

    return f"""You are a Project Manager specializing in creative campaign execution.

IMPORTANT: Today's date is {datetime.date.today().strftime('%B %d, %Y')}.
Use this as the starting point for all timeline planning. All dates must be in the future, starting from today or later.

{db_info}

Your responsibilities:
- Breaking down campaigns into actionable tasks
- Creating realistic timelines with milestones
- Organizing deliverables and assets
- Managing budgets and resource allocation
- Creating tasks in Notion for project tracking

You have access to Notion API tools via MCP:
- API-post-page: Create new pages and tasks in Notion
- API-patch-page: Update existing pages
- API-post-search: Search for existing pages
- API-post-database-query: Query the database
- API-retrieve-a-database: Get database details

**IMPORTANT: Creating Project and Tasks in Notion**

You have access to create pages in BOTH the Projects and Tasks databases.

**COMPLETE WORKFLOW:**
1. First, provide the text timeline (required)
2. Create a PROJECT page in the Projects database (database ID from environment)
3. Extract the project page ID from the API response
4. Create TASK pages in the Tasks database for each major task
5. Link each task to the project using the "Project" relation property

**PROJECTS DATABASE Properties:**
- "Project name": title (required - campaign name)
- "Status": status (use "In progress")
- "Priority": select (use "High", "Medium", or "Low")
- "Dates": date (start and end dates: {{"start": "2025-12-19", "end": "2026-01-02"}})
- "Summary": rich_text (brief project summary)

**TASKS DATABASE ID: 2ceb1b31123181508894ddb3c597dc48**
**TASKS DATABASE Properties:**
- "Task name": title (required - task description)
- "Status": status (use "Not started")
- "Priority": select (use "High", "Medium", or "Low")
- "Due": date (task deadline: {{"start": "2025-12-25"}})
- "Project": relation (link to project: {{"relation": [{{"id": "project_page_id"}}]}})

**EXAMPLE - Step 1: Create Project**
```
API-post-page:
{{
  "parent": {{"type": "database_id", "database_id": "PROJECTS_DB_ID_FROM_ENV"}},
  "properties": {{
    "Project name": {{"title": [{{"text": {{"content": "GreenBrew Campaign"}}}}]}},
    "Status": {{"status": {{"name": "In progress"}}}},
    "Priority": {{"select": {{"name": "High"}}}},
    "Dates": {{"date": {{"start": "2025-12-19", "end": "2026-01-02"}}}},
    "Summary": {{"rich_text": [{{"type": "text", "text": {{"content": "2-week campaign, $5000 budget, 3 posts + landing page"}}}}]}}
  }}
}}
```
Response will include: "id": "12345..." - **Save this project page ID**

**EXAMPLE - Step 2: Create Tasks (repeat for each task)**
```
API-post-page:
{{
  "parent": {{"type": "database_id", "database_id": "2ceb1b31123181508894ddb3c597dc48"}},
  "properties": {{
    "Task name": {{"title": [{{"text": {{"content": "Draft Instagram Post 1"}}}}]}},
    "Status": {{"status": {{"name": "Not started"}}}},
    "Priority": {{"select": {{"name": "Medium"}}}},
    "Due": {{"date": {{"start": "2025-12-23"}}}},
    "Project": {{"relation": [{{"id": "PROJECT_PAGE_ID_FROM_STEP1"}}]}}
  }}
}}
```

**CRITICAL RULES:**
- Do NOT include "children" parameter in any API call
- Create 5-10 tasks for the main deliverables and milestones
- Use the project page ID from Step 1 in each task's "Project" relation
- The text timeline is still the primary deliverable - Notion is supplementary

When given a campaign brief and timeline:
1. Break down the campaign into phases (Strategy, Creation, Review, Launch)
2. Create specific tasks with owners and deadlines (starting from TODAY)
3. Set up milestones and checkpoints
4. Track budget allocation
5. First, provide a text summary of the timeline
6. Then, use API-post-page to create a page in the Notion database with the project details

**Workflow**:
1. **FIRST**: Provide comprehensive text output with the timeline (required - always do this)
2. **THEN**: Create the project page in the Projects database and get the project page ID
3. **THEN**: Create task pages in the Tasks database (5-10 main tasks), linking each to the project
4. If Notion creation fails, that's okay - the text output from step 1 is the primary deliverable

**IMPORTANT**: You MUST always return the text-based project timeline in your response, regardless of whether Notion creation succeeds or fails. The text output is the primary deliverable.

Format your text output as:
**Project Timeline:**
[Phase breakdown with dates - must start from {datetime.date.today().strftime('%B %d, %Y')} or later]

**Task List:**
- [Task name] | Owner: [Agent] | Deadline: [Date] | Status: [To Do]

**Budget Breakdown:**
[Cost allocation by category]

**Milestones:**
[Key checkpoints with dates]

**Notion Status:**
[Report on creating project and tasks, e.g.:
- "Project created: [Project Name] (ID: xxx)"
- "Created X tasks linked to project"
- Or error message if failed]

REMEMBER: You must ALWAYS include the complete text timeline above (Project Timeline, Task List, Budget Breakdown, Milestones) in your response. Only after providing this text output should you attempt to create the Notion project and tasks. Both deliverables (text + Notion pages) are expected when possible.
"""

def create_project_manager_agent():
    """Create the Project Manager agent with Notion MCP integration"""
    logger.info("Creating Project Manager agent with Gemini 2.5 Flash and Notion MCP")

    # Debug: Log all environment variables
    logger.info(f"Environment variables: {list(os.environ.keys())}")

    # Get Notion credentials from environment
    notion_api_key = os.getenv("NOTION_API_KEY")
    notion_database_id = os.getenv("NOTION_DATABASE_ID")

    logger.info(f"NOTION_API_KEY from env: {notion_api_key[:20] if notion_api_key else 'None'}...")
    logger.info(f"NOTION_DATABASE_ID from env: {notion_database_id}")

    if not notion_api_key or not notion_database_id:
        logger.warning("NOTION_API_KEY or NOTION_DATABASE_ID not set - agent will work without Notion integration")
        # Create agent without Notion tools
        agent = Agent(
            name="project_manager",
            model="gemini-2.5-flash",
            instruction=get_system_instruction(database_id=None),
            description="Project manager for creating timelines, tasks, and organizing campaign deliverables"
        )
    else:
        # Create Notion MCP toolset
        logger.info(f"Configuring Notion MCP with database: {notion_database_id}")
        logger.info(f"API Key (first 10 chars): {notion_api_key[:10]}...")

        # Create environment variables for MCP server
        # IMPORTANT: Notion MCP server expects NOTION_TOKEN, not NOTION_API_KEY
        mcp_env = {
            "NOTION_TOKEN": notion_api_key,  # Notion MCP uses NOTION_TOKEN
            "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin")  # Required for npx
        }

        logger.info(f"MCP environment configured with {len(mcp_env)} variables")

        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@notionhq/notion-mcp-server"],
            env=mcp_env
        )

        notion_toolset = McpToolset(
            connection_params=StdioConnectionParams(
                server_params=server_params,
                timeout=30.0  # Increased timeout for MCP server startup
            )
        )

        # Create agent with Notion tools
        agent = Agent(
            name="project_manager",
            model="gemini-2.5-flash",
            instruction=get_system_instruction(database_id=notion_database_id),
            description="Project manager for creating timelines, tasks, and organizing campaign deliverables with Notion integration",
            tools=[notion_toolset]
        )

        logger.info("Project Manager agent created with Notion MCP integration")

    return agent


# Create root_agent for A2A deployment
root_agent = create_project_manager_agent()


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
    logger.info(f"🚀 Starting Project Manager A2A Server on {PROTOCOL}://{HOST}:{PORT}")
    logger.info(f"📋 Agent card available at: {PROTOCOL}://{HOST}:{PORT}/.well-known/agent-card.json")
    logger.info(f"🌐 Public URL: {PROTOCOL}://{PUBLIC_HOST}:{PUBLIC_PORT}")

    uvicorn.run(a2a_app, host=HOST, port=PORT)
