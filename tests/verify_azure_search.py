import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Load environment variables explicitly
from dotenv import load_dotenv
env_path = os.path.join(os.getcwd(), 'backend', '.env')
print(f"Loading .env from: {env_path}")
load_dotenv(env_path)

from app.rag.retriever import RAGRetriever
from app.rag.indexer import RAGIndexer

async def verify_azure_connection():
    print("🔌 Verifying Azure AI Search Connection...")
    
    try:
        # 1. Test Retriever
        print("\n[Retriever Test]")
        retriever = RAGRetriever()
        print(f"Endpoint: {retriever.endpoint}")
        # print(f"Key: {retriever.key[:5]}...") # Don't print secrets
        
        # Test client creation
        client = retriever.client
        print("✅ SearchClient created")
        
        # Test basic search query
        print("Trying search query 'test'...")
        results = await retriever.retrieve("test")
        print(f"✅ Search successful! Got {len(results)} results.")
        
        # 2. Test Indexer
        print("\n[Indexer Test]")
        indexer = RAGIndexer()
        
        # Test index existence check
        print("Checking index existence...")
        await indexer.create_index_if_not_exists()
        print("✅ Index check/creation successful.")
        
        return True

    except Exception as e:
        print(f"❌ Azure verification failed: {str(e)}")
        # Print full traceback
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(verify_azure_connection())
    if not success:
        sys.exit(1)
