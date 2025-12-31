import asyncio
import sys
import os
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
env_path = os.path.join(os.getcwd(), 'backend', '.env')
load_dotenv(env_path)

from app.kag.graph_retriever import KAGRetriever

async def verify_kag():
    print("🚀 Verifying KAG (Cosmos DB Gremlin) Connectivity (Simplified)...")
    
    retriever = KAGRetriever()
    
    # 1. Test Raw Connection First
    try:
        print("🔗 Testing raw Gremlin connection...")
        client = retriever._get_client()
        # Simple query to list labels
        result_set = client.submit("g.V().label().dedup().limit(10)")
        results = result_set.all().result()
        print(f"✅ Connection Successful! Found labels: {results}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return

    # 2. Test Retriever Logic
    try:
        print("\n🔍 Testing retriever.retrieve() logic...")
        # Search for something very generic or nothing
        # Note: If graph is empty, this returns []
        results = await retriever.retrieve("a")
        print(f"Retriever returned {len(results)} results.")
        for r in results:
             print(f" - {r}")
    except Exception as e:
        print(f"❌ Retriever Error: {e}")

    retriever.close()

if __name__ == "__main__":
    # Ensure we use a clean event loop
    asyncio.run(verify_kag())
