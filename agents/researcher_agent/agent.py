"""
Market Researcher Agent
Conducts market research using RAG/KAG data
"""
from typing import Dict, List
from agents.base.agent import BaseAgent, AgentResponse


class ResearcherAgent(BaseAgent):
    """
    Market Researcher Agent
    Uses RAG and KAG to conduct market research analysis
    """
    
    def __init__(self):
        super().__init__(
            name="Market Researcher",
            description="Conducts market research analysis using uploaded documents and knowledge graphs"
        )
    
    def _get_system_prompt(self) -> str:
        return """You are a concise market research expert.

IMPORTANT: You research is strictly limited to METADATA (titles, filenames, topics) provided in your context.
You CANNOT read the actual content of documents.

Your role is to:
1. Identify relevant documents based on their titles and metadata
2. Suggest what *topics* seem to be covered
3. Recommend which documents to open/read (for the user to do)

DATA ACCESS RESTRICTIONS:
- NO CONTENT ACCESS: You cannot summarize text you cannot see
- METADATA ONLY: You see filenames, properties, and labels
- PROHIBITED: Do not pretend to read the file content

If the user asks for a summary of a file, say: "I cannot read the file content directly. Based on the metadata (Title: ...), it appears to be relevant. Please open it to read details."

At the end of your response (except for simple greetings), provide 2-3 short "Suggestions:" for follow-up questions."""
    
    def _get_tools(self) -> List[Dict]:
        return [
            {
                "name": "search_documents",
                "description": "Search uploaded documents for relevant information",
                "parameters": {"query": "string"}
            },
            {
                "name": "analyze_trends",
                "description": "Analyze market trends from available data",
                "parameters": {"topic": "string"}
            }
        ]
