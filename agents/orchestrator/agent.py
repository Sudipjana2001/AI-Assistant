"""
Orchestrator Agent
Routes queries to appropriate specialized agents
Coordinates multi-agent tasks
"""
from typing import Dict, List, Any
from agents.base.agent import BaseAgent, AgentResponse


class OrchestratorAgent(BaseAgent):
    """
    Orchestrator Agent - Routes queries to specialized agents
    """
    
    def __init__(self):
        super().__init__(
            name="Orchestrator",
            description="Routes queries to appropriate agents and coordinates multi-agent tasks"
        )
        self.agent_routing = {
            "sql": ["sql", "query", "database", "table", "select", "join"],
            "python": ["code", "python", "script", "analyze", "calculate", "plot", "visualize"],
            "researcher": ["research", "market", "trend", "competitor", "industry", "report"],
            "analyst": ["analyze", "statistics", "insight", "pattern", "correlation"],
            "writer": ["write", "report", "summary", "document", "executive"]
        }
    
    def _get_system_prompt(self) -> str:
        return """You are the Orchestrator Agent for a market research assistant.
Your role is to:
1. Understand user queries and route them to the appropriate specialized agent
2. Coordinate multi-step tasks across multiple agents
3. Aggregate results from multiple agents into coherent responses

Available agents:
- SQL Agent: For database queries and SQL generation
- Python Agent: For code execution and data analysis
- Researcher Agent: For market research and trend analysis
- Analyst Agent: For statistical analysis and insights
- Writer Agent: For report writing and documentation

When responding:
1. Identify which agent(s) should handle the query
2. If multiple agents needed, plan the workflow
3. Summarize the routing decision

IMPORTANT:
- Be concise (no fluff)
- At the end of your response, provide 2-3 short "Suggested Next Steps" or follow-up questions based on the conversation context.
- Format suggestions as a bulleted list titled "Suggestions:"
"""
    
    def _get_tools(self) -> List[Dict]:
        return [
            {
                "name": "route_to_agent",
                "description": "Route a query to a specialized agent",
                "parameters": {
                    "agent_name": "string",
                    "query": "string"
                }
            }
        ]
    
    def determine_agent(self, query: str) -> str:
        """Determine which agent should handle the query"""
        query_lower = query.lower()
        
        scores = {}
        for agent, keywords in self.agent_routing.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > 0:
                scores[agent] = score
        
        if scores:
            return max(scores, key=scores.get)
        return "researcher"  # Default to researcher for general queries
    
    async def execute(self, query: str, context: Dict = None) -> AgentResponse:
        """
        Execute orchestrator logic
        Routes to appropriate agent or handles multi-agent workflow
        """
        try:
            # Determine target agent
            target_agent = self.determine_agent(query)
            
            # Get the target agent from registry
            from agents.registry import AgentRegistry
            agent = AgentRegistry.get_agent(target_agent)
            
            if agent:
                # Execute target agent
                result = await agent.execute(query, context)
                return AgentResponse(
                    content=f"[Routed to {target_agent}]\n\n{result.content}",
                    agent_name=self.name,
                    sources=result.sources,
                    metadata={
                        "routed_to": target_agent,
                        "original_metadata": result.metadata
                    },
                    success=result.success
                )
            else:
                # Fallback to base execution
                return await super().execute(query, context)
                
        except Exception as e:
            return AgentResponse(
                content="",
                agent_name=self.name,
                success=False,
                error=str(e)
            )
