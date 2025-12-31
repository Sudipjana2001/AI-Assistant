# Agents - Market Research Multi-Agent System

This folder contains all agent implementations, separate from the backend API.

## Structure

```
agents/
├── base/           # Base agent class and common tools
├── orchestrator/   # Routes queries to appropriate agents
├── sql_agent/      # SQL query generation
├── python_agent/   # Python code execution
├── researcher_agent/ # Market research
├── analyst_agent/  # Data analysis
├── writer_agent/   # Report writing
└── registry.py     # Agent registration and factory
```

## Usage

```python
from agents.registry import AgentRegistry

# Initialize all agents
AgentRegistry.initialize()

# Get a specific agent
agent = AgentRegistry.get_agent("researcher")

# Execute a query
result = await agent.execute("Analyze market trends for AI")
```

## Adding New Agents

1. Create a new folder: `agents/new_agent/`
2. Create `agent.py` with a class inheriting from `BaseAgent`
3. Add tools in `tools.py`
4. Register in `registry.py`
