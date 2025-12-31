import asyncio
import sys
import os

# Add backend and root to path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))
sys.path.insert(0, os.getcwd())

# Mock Azure modules
from unittest.mock import MagicMock
sys.modules['azure'] = MagicMock()
sys.modules['azure.core'] = MagicMock()
sys.modules['azure.core.credentials'] = MagicMock()
sys.modules['azure.search'] = MagicMock()
sys.modules['azure.search.documents'] = MagicMock()
sys.modules['azure.search.documents.models'] = MagicMock()
sys.modules['gremlin_python'] = MagicMock()
sys.modules['gremlin_python.driver'] = MagicMock()
sys.modules['gremlin_python.driver.client'] = MagicMock()
sys.modules['gremlin_python.driver.driver_remote_connection'] = MagicMock()
sys.modules['gremlin_python.process'] = MagicMock()
sys.modules['gremlin_python.process.anonymous_traversal'] = MagicMock()

async def verify_code_gen():
    print("🧪 Testing Metadata-Driven Code Generation")
    
    # 1. Test SQL Agent
    print("\n1. Testing SQL Agent...")
    try:
        from agents.sql_agent.agent import SQLAgent
        
        # Mock LLM to return a predictable response if it were real, 
        # but here we mainly check if the prompt construction works or if execution crashes.
        # Since we don't have a real LLM connected in this script without env vars,
        # we will check the agent's logic flow.
        
        # Actually, let's use the Orchestrator to route or just SQLAgent directly.
        agent = SQLAgent()
        
        # Mock LLM response
        mock_llm = MagicMock()
        future = asyncio.Future()
        future.set_result("SELECT * FROM sales WHERE amount > 1000;")
        mock_llm.simple_chat.return_value = future
        agent._llm = mock_llm
        
        # Inject metadata context simulating a "sales.csv" file
        context = {
            "rag_results": [{
                "title": "sales.csv", 
                "source": "blob/sales.csv",
                "content": "[METADATA ONLY]",
                "metadata": {"columns": ["id", "amount", "date"]}
            }],
            "schema": "Table: sales (derived from sales.csv)\nColumns: id, amount, date" # SQLAgent enhances prompt with this
        }
        
        response = await agent.execute("Show me high value sales", context)
        
        print(f"   Response: {response.content}")
        if "SELECT * FROM sales" in response.content:
            print("   ✅ SQL Generation Success (Mocked)")
        else:
            print("   ❌ Unexpected SQL Response")
            
    except Exception as e:
        print(f"   ❌ SQL Agent Error: {e}")
        import traceback
        traceback.print_exc()

    # 2. Test Python Agent
    print("\n2. Testing Python Agent...")
    try:
        from agents.python_agent.agent import PythonAgent
        p_agent = PythonAgent()
        
        mock_llm_p = MagicMock()
        future_p = asyncio.Future()
        future_p.set_result("```python\nimport pandas as pd\ndf = pd.read_csv('sales.csv')\nprint(df.head())\n```")
        mock_llm_p.simple_chat.return_value = future_p
        p_agent._llm = mock_llm_p
        
        response_p = await p_agent.execute("Analyze the sales data", context)
        
        print(f"   Response: {response_p.content}")
        if "pd.read_csv('sales.csv')" in response_p.content:
            print("   ✅ Python Generation Success (Mocked)")
        else:
            print("   ❌ Unexpected Python Response")

    except Exception as e:
        print(f"   ❌ Python Agent Error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_code_gen())
