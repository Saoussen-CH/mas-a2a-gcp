"""
Test Notion MCP connection
"""
import os
import asyncio
from dotenv import load_dotenv
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from google.adk.agents import Agent
from mcp import StdioServerParameters

# Load environment variables
load_dotenv(dotenv_path="../../.env")

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

print(f"NOTION_API_KEY: {NOTION_API_KEY[:10]}..." if NOTION_API_KEY else "NOTION_API_KEY: None")
print(f"NOTION_DATABASE_ID: {NOTION_DATABASE_ID}")

async def test_notion_mcp():
    """Test connecting to Notion MCP server"""
    try:
        # Create server parameters
        server_params = StdioServerParameters(
            command="npx",
            args=[
                "-y",
                "@notionhq/notion-mcp-server"
            ],
            env={
                "NOTION_API_KEY": NOTION_API_KEY,
                "NOTION_DATABASE_ID": NOTION_DATABASE_ID,
            }
        )

        # Create MCP toolset with Notion server
        toolset = McpToolset(
            connection_params=StdioConnectionParams(
                server_params=server_params,
                timeout=10.0
            )
        )

        print("\n✓ MCP Toolset created successfully")

        # Create a test agent with the toolset
        agent = Agent(
            name="test_pm",
            model="gemini-2.5-flash",
            instruction="You are a test agent",
            tools=[toolset]
        )

        print("✓ Agent created with MCP toolset")

        # Get available tools
        tools = await toolset.get_tools()
        print(f"\n✓ Available tools: {len(tools)}")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description if hasattr(tool, 'description') else 'No description'}")

        print("\n✓ Notion MCP connection successful!")

    except Exception as e:
        print(f"\n✗ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_notion_mcp())
