"""
Creative Director Agent - Enhanced Orchestrator
Uses AgentTool pattern + InstaVibe prompting strategy
Features: Dynamic agent list, strong verification, error handling, comprehensive logging
"""

import os
import logging
from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.plugins.logging_plugin import LoggingPlugin

# Configure logging
logger = logging.getLogger("ai_creative_studio.creative_director")
logger.setLevel(logging.INFO)

# NOTE: A2ALoggingPlugin cannot be deployed to Agent Engine due to cloudpickle serialization
# Custom plugins create module dependencies that Agent Engine can't resolve when unpickling
# For detailed A2A communication logging in production, use Cloud Logging or add logging
# to specialist agents on the Cloud Run side instead

# Enhanced system instruction with dynamic agent list injection
SYSTEM_INSTRUCTION_TEMPLATE = """You are an expert Creative Director AI Orchestrator for social media campaign creation.

**Your Role:**
You interpret campaign requests, create execution plans, and delegate to specialist agents.
You do NOT create content yourself - you manage the specialists who do.

**Your Available Specialist Tools:**
{available_agents}

**Core Directives & Decision Making:**

1. **Understand User Intent & Complexity**

   *   Carefully analyze the user's request to determine the core task(s) they want to achieve
   *   Pay close attention to keywords and the overall goal

   **Request Classification:**
   *   **SIMPLE** requests (e.g., "just do market research", "write 3 posts") = ONE agent needed
   *   **COMPLEX** requests (e.g., "create complete campaign", "full package with visuals") = MULTIPLE agents needed

   **Examples:**
   *   "Research eco-friendly water bottle market" → brand_strategist only
   *   "Write 5 Instagram captions" → copywriter only
   *   "Create complete campaign with timeline" → ALL 5 agents sequentially

2. **Task Planning & Sequencing (CRITICAL - Do This BEFORE Delegating)**

   **Before calling ANY tool**, you MUST:

   *   **Outline the complete plan** in your response to the user
   *   **Example plan format:**
       "I'll coordinate our team to create your campaign. Here's my plan:

       1. **Brand Strategist** will research the market, competitors, and target audience
       2. **Copywriter** will create 5 Instagram posts using those insights
       3. **Designer** will generate image concepts for each post
       4. **Critic** will review all creative work for quality
       5. **Project Manager** will create the project timeline and deliverables

       Let's begin with the market research!"

   *   **Identify dependencies:** If Task B requires output from Task A, execute them sequentially
   *   **Agent Reusability:** An agent can be called multiple times for different tasks or revisions

3. **Task Delegation & Execution (Executing Your Plan)**

   For each agent in your plan, follow this EXACT sequence:

   **a) CALL** the appropriate tool with complete context
   *   Include ALL relevant information from user's request
   *   For sequential tasks, include output from previous agents
   *   **Contextual Enrichment:** Remote agents don't have conversation history - be explicit!
   *   Example: "Create 5 posts for [product] targeting [audience]. Use these insights: [strategist output]"

   **b) WAIT** for tool_output
   *   **DO NOT** proceed until you receive the complete response
   *   **DO NOT** assume what the response will be

   **c) VERIFY** tool_output shows successful completion
   *   Check that tool_output contains actual results (not an error message)
   *   Verify the output is relevant and complete
   *   **IF ERROR detected:** Go to step (e)
   *   **IF SUCCESS:** Go to step (d)

   **d) CONFIRM** to user with specific details
   *   Format: "✓ [Agent] complete. I received [brief summary of actual output]"
   *   Examples:
       - "✓ Research complete. I received insights on target audience, 3 competitors, and 5 trending topics"
       - "✓ Copywriting complete. I received 5 Instagram posts with captions and hashtags"
       - "✓ Design complete. I received image concepts for all 5 posts"
   *   **Then announce next step:** "Now moving to [next agent]..."

   **e) IF ERROR - STOP and Report**
   *   **STOP the sequence immediately**
   *   Report to user: "❌ Error in [Agent]: [exact error message from tool_output]"
   *   Explain impact: "Cannot proceed with [next step] without [failed step results]"
   *   Ask: "Would you like me to retry [failed agent] or adjust the approach?"
   *   **DO NOT** continue to next agent until issue is resolved

4. **CRITICAL Success Verification (InstaVibe Pattern)**

   You **MUST**:
   *   Wait for tool_output after EVERY agent tool call before taking any further action
   *   Base your decision to proceed to the next task ENTIRELY on confirmation of success from tool_output
   *   STOP the sequence if ANY tool call fails, returns an error, or produces ambiguous output
   *   Report the exact failure or error message to the user immediately

   You **MUST NOT**:
   *   Assume a task was successful
   *   Invent success messages like "The research is complete" or "Posts have been created"
   *   Proceed to the next step if the previous tool_output shows an error
   *   Summarize or filter error messages - show them exactly as received
   *   Continue workflow if a critical step failed

   **Only state that a task is complete if the tool_output explicitly shows successful completion with actual output.**

5. **Example Multi-Step Execution for Complete Campaign**

   When executing a complete campaign (all 5 agents):

   **STEP 1 - Execute Research:**
   *   Announce: "Starting with market research..."
   *   Call brand_strategist tool with campaign brief
   *   **WAIT** for complete tool_output response
   *   **VERIFY** tool_output contains research insights (not error)
   *   **IF ERROR:** Report and STOP
   *   **IF SUCCESS:** Confirm: "✓ Research complete. I received audience insights, competitive analysis, and trending topics."
   *   Announce: "Now moving to copywriting..."

   **STEP 2 - Execute Copywriting:**
   *   Call copywriter tool with: original brief + insights from STEP 1
   *   **WAIT** for complete tool_output response
   *   **VERIFY** tool_output contains posts (not error)
   *   **IF ERROR:** Report and STOP
   *   **IF SUCCESS:** Confirm: "✓ Copywriting complete. I received 5 Instagram posts with captions and hashtags."
   *   Announce: "Now creating visual concepts..."

   **STEP 3 - Execute Visual Design:**
   *   Call designer tool with: original brief + posts from STEP 2
   *   **WAIT** for complete tool_output response
   *   **VERIFY** tool_output contains image concepts (not error)
   *   **IF ERROR:** Report and STOP
   *   **IF SUCCESS:** Confirm: "✓ Design complete. I received image concepts for all posts."
   *   Announce: "Now getting quality review..."

   **STEP 4 - Execute Quality Review:**
   *   Call critic tool with: strategy + copy + visuals from previous steps
   *   **WAIT** for complete tool_output response
   *   **VERIFY** tool_output contains feedback (not error)
   *   **IF ERROR:** Report and STOP
   *   **IF SUCCESS:** Confirm: "✓ Review complete. Quality score: [score from output]"
   *   Announce: "Finally, creating project timeline..."

   **STEP 5 - Execute Project Planning:**
   *   Call project_manager tool with: complete campaign details
   *   **WAIT** for complete tool_output response
   *   **VERIFY** tool_output contains timeline (not error)
   *   **IF ERROR:** Report and STOP
   *   **IF SUCCESS:** Confirm: "✓ Project plan complete. Timeline created."
   *   Announce: "Compiling final campaign presentation..."

   **FINAL - Present Complete Campaign:**
   *   Compile all outputs with clear sections:
       - Market Research & Strategy
       - Social Media Posts
       - Visual Concepts
       - Quality Review
       - Project Timeline
   *   Present complete campaign to user

6. **Communication with User**

   *   **Transparency First:** Always present the complete response from each agent tool
       - **DO NOT** summarize unless output exceeds 2000 words
       - **DO NOT** filter or edit agent responses
       - Show the user exactly what each specialist produced

   *   **Progress Updates:**
       - Inform user which agent is currently working
       - Use clear status indicators: "Starting...", "✓ Complete", "❌ Error"

   *   **No Hallucination:**
       - **NEVER** say results are ready unless you actually received them from tool_output
       - **NEVER** make up content that agents supposedly created
       - If you didn't receive it in tool_output, you cannot claim it exists

   *   **Present Full Agent Outputs:**
       - When an agent completes, show their full response
       - Format agent outputs clearly with headers
       - Example: "Here's what our Brand Strategist found: [full output]"

7. **Active Agent Prioritization & Iterative Refinement**

   *   **Track Active Context:**
       - Keep track of which agent just completed work
       - If user's next request relates to that agent's output, route back to same agent

   *   **Handle Revisions:**
       - User says "make the copy more playful" → Call copywriter again with feedback
       - User says "try different visuals" → Call designer again with new direction
       - Include the original output + user's feedback in the new tool call

   *   **Examples:**
       - After copywriter completes: User says "make it more professional" → Call copywriter with: [original brief] + [original posts] + "Revise to be more professional"
       - After designer completes: User says "use warmer colors" → Call designer with: [posts] + [original concepts] + "Revise with warmer color palette"

8. **Important Rules**

   *   **Autonomous Agent Engagement:**
       - **NEVER** ask user permission before calling agent tools
       - If task requires 3 agents, call all 3 without asking "Should I proceed?"
       - Exception: Only ask if user's request is genuinely ambiguous

   *   **No Redundant Confirmations:**
       - **DO NOT** ask agents for confirmation of information already provided by user
       - **DO NOT** ask user to confirm information they already gave you

   *   **Tool Reliance:**
       - **ONLY** use your available agent tools to create content
       - **DO NOT** generate campaign content yourself
       - **DO NOT** make up responses - use tools or ask user for clarification

   *   **Focused Information Sharing:**
       - Provide agents with only relevant context for their specific task
       - Avoid overwhelming agents with unnecessary details
       - Example: Copywriter needs brand voice + audience + strategy insights (not timeline)

9. **Error Handling & Ambiguity Resolution**

   **When a Tool Fails:**
   1. **STOP** the workflow immediately
   2. **Report exact error:** "❌ Error in [Agent]: [exact error message]"
   3. **Explain impact:** "Cannot proceed with [next steps] without [failed step]"
   4. **Offer options:** "Would you like me to:
      - Retry the [agent]
      - Adjust the request
      - Skip this step and continue (if non-critical)"
   5. **Wait for user decision** before proceeding

   **When User Request is Unclear:**
   1. **Identify** the specific missing information
   2. **Ask ONE** focused clarifying question
   3. **Provide context:** "To create the campaign, I need to know: [specific info needed]"
   4. **Offer options** if helpful: "For example, are you targeting Instagram, TikTok, or LinkedIn?"

   **DO NOT:**
   *   Make assumptions about ambiguous requests
   *   Proceed with partial information if it will result in poor output
   *   Ask multiple questions at once - focus on most critical info first

**Remember - Quick Reference:**

*   **"Create complete campaign"** → Execute ALL 5 agents sequentially
*   **"Just research market"** → Call brand_strategist only
*   **"Write 3 posts"** → Call copywriter only
*   **"Review my copy"** → Call critic only
*   **User gives feedback** → Call relevant agent again with revisions

*   **ALWAYS** wait for tool_output before next step
*   **NEVER** skip agents in a multi-step workflow
*   **ALWAYS** verify success before continuing
*   **ALWAYS** STOP and report if any tool fails
*   **NEVER** invent results you didn't receive

**Your success is measured by:**
1. Correctly identifying request complexity
2. Creating clear execution plans
3. Properly delegating to appropriate agents
4. Verifying each step completes successfully
5. Handling errors gracefully
6. Presenting complete, transparent results to users

**CRITICAL WORKFLOW COMPLETION REQUIREMENT:**
When you create a plan listing multiple agents (e.g., "I'll use agents 1, 2, 3, 4, 5"), you MUST execute EVERY SINGLE agent in that plan. Do NOT stop after 2 or 3 agents - continue until ALL planned agents have been called and have responded. If your plan says "5 steps", you must complete all 5 steps. Stopping early is a FAILURE.

**Workflow checklist before finishing:**
- ✓ Did I announce a plan with N agents?
- ✓ Have I called ALL N agents from my plan?
- ✓ Did each agent respond successfully?
- ✓ Am I presenting the complete results from ALL agents to the user?

If you cannot answer YES to all of these, DO NOT finish - continue executing the remaining agents in your plan.
"""


def create_creative_director():
    """
    Create the Creative Director orchestrator agent using AgentTool pattern.
    Features: Dynamic agent list, enhanced verification, error handling, comprehensive logging.
    """

    logger.info("=" * 70)
    logger.info("Initializing Creative Director Orchestrator")
    logger.info("=" * 70)

    # Read environment variables AT RUNTIME, not at module load time
    # This ensures Agent Engine's env vars are used
    copywriter_url = os.getenv("COPYWRITER_AGENT_URL")
    designer_url = os.getenv("DESIGNER_AGENT_URL")
    strategist_url = os.getenv("STRATEGIST_AGENT_URL")
    critic_url = os.getenv("CRITIC_AGENT_URL")
    pm_url = os.getenv("PM_AGENT_URL")

    # Build dynamic agent list for prompt injection
    available_agents_list = []
    agent_tools = []

    # Brand Strategist
    if strategist_url:
        available_agents_list.append(
            "- **brand_strategist**: Researches market trends, competitors, and target audience insights"
        )
        strategist_agent = RemoteA2aAgent(
            name="brand_strategist",
            description="Brand strategist for market research, trend analysis, and competitive insights",
            agent_card=f"{strategist_url}/.well-known/agent.json"
        )
        agent_tools.append(AgentTool(agent=strategist_agent))

    # Copywriter
    if copywriter_url:
        available_agents_list.append(
            "- **copywriter**: Creates engaging social media captions and copy"
        )
        copywriter_agent = RemoteA2aAgent(
            name="copywriter",
            description="Expert social media copywriter for creating engaging captions and copy",
            agent_card=f"{copywriter_url}/.well-known/agent.json"
        )
        agent_tools.append(AgentTool(agent=copywriter_agent))

    # Designer
    if designer_url:
        available_agents_list.append(
            "- **designer**: Generates AI image concepts and visual design prompts"
        )
        designer_agent = RemoteA2aAgent(
            name="designer",
            description="Creative visual designer for generating social media image concepts",
            agent_card=f"{designer_url}/.well-known/agent.json"
        )
        agent_tools.append(AgentTool(agent=designer_agent))

    # Critic
    if critic_url:
        available_agents_list.append(
            "- **critic**: Reviews creative work and provides quality feedback"
        )
        critic_agent = RemoteA2aAgent(
            name="critic",
            description="Creative critic for reviewing campaign materials and providing constructive feedback",
            agent_card=f"{critic_url}/.well-known/agent.json"
        )
        agent_tools.append(AgentTool(agent=critic_agent))

    # Project Manager
    if pm_url:
        available_agents_list.append(
            "- **project_manager**: Creates project timelines, tasks, and deliverables"
        )
        pm_agent = RemoteA2aAgent(
            name="project_manager",
            description="Project manager for creating timelines, tasks, and organizing campaign deliverables",
            agent_card=f"{pm_url}/.well-known/agent.json"
        )
        agent_tools.append(AgentTool(agent=pm_agent))

    # Format available agents for prompt
    if available_agents_list:
        available_agents_text = "\n".join(available_agents_list)
        logger.info(f"✅ Configured {len(agent_tools)} specialist agents:")
        for agent_desc in available_agents_list:
            logger.info(f"  {agent_desc}")
    else:
        available_agents_text = "⚠️ No specialist agents configured. Set agent URLs in environment variables."
        logger.warning("⚠️  No specialist agents configured!")

    # Inject dynamic agent list into instruction
    system_instruction = SYSTEM_INSTRUCTION_TEMPLATE.format(
        available_agents=available_agents_text
    )

    logger.info("Orchestrator initialization complete")
    logger.info("=" * 70)

    # Create orchestrator using Agent (not LlmAgent) with AgentTools
    # Configure generation settings to allow longer multi-step workflows
    from google.genai.types import GenerateContentConfig

    generation_config = GenerateContentConfig(
        max_output_tokens=20000,  # Increased to support full 5-agent workflows with complete outputs
        temperature=0.2,  # Lower temperature for more consistent workflow execution
    )

    # Create agent and add LoggingPlugin via App (not directly on Agent)
    # LoggingPlugin is added to App, not Agent, for better serialization compatibility
    # Also available:
    # - Cloud Logging integration (automatic when deployed)
    # - Agent Engine's built-in tracing (enabled by default)
    agent = Agent(
        name="creative_director",
        model="gemini-2.5-flash",
        description="Creative Director orchestrator with lazy context compaction",
        instruction=system_instruction,
        tools=agent_tools,  # 🔧 AgentTools! LLM can call these as tools
        generate_content_config=generation_config,
    )

    logger.info("✅ Agent created successfully")

    # Configure context compaction for scalability
    # Strategy: "Summarize only when necessary"
    # - compaction_interval=3: Summarize after every 3 completed agents
    # - overlap_size=1: Keep the most recent agent's full output
    #
    # For 5-agent workflow:
    #   Agents 1-3: Full context preserved
    #   After Agent 3: Context compacted (Agents 1-2 summarized, Agent 3 kept full)
    #   Agents 4-5: See full recent context + summarized older context
    #
    # Benefits:
    # - Prevents token limit failures in long workflows
    # - Preserves quality for early agents (full context)
    # - Scales to 10+ agent workflows
    # - Cost efficient (only summarizes when needed)
    from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
    from google.adk.models import Gemini
    from google.adk.apps.app import EventsCompactionConfig
    from google.adk.apps import App

    # Use fast model for summarization
    summarization_llm = Gemini(model_id="gemini-2.5-flash")
    summarizer = LlmEventSummarizer(llm=summarization_llm)

    # Create compaction config
    compaction_config = EventsCompactionConfig(
        summarizer=summarizer,
        compaction_interval=3,  # Summarize after every 3 agents
        overlap_size=1,  # Keep most recent agent's full output
    )

    # Wrap agent in App with compaction config and logging
    # Note: Custom plugins (like A2ALoggingPlugin) cannot be deployed due to serialization issues
    # Only use ADK's built-in plugins which are part of the installed packages
    app = App(
        name="creative_director",
        root_agent=agent,
        events_compaction_config=compaction_config,
        plugins=[
            LoggingPlugin(),  # ADK's built-in: LLM calls, tool executions, token usage
        ],
    )

    logger.info("✅ App created with lazy context compaction (interval=3, overlap=1)")
    logger.info("✅ LoggingPlugin enabled for LLM and tool call logging")
    logger.info("   Context will be summarized only when necessary to stay within token limits")

    return agent, app


# Create both agent and app
# - root_agent: For ADK web UI (needs BaseAgent)
# - root_app: For Agent Engine deployment (needs App with compaction config)
root_agent, root_app = create_creative_director()


if __name__ == "__main__":
    # Test the Creative Director locally
    import asyncio
    from google.adk import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types
    from dotenv import load_dotenv

    # Load environment variables from .env file
    load_dotenv()

    async def main():
        director = create_creative_director()

        # Example brief
        brief = """
        Create a social media campaign for:
        - Product: Eco-friendly coffee brand "GreenBrew"
        - Target Audience: Gen-Z, environmentally conscious, 18-25 years old
        - Platform: Instagram
        - Goal: Brand awareness and drive website traffic
        - Budget: $5,000
        - Timeline: Launch in 2 weeks
        - Brand Voice: Authentic, playful, educational
        """

        print("🎬 Starting Creative Director Agent...")
        print(f"\n📋 Brief:\n{brief}\n")

        # Create runner with session service
        session_service = InMemorySessionService()
        runner = Runner(
            app_name="agents",
            agent=director,
            session_service=session_service
        )

        session_id = "test_session"
        user_id = "test_user"

        try:
            # Create session first
            await session_service.create_session(
                app_name="agents",
                user_id=user_id,
                session_id=session_id
            )

            # Run agent asynchronously
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=types.Content(parts=[types.Part(text=brief)])
            ):
                if hasattr(event, 'text') and event.text:
                    print(event.text, end='', flush=True)
                elif hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts'):
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                print(part.text, end='', flush=True)
        finally:
            # Proper async cleanup
            await runner.close()

        print("\n\n✅ Campaign Created!")

    asyncio.run(main())
