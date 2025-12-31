"""
Python Agent
Generates and executes Python code for data analysis
Uses sandbox for safe execution
"""
from typing import Dict, List
from agents.base.agent import BaseAgent, AgentResponse


class PythonAgent(BaseAgent):
    """
    Python Agent - Generates Python code for data analysis
    Can execute code in a sandboxed environment
    """
    
    def __init__(self):
        super().__init__(
            name="Python Agent",
            description="Generates Python code for data analysis and visualization"
        )
    
    def _get_system_prompt(self) -> str:
        return """You are a Python expert agent for data analysis.

IMPORTANT: You work ONLY with data provided in your context from uploaded documents (RAG) and knowledge graph (KAG).

Your role is to:
1. Generate Python code for data analysis based on the context provided
2. Create visualizations using matplotlib/seaborn
3. Process data that is already available in the context
4. Explain your code clearly

Available libraries:
- pandas (as pd)
- numpy (as np)
- matplotlib.pyplot (as plt)
- seaborn (as sns)

DATA ACCESS RESTRICTIONS:
- You CANNOT read files directly from disk (e.g., no `open()`, no absolute paths)
- You SHOULD generate code that assumes data is loaded into pandas DataFrames based on filenames
  - Example: For "sales.csv", assume a dataframe `df_sales` exists or write code to load it: `df_sales = pd.read_csv('sales.csv')`
- EXPLAIN that this code is for the user to run, or for a secure execution environment (if available)
- ONLY use the metadata (columns, types) provided to ensure your code uses correct field names
- If no columns are known, infer generic ones and comment them

Guidelines:
- Write clean, well-commented code
- Handle edge cases and errors
- Use vectorized operations for performance
- Create clear visualizations with labels
- Reference the source of any data you use

Format your response as:
1. Python code in a code block (working with context data)
2. Expected output description

At the bottom, provide 2-3 short "Suggestions:" for follow-up analysis."""
    
    def _get_tools(self) -> List[Dict]:
        return [
            {
                "name": "generate_code",
                "description": "Generate Python code for a task",
                "parameters": {"task": "string"}
            },
            {
                "name": "execute_code",
                "description": "Execute Python code in sandbox",
                "parameters": {"code": "string"}
            }
        ]
    
    async def execute(self, query: str, context: Dict = None) -> AgentResponse:
        """Generate Python code for data analysis"""
        # Add data context if available
        enhanced_query = query
        if context and "data_summary" in context:
            enhanced_query += f"\n\nData available:\n{context['data_summary']}"
        
        return await super().execute(enhanced_query, context)
