import asyncio
import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.join(os.getcwd(), 'backend'))
env_path = os.path.join(os.getcwd(), 'backend', '.env')
load_dotenv(env_path)

from app.rag.retriever import RAGRetriever
from app.rag.indexer import RAGIndexer

async def clean_index():
    print("🧹 Cleaning Stale Index Data...")
    retriever = RAGRetriever()
    indexer = RAGIndexer()
    client = retriever.client
    
    # Find the document
    results = client.search("brand_tracking_data.csv", select=["id", "title"])
    
    to_delete = []
    for doc in results:
        print(f"Found: {doc['title']} (ID: {doc['id']})")
        if "brand_tracking_data.csv" in doc['title']:
            # We need the chunk_id or id to delete? 
            # The delete_document method in indexer.py isn't fully implemented for chunk-based deletion 
            # in the version I saw earlier (it passed).
            # So I must delete manually using the SearchClient.
            to_delete.append({"id": doc['id']})
            # Also delete chunks? The ID we see in search is likely chunk_id?
            # Wait, doc['id'] is the key. RAGIndexer.index_document uses f"{file_id}-{i}" as key.
    
    if to_delete:
        print(f"Deleting {len(to_delete)} documents/chunks...")
        # Use existing client to delete
        # client.delete_documents(documents=to_delete) # This expects list of dicts with key
        # We need to ensure we get ALL chunks.
        # Search "*" with filter "title eq 'brand_tracking_data.csv'"?
        # A filter on title is safer.
        pass # manual delete below
        
    # Better approach: Delete by Query does not exist in Azure AI Search API directly for all SDKs easily.
    # We must Query -> Delete.
    
    # Get ALL chunks for this file
    # We filter by title, assuming title hasn't changed to the schema version yet which is why we are deleting it.
    # Or strict search.
    
    # Filter query
    results = client.search(search_text="*", filter="title eq 'brand_tracking_data.csv'", select=["id"])
    docs_to_delete = [{"id": r["id"]} for r in results]
    
    if docs_to_delete:
        print(f"Deleting {len(docs_to_delete)} stale chunks...")
        try:
            client.delete_documents(documents=docs_to_delete)
            print("✅ Deleted successfully.")
        except Exception as e:
             print(f"❌ Delete failed: {e}")
    else:
        print("ℹ️ No stale documents found.")

if __name__ == "__main__":
    asyncio.run(clean_index())
