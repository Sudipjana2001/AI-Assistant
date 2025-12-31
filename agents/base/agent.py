"""
Base Agent Class
All agents inherit from this class
Uses Azure AI Foundry SDK for LLM operations
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


@dataclass
class AgentResponse:
    """Standard response from an agent"""
    content: str
    agent_name: str
    sources: List[str] = None
    metadata: Dict[str, Any] = None
    success: bool = True
    error: Optional[str] = None


class BaseAgent(ABC):
    """
    Abstract base class for all agents
    
    SECURITY: Data access is restricted to DataAccessLayer only.
    Agents can ONLY access data through:
    - RAG (Azure AI Search) 
    - KAG (Cosmos DB Gremlin)
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self._llm = None
        self._data_layer = None
    
    @property
    def llm(self):
        """Lazy load LLM client"""
        if self._llm is None:
            self._llm = self._initialize_llm()
        return self._llm
    
    def _initialize_llm(self):
        """Initialize Azure AI Foundry LLM client"""
        try:
            from app.core.azure_client import get_ai_client
            return get_ai_client()
        except ImportError:
            print(f"Warning: Could not import Azure client for {self.name}")
            return None
    
    @property
    def data_layer(self):
        """
        Secure Data Access Layer - the ONLY way to access data.
        
        This enforces that all data access goes through:
        - RAG (Azure AI Search)
        - KAG (Cosmos DB Gremlin)
        
        No direct file access. No direct database queries.
        """
        if self._data_layer is None:
            try:
                from app.core.data_access import get_data_access_layer
                self._data_layer = get_data_access_layer()
            except ImportError as e:
                print(f"Warning: DataAccessLayer not available: {e}")
        return self._data_layer
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Get the system prompt for this agent"""
        pass
    
    @abstractmethod
    def _get_tools(self) -> List[Dict]:
        """Get the tools available to this agent"""
        pass
    
    def _get_data_access_policy(self) -> str:
        """Standard data access policy for all agents"""
        return """
DATA ACCESS POLICY:
- You ONLY have access to data retrieved from the knowledge base
- Data sources: Uploaded Documents (RAG) and Knowledge Graph (KAG)
- You CANNOT access local files, databases, or external APIs directly
- When referencing data, always indicate its source
- If asked about data not in your context, say you don't have access to it
"""
    
    async def retrieve_context(self, query: str) -> Dict[str, Any]:
        """
        Retrieve context from RAG and KAG directly (using secured retrievers).
        
        This enables agents to have direct access to metadata services
        as requested by the user, while still being safe because the
        retrievers themselves are configured to only fetch metadata.
        """
        context = {
            "rag_results": [],
            "kag_results": [],
            "sources_used": [],
            "context_text": ""
        }
        
        try:
            # DIRECT ACCESS: Instantiate retrievers directly
            from app.rag.retriever import RAGRetriever
            from app.kag.graph_retriever import KAGRetriever
            
            # 1. Direct RAG Access (Metadata Only)
            rag = RAGRetriever()
            rag_docs = await rag.retrieve(query)
            
            if rag_docs:
                context["rag_results"] = rag_docs
                context["sources_used"].append("Azure AI Search (Direct Metadata)")
                
            # 2. Direct KAG Access (Graph Structure Only)
            kag = KAGRetriever()
            kag_entities = await kag.retrieve(query)
            
            if kag_entities:
                context["kag_results"] = kag_entities
                context["sources_used"].append("Cosmos DB Gremlin (Direct Graph)")
            
            # Build context text from results
            context_parts = ["=== AVAILABLE METADATA (Direct Access) ==="]
            
            if rag_docs:
                context_parts.append("\n📁 Documents (Metadata):")
                for doc in rag_docs[:5]:
                    title = doc.get('title', 'Unknown')
                    fname = doc.get('metadata_storage_name', 'Unknown File')
                    context_parts.append(f"  - [Doc] {title} ({fname})")

            if kag_entities:
                context_parts.append("\n🔗 Knowledge Graph (Structure):")
                for entity in kag_entities[:5]:
                    name = entity.get('name', 'Unknown')
                    label = entity.get('label', 'Entity')
                    context_parts.append(f"  - [Graph] {label}: {name}")
            
            if not rag_docs and not kag_entities:
                context_parts.append("No relevant metadata found.")
                
            context["context_text"] = "\n".join(context_parts)
                
        except Exception as e:
            print(f"Direct retrieval error: {e}")
        
        return context
    
    async def execute(self, query: str, context: Dict = None) -> AgentResponse:
        """
        Execute the agent with a query
        
        Args:
            query: User query or task
            context: Optional additional context
            
        Returns:
            AgentResponse with results
        """
        try:
            # Retrieve relevant context from RAG/KAG via secure DataAccessLayer
            retrieved_context = await self.retrieve_context(query)
            
            # Merge with provided context
            full_context = {**(context or {}), **retrieved_context}
            
            # Build prompt with data access policy first
            system_prompt = self._get_data_access_policy() + "\n" + self._get_system_prompt()
            
            # Add retrieved context (with source attribution)
            if retrieved_context.get("context_text"):
                system_prompt += f"\n\n{retrieved_context['context_text']}"
            elif retrieved_context["rag_results"]:
                # Fallback for backward compatibility
                rag_text = "\n".join([str(r) for r in retrieved_context["rag_results"][:5]])
                system_prompt += f"\n\nRelevant information from uploaded documents:\n{rag_text}"
            
            # Add conversation history if available
            if full_context.get("conversation_history"):
                system_prompt += f"\n\nConversation History:\n{full_context['conversation_history']}"
            
            # Execute with LLM
            if self.llm:
                try:
                    response = await self.llm.simple_chat(
                        user_message=query,
                        system_message=system_prompt
                    )
                except Exception as llm_error:
                    print(f"LLM execution error: {llm_error}")
                    response = f"[{self.name}] I'm having trouble connecting to the AI service. Error: {str(llm_error) or 'Unknown'}"
            else:
                # Provide a meaningful fallback response
                response = f"Hello! I'm the {self.name} agent. I understood your query: '{query}'\n\n"
                response += "However, the AI model is not currently available. "
                response += "Please ensure Azure OpenAI is properly configured.\n\n"
                if retrieved_context.get("rag_results"):
                    response += f"I found {len(retrieved_context['rag_results'])} relevant documents that might help."
            
            # Include sources used in response metadata
            sources_used = retrieved_context.get("sources_used", [])
            
            return AgentResponse(
                content=response,
                agent_name=self.name,
                sources=sources_used + [str(r.get("title", r.get("content", "")[:50])) for r in retrieved_context.get("rag_results", [])[:3]],
                metadata={
                    "context_used": bool(retrieved_context["rag_results"]),
                    "sources_used": sources_used,
                    "data_access": "RAG/KAG only"
                },
                success=True
            )
            
        except Exception as e:
            error_msg = str(e) if str(e) else f"Unknown error in {self.name} agent"
            print(f"Agent execution error: {error_msg}")
            return AgentResponse(
                content=f"I apologize, I encountered an issue: {error_msg}",
                agent_name=self.name,
                success=False,
                error=error_msg
            )
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}')>"
