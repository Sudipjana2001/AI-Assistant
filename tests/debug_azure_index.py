import asyncio
import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.join(os.getcwd(), 'backend'))
env_path = os.path.join(os.getcwd(), 'backend', '.env')
load_dotenv(env_path)

from app.rag.retriever import RAGRetriever

async def list_index_contents():
    print("🔍 Inspecting Azure Search Index...")
    try:
        retriever = RAGRetriever()
        client = retriever.client
        
        # Search for everything
        results = client.search("*", select=["title", "source", "chunk_id", "id"])
        
        count = 0
        found_target = False
        print("\n--- Index Contents ---")
        for doc in results:
            count += 1
            title = doc.get("title", "N/A")
            source = doc.get("source", "N/A")
            print(f"📄 [{count}] Title: {title} | Source: {source}")
            
            if "brand_tracking" in title.lower() or "brand_tracking" in source.lower():
                found_target = True
        
        print(f"\nTotal Documents: {count}")
        if found_target:
            print("✅ 'brand_tracking_data.csv' found in index.")
        else:
            print("❌ 'brand_tracking_data.csv' NOT found in index.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(list_index_contents())
