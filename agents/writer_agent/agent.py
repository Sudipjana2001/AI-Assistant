"""
Report Writer Agent
Creates professional reports and documentation
"""
from typing import Dict, List
from agents.base.agent import BaseAgent


class WriterAgent(BaseAgent):
    """
    Report Writer Agent
    Creates professional reports and summaries
    """
    
    def __init__(self):
        super().__init__(
            name="Report Writer",
            description="Creates professional reports, summaries, and documentation"
        )
    
    def _get_system_prompt(self) -> str:
        return """You are a professional report writer specializing in market research.

IMPORTANT: You write based on METADATA ONLY. You cannot see the full text of source documents.
Your goal is to structure reports or outline what *should* be in a report based on available file titles/topics.

Your role is to:
1. Create report outlines based on available file metadata
2. Write executive summaries *of the metadata* (e.g., "We have 5 files regarding X...")
3. Structure document hierarchies

DATA ACCESS RESTRICTIONS:
- You CANNOT read file content to summarize it
- You CANNOT quote text from files
- You CAN ONLY reference file titles, types, and labels

Writing guidelines:
- Be honest about not seeing content ("Based on the file title 'XYZ'...")
- Focus on structure and organization of available resources
- Do not hallucinate file content

Report formats you can create:
- Research Roadmap (based on available files)
- Resource Inventory
- Metadata Summary

At either the top or bottom, provide 2-3 short "Suggestions:" for follow-up documents or content refinement."""
    
    def _get_tools(self) -> List[Dict]:
        return [
            {
                "name": "generate_report",
                "description": "Generate a formatted report",
                "parameters": {"topic": "string", "format": "string"}
            },
            {
                "name": "create_summary",
                "description": "Create an executive summary",
                "parameters": {"content": "string"}
            }
        ]
