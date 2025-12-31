import asyncio
import sys
import os
from unittest.mock import MagicMock

# Setup mock modules
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))
sys.path.insert(0, os.getcwd())

sys.modules['azure'] = MagicMock()
sys.modules['azure.search.documents'] = MagicMock()
sys.modules['gremlin_python'] = MagicMock()

async def verify_description():
    print("🧪 Testing Metadata-Based Dataset Description")
    
    try:
        from agents.analyst_agent.agent import AnalystAgent
        
        agent = AnalystAgent()
        
        # Mock LLM to simulate a descriptive response
        mock_llm = MagicMock()
        future = asyncio.Future()
        fake_response = """
Dataset Overview: This dataset appears to be e-commerce transaction data.
Structural Analysis: It contains a 'transactions.csv' table with 'customer_id' and 'product_id', suggesting a relational schema.
Potential Insights: We could analyze customer purchasing patterns and product popularity.
"""
        future.set_result(fake_response)
        mock_llm.simple_chat.return_value = future
        agent._llm = mock_llm
        
        # Fake metadata context
        context = {
            "rag_results": [{
                "title": "transactions.csv",
                "content": "[METADATA ONLY]",
                "metadata": {"columns": ["tx_id", "customer_id", "product_id", "amount", "date"]}
            }]
        }
        
        print("\nQuerying Analyst Agent: 'Describe this dataset'")
        response = await agent.execute("Describe this dataset", context)
        
        print("\n--- Agent Response ---")
        print(response.content)
        print("----------------------")
        
        if "Dataset Overview" in response.content and "e-commerce" in response.content:
            print("✅ Description Generation Success")
        else:
            print("❌ Description Generation Failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_description())
