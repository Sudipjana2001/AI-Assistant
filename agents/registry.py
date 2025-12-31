"""
Agent Registry
Central registry for all available agents
"""
from typing import Dict, Optional, List
from agents.base.agent import BaseAgent


class AgentRegistry:
    """
    Central registry for all agents
    Supports lazy initialization and dynamic agent registration
    """
    
    _agents: Dict[str, BaseAgent] = {}
    _initialized: bool = False
    
    @classmethod
    def initialize(cls):
        """Initialize all agents"""
        if cls._initialized:
            return
        
        print("Initializing agent registry...")
        
        # Import and register agents
        try:
            from agents.orchestrator.agent import OrchestratorAgent
            cls._agents["orchestrator"] = OrchestratorAgent()
        except ImportError as e:
            print(f"Could not load OrchestratorAgent: {e}")
        
        try:
            from agents.sql_agent.agent import SQLAgent
            cls._agents["sql"] = SQLAgent()
        except ImportError as e:
            print(f"Could not load SQLAgent: {e}")
        
        try:
            from agents.python_agent.agent import PythonAgent
            cls._agents["python"] = PythonAgent()
        except ImportError as e:
            print(f"Could not load PythonAgent: {e}")
        
        try:
            from agents.researcher_agent.agent import ResearcherAgent
            cls._agents["researcher"] = ResearcherAgent()
        except ImportError as e:
            print(f"Could not load ResearcherAgent: {e}")
        
        try:
            from agents.analyst_agent.agent import AnalystAgent
            cls._agents["analyst"] = AnalystAgent()
        except ImportError as e:
            print(f"Could not load AnalystAgent: {e}")
        
        try:
            from agents.writer_agent.agent import WriterAgent
            cls._agents["writer"] = WriterAgent()
        except ImportError as e:
            print(f"Could not load WriterAgent: {e}")
        
        cls._initialized = True
        print(f"Initialized {len(cls._agents)} agents: {list(cls._agents.keys())}")
    
    @classmethod
    def get_agent(cls, name: str) -> Optional[BaseAgent]:
        """Get an agent by name"""
        if not cls._initialized:
            cls.initialize()
        return cls._agents.get(name)
    
    @classmethod
    def list_agents(cls) -> List[str]:
        """List all available agent names"""
        if not cls._initialized:
            cls.initialize()
        return list(cls._agents.keys())
    
    @classmethod
    def get_all_agents(cls) -> Dict[str, BaseAgent]:
        """Get all agents"""
        if not cls._initialized:
            cls.initialize()
        return cls._agents.copy()
    
    @classmethod
    def register_agent(cls, name: str, agent: BaseAgent):
        """Register a new agent"""
        cls._agents[name] = agent
        print(f"Registered agent: {name}")
    
    @classmethod
    def unregister_agent(cls, name: str) -> bool:
        """Unregister an agent"""
        if name in cls._agents:
            del cls._agents[name]
            print(f"Unregistered agent: {name}")
            return True
        return False
