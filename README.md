# MCP CRM Example with Google ADK

This repository demonstrates how to build an MCP (Model Context Protocol) server backed by a SQLite CRM database, and how to interact with it using a Gemini-powered agent via the Google Application Development Kit (ADK).

## 🚀 What is This Project?

- ✅ A ready-to-use MCP server using a SQLite CRM database
- 🤖 A custom Google ADK agent capable of querying, updating, and analyzing CRM data
- 💬 A simulated CLI chat interface to test interactions with the agent
- 🧰 A toolset of 6 MCP tools exposed to the agent (read, write, create, list tables, describe schema, add insights)

---

## 🧱 Project Structure

```
mcp-crm-project/
├── agent.py           # Main agent logic (Gemini + ADK)
├── db/
│   ├── setup_db.py    # Script to initialize the SQLite database
│   └── crm.db         # Auto-generated SQLite CRM database
├── sqlite/            # MCP server adapted from official repo
└── README.md          # You're here!
```

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Hamza-Chergui-Converteo/adk-mcp-servers.git
cd mcp-crm-project
```

### 2. Initialize the SQLite Database

```bash
cd db
python setup_db.py
```

This will create a `crm.db` file with mock data.

### 3. Add Your Gemini API Key

In `agent.py`, replace `YOUR_API_KEY` with your actual Google API key:

```python
os.environ["GOOGLE_API_KEY"] = "your-key-here"
```

---

## 🧠 Agent Toolset

The MCP server exposes 6 tools accessible by the agent:

### 🔍 Query Tools
- `read_query`: Run SELECT queries  
- `write_query`: INSERT, UPDATE, DELETE  
- `create_table`: Create new tables

### 🧾 Schema Tools
- `list_tables`: List all tables  
- `describe_table`: Get schema of a table

### 📊 Insight Tools
- `append_insight`: Add business insights to `memo://insights`

---

## 💬 Start Chatting with the Agent

Simply run:

```bash
python agent.py
```

You’ll enter a CLI chat with the CRM agent. Type your questions or SQL commands (e.g., *“list all prospects”*, *“add a new contact”*, etc.). Type `exit` to quit.

---

## 📚 Reference

This project is based on the official MCP servers repository:  
🔗 https://github.com/modelcontextprotocol/servers

Feel free to explore it for other backends (Redis, OpenAI, Slack, etc.).

