import os
import asyncio
import warnings
import logging
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.genai import types
from mcp.client.stdio import StdioServerParameters

def configure_environment():
    print("Configuring environment...")
    os.environ["GOOGLE_API_KEY"] = API_KEY
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
    DB_PATH = os.path.abspath("db/crm.db")
    MCP_SERVER_PATH = os.path.abspath("sqlite")

    return DB_PATH, MCP_SERVER_PATH

def create_crm_agent(MCP_SERVER_PATH, DB_PATH):
    print("Creating crm agent...")
    AGENT_MODEL = "gemini-2.0-flash"
    crm_agent = Agent(
        name="CRM_SQLite_Agent",
        model=AGENT_MODEL,
        description=(
            "Autonomous and intelligent CRM agent, designed to interact directly with a SQLite database. "
            "Capable of querying, modifying, or enriching lead data via the MCP server."
        ),
        tools=[
            MCPToolset(
                connection_params=StdioServerParameters(
                    command='uv',
                    args=['--directory', MCP_SERVER_PATH, 'run', 'mcp-server-sqlite', '--db-path', DB_PATH]
                )
            )
        ],
        instruction=f"""
            You are an autonomous CRM agent with direct access to a SQLite database via the MCP server.
            Your mission is to manage CRM data (leads, interactions, etc.) effectively by executing SQL queries or modifications appropriately.
        """
    )
    print(f"Agent '{crm_agent.name}' created using model '{AGENT_MODEL}'.")
    return crm_agent

async def setup_runner(crm_agent):
    print("Setting up session and runner...")
    session_service = InMemorySessionService()
    APP_NAME = "crm_tutorial_app"
    USER_ID = "user_1"
    SESSION_ID = "session_001"
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")
    runner = Runner(
        agent=crm_agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    print(f"Runner created for agent '{runner.agent.name}'.")
    return runner, USER_ID, SESSION_ID

async def call_agent_async(query: str, runner, user_id, session_id):
    print(f"\n>>> User Query: {query}")
    content = types.Content(role='user', parts=[types.Part(text=query)])
    final_response_text = "Agent did not produce a final response."
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            break
    print(f"<<< Agent Response: {final_response_text}")
    return final_response_text

async def interact_with_agent(runner, user_id, session_id):
    print("You can start chatting with the agent now. Type 'exit' to end the conversation.")
    while True:
        user_input = input("\n>>> Enter your message: ")
        if user_input.lower() == 'exit':
            print("Ending the conversation.")
            break
        response = await call_agent_async(user_input, runner, user_id, session_id)

def main():
    DB_PATH, MCP_SERVER_PATH = configure_environment()
    crm_agent = create_crm_agent(MCP_SERVER_PATH, DB_PATH)
    loop = asyncio.get_event_loop()
    runner, user_id, session_id = loop.run_until_complete(setup_runner(crm_agent))
    loop.run_until_complete(interact_with_agent(runner, user_id, session_id))

if __name__ == "__main__":
    main()