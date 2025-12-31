import sys
import os
from dotenv import load_dotenv
from gremlin_python.driver import client as gremlin_client

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
env_path = os.path.join(os.getcwd(), 'backend', '.env')
load_dotenv(env_path)

def verify_kag_sync():
    print("🚀 Verifying KAG (Cosmos DB Gremlin) Connectivity Sync...")
    
    endpoint = os.getenv("COSMOS_GREMLIN_ENDPOINT")
    key = os.getenv("COSMOS_GREMLIN_KEY")
    database = os.getenv("COSMOS_GREMLIN_DATABASE", "KnowledgeGraph")
    graph = os.getenv("COSMOS_GREMLIN_GRAPH", "MarketResearch")
    
    if not endpoint or not key:
        print("❌ Missing credentials in .env")
        return

    # Prepare connection
    username = f"/dbs/{database}/colls/{graph}"
    
    print(f"🔗 Connecting to {endpoint}...")
    try:
        client = gremlin_client.Client(
            url=endpoint,
            traversal_source='g',
            username=username,
            password=key,
            message_serializer=gremlin_client.serializer.GraphSONSerializersV2d0()
        )
        
        # Test query
        print("🔍 Submitting query: g.V().count()...")
        result_set = client.submit("g.V().count()")
        results = result_set.all().result()
        print(f"✅ Success! Vertex count: {results}")
        
        # List labels
        print("🔍 Submitting query: g.V().label().dedup()...")
        result_set = client.submit("g.V().label().dedup()")
        labels = result_set.all().result()
        print(f"✅ Found labels: {labels}")
        
        client.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify_kag_sync()
