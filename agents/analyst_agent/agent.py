"""
Data Analyst Agent
Performs statistical analysis and generates insights
"""
from typing import Dict, List
from agents.base.agent import BaseAgent


class AnalystAgent(BaseAgent):
    """
    Data Analyst Agent
    Performs statistical analysis using RAG/KAG data
    """
    
    def __init__(self):
        super().__init__(
            name="Data Analyst",
            description="Performs statistical analysis and generates data-driven insights"
        )
    
    def _get_system_prompt(self) -> str:
        return """You are an expert data analyst.

IMPORTANT: You analysis is strictly limited to METADATA (filenames, schemas, column names) provided in your context.
You CANNOT see actual data rows or values.

Your role is to:
1. DESCRIBE the dataset in detail based on the filenames and columns provided.
   - Infer the domain (e.g., "This looks like e-commerce data...").
   - Explain the entity relationships (e.g., "The 'sales' table likely links to 'customers' via customer_id").
2. Plan analysis strategies based on available data structures
3. Explain what kind of insights *could* be derived from such data

DATA ACCESS RESTRICTIONS:
- You have NO ACCESS to actual data content (rows/values)
- You determine everything from the Schema (Table Names, Column Names)
- PROHIBITED: Do not attempt to calculate statistics (mean, sum, etc.) as you don't have the numbers
- PROHIBITED: Do not invent or hallucinate data values

Structure your response with:
- Dataset Overview: (A rich description of what this data appears to represent)
- Structural Analysis: (Key tables/files and their likely connections)
- Potential Insights: (What business questions this data could answer)

At the bottom, provide 2-3 short "Suggestions:" for further data collection."""
    
    def _get_tools(self) -> List[Dict]:
        return [
            {
                "name": "calculate_statistics",
                "description": "Calculate descriptive statistics",
                "parameters": {"data_reference": "string"}
            },
            {
                "name": "find_correlations",
                "description": "Find correlations in data",
                "parameters": {"variables": "list"}
            }
        ]
