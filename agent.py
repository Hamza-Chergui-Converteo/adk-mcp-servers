import os
import asyncio
import warnings
import logging
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from mcp.client.stdio import StdioServerParameters
from schema_db import SCHEMA

# Ignore all warnings
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)

# Environment Configuration
def configure_environment():
    print("Configuring environment...")
    # API keys setup
    os.environ["GOOGLE_API_KEY"] = "AIzaSyBZWDdUAiOzcrKMs7_F_WUShbrcVajZepM"
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
    
    # Paths
    DB_PATH = os.path.abspath("db/crm.db")
    MCP_SERVER_PATH = os.path.abspath("mcp-server/sqlite")
    
    return DB_PATH, MCP_SERVER_PATH

# Define the crm Agent
def create_crm_agent(MCP_SERVER_PATH, DB_PATH):
    print("Creating crm agent...")
    AGENT_MODEL = "gemini-2.0-flash"  # Model constant


    crm_agent = Agent(
    name="CRM_SQLite_Agent",
    model=AGENT_MODEL,
        description=(
            "Agent CRM autonome et intelligent, conçu pour interagir directement avec une base de données SQLite. "
            "Il est capable d'interroger, modifier ou enrichir les données des prospects via le serveur MCP."
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
            Tu es un agent CRM autonome doté d'un accès direct à une base de données SQLite via le serveur MCP.

            Ta mission est de gérer efficacement les données CRM (prospects, interactions, etc.), en exécutant des requêtes SQL ou des modifications de manière pertinente et sécurisée.

            Voici le schéma actuel de la base de données, que tu dois respecter dans toutes tes opérations :
            {SCHEMA}

            Règles :
            - Assure-toi que toutes les requêtes respectent la structure et les contraintes du schéma.
            - Ne propose que des opérations utiles dans un contexte CRM.
            - Vérifie les données critiques avant toute modification ou suppression.
            - Sois clair et explicite dans tes réponses : décris ce que tu fais et pourquoi.

            Tu es un assistant CRM fiable, précis, et respectueux de la logique métier.
            """
    )




    print(f"Agent '{crm_agent.name}' created using model '{AGENT_MODEL}'.")
    return crm_agent

# Setup Session Service and Runner
async def setup_runner(crm_agent):
    print("Setting up session and runner...")
    session_service = InMemorySessionService()

    # Constants for session context
    APP_NAME = "crm_tutorial_app"
    USER_ID = "user_1"
    SESSION_ID = "session_001"

    # Create session
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

    # Runner setup
    runner = Runner(
        agent=crm_agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    print(f"Runner created for agent '{runner.agent.name}'.")
    return runner, USER_ID, SESSION_ID

# Define Agent Interaction Function
async def call_agent_async(query: str, runner, user_id, session_id):
    print(f"\n>>> User Query: {query}")
    content = types.Content(role='user', parts=[types.Part(text=query)])

    final_response_text = "Agent did not produce a final response."

    # Key Concept: run_async executes the agent logic and yields Events.
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            break

    print(f"<<< Agent Response: {final_response_text}")
    return final_response_text

# Function to continuously interact with the agent via terminal
async def interact_with_agent(runner, user_id, session_id):
    print("You can start chatting with the agent now. Type 'exit' to end the conversation.")
    while True:
        user_input = input("\n>>> Enter your message: ")
        if user_input.lower() == 'exit':
            print("Ending the conversation.")
            break
        response = await call_agent_async(user_input, runner, user_id, session_id)

# Main function
def main():
    # Configure the environment
    DB_PATH, MCP_SERVER_PATH = configure_environment()

    # Create the agent
    crm_agent = create_crm_agent(MCP_SERVER_PATH, DB_PATH)

    # Setup runner and session
    loop = asyncio.get_event_loop()
    runner, user_id, session_id = loop.run_until_complete(setup_runner(crm_agent))

    # Start interacting with the agent
    loop.run_until_complete(interact_with_agent(runner, user_id, session_id))

if __name__ == "__main__":
    main()
