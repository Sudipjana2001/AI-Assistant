import asyncio
import sys
import os
import uuid
# Load env
from dotenv import load_dotenv
sys.path.append(os.path.join(os.getcwd(), 'backend'))
env_path = os.path.join(os.getcwd(), 'backend', '.env')
load_dotenv(env_path)

from app.api.v1.endpoints.files import _process_and_index_file
from app.rag.retriever import RAGRetriever

async def debug_indexing():
    print("🚀 Starting Upload & Indexing Debug...")
    
    # 1. Create a dummy CSV
    file_id = str(uuid.uuid4())
    filename = "debug_schema_test.csv"
    content = b"Date,Brand,Awareness,Sentiment\n2023-01-01,BrandA,85.5,Positive\n2023-01-02,BrandB,90.2,Neutral"
    ext = "csv"
    blob_url = "https://example.com/debug.csv"
    
    print(f"📄 Simulating Upload for {filename} (ID: {file_id})")
    
    # 2. Run the processing function directly
    try:
        await _process_and_index_file(file_id, content, ext, filename, blob_url)
        print("✅ _process_and_index_file completed without raising exception.")
    except Exception as e:
        print(f"❌ _process_and_index_file FAILED: {e}")
        import traceback
        traceback.print_exc()
        return

    # 3. Verify visibility in Retriever
    print("\n🔍 Verifying visibility via Retriever...")
    retriever = RAGRetriever()
    
    # Wait a moment for Azure
    await asyncio.sleep(5)
    
    try:
        # Search for the specific file ID or filename
        results = await retriever.retrieve(filename)
        print(f"found {len(results)} results for query '{filename}'")
        
        found = False
        for doc in results:
            print(f" - Title: {doc.get('title')}")
            if "Schema: Date, Brand" in doc.get('title', ''):
                found = True
        
        if found:
            print("✅ SUCCESS: File found with injected Schema in title!")
        else:
            print("❌ FAILURE: File not found or Schema missing from title.")
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")

if __name__ == "__main__":
    asyncio.run(debug_indexing())
