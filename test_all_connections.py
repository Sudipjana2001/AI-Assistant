import asyncio
import os
import sys
from dotenv import load_dotenv

# Load env vars
load_dotenv(dotenv_path="backend/.env")

# Services
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.storage.blob import BlobServiceClient
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
import httpx

async def test_openai():
    print("\n--------- TESTING OPENAI ---------")
    try:
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        key = os.getenv("AZURE_OPENAI_API_KEY")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        
        if not endpoint or not key:
            print("❌ OpenAI Config Missing")
            return
            
        print(f"Connecting to: {endpoint} (Deployment: {deployment})")
        
        # Test basic chat completion
        # Note: Using REST for simplicity if SDK version mismatches, but let's try strict SDK first as per requirements
        
        # Actually, let's use the simplest checks. Connection is what matters.
        client = ChatCompletionsClient(
            endpoint=f"{endpoint}/openai/deployments/{deployment}",
            credential=AzureKeyCredential(key),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        )
        # We perform a lightweight call
        response = client.complete(
            messages=[UserMessage(content="Ping")],
            max_tokens=5
        )
        print("✅ OpenAI Connection Successful!")
        print(f"Response: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ OpenAI Failed: {e}")

async def test_search():
    print("\n--------- TESTING AI SEARCH ---------")
    try:
        endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        key = os.getenv("AZURE_SEARCH_KEY")
        
        if not endpoint or not key:
            print("❌ Search Config Missing")
            return
            
        print(f"Connecting to: {endpoint}")
        client = SearchIndexClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        indexes = list(client.list_indexes())
        print(f"✅ Search Connection Successful! found {len(indexes)} indexes.")
    except Exception as e:
        print(f"❌ Search Failed: {e}")

async def test_storage():
    print("\n--------- TESTING STORAGE ---------")
    try:
        conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        container = os.getenv("AZURE_STORAGE_CONTAINER")
        
        if not conn_str:
            print("❌ Storage Config Missing")
            return
            
        print("Connecting to Blob Storage...")
        client = BlobServiceClient.from_connection_string(conn_str)
        # Check if container exists or list containers
        containers = list(client.list_containers())
        found = any(c.name == container for c in containers)
        
        print(f"✅ Storage Connection Successful! Found {len(containers)} containers.")
        if found:
            print(f"   - Container '{container}' exists: YES")
        else:
            print(f"   - Container '{container}' exists: NO (will be created by app)")
            
    except Exception as e:
        print(f"❌ Storage Failed: {e}")

async def test_databricks():
    print("\n--------- TESTING DATABRICKS ---------")
    try:
        url = os.getenv("DATABRICKS_WORKSPACE_URL")
        token = os.getenv("DATABRICKS_TOKEN")
        cluster_id = os.getenv("DATABRICKS_CLUSTER_ID")
        
        if not url or not token:
            print("❌ Databricks Config Missing")
            return
            
        print(f"Connecting to: {url}")
        headers = {"Authorization": f"Bearer {token}"}
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{url}/api/2.0/clusters/list", headers=headers)
            
            if resp.status_code == 200:
                print("✅ Databricks API Connection Successful!")
                clusters = resp.json().get('clusters', [])
                found_cluster = next((c for c in clusters if c['cluster_id'] == cluster_id), None)
                if found_cluster:
                    print(f"   - Cluster '{cluster_id}' Found: YES (State: {found_cluster['state']})")
                else:
                    if cluster_id:
                         print(f"   - Cluster '{cluster_id}' Found: NO (Check ID)")
                    else:
                        print("   - No Cluster ID configured to check.")
            else:
                print(f"❌ Databricks Failed: Status {resp.status_code} - {resp.text}")
                
    except Exception as e:
        print(f"❌ Databricks Failed: {e}")

async def main():
    await test_openai()
    await test_search()
    await test_storage()
    await test_databricks()
    print("\n-----------------------------------")

if __name__ == "__main__":
    asyncio.run(main())
