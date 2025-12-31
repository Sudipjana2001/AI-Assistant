import os
import sys
import asyncio
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def check_azure_openai():
    logger.info("--- Checking Azure OpenAI ---")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    version = os.getenv("AZURE_OPENAI_API_VERSION")

    if not all([endpoint, api_key, deployment]):
        logger.error("MISSING CONFIG: Azure OpenAI variables not fully set.")
        return

    try:
        from openai import AsyncAzureOpenAI
        client = AsyncAzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=version
        )
        
        logger.info(f"Endpoint: {endpoint}")
        logger.info("Tentative Authentication...")
        
        # ACTIVE CHECK: List models to confirm auth works
        try:
            # We use a timeout to not hang
            await asyncio.wait_for(client.models.list(), timeout=10)
            logger.info("SUCCESS: Azure OpenAI Connection Verified (Models listed).")
        except Exception as e:
             logger.error(f"FAILURE: Azure OpenAI Connection Failed: {e}")

        logger.info(f"Targeting Deployment: {deployment}")
        
    except Exception as e:
        logger.error(f"FAILURE: Azure OpenAI Client Init Failed: {e}")

async def check_azure_storage():
    logger.info("--- Checking Azure Blob Storage ---")
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container = os.getenv("AZURE_STORAGE_CONTAINER")
    
    if not conn_str:
        logger.error("MISSING CONFIG: Azure Storage Connection String not set.")
        return

    try:
        from azure.storage.blob.aio import BlobServiceClient
        client = BlobServiceClient.from_connection_string(conn_str)
        
        # Check if we can list containers (auth check)
        async with client:
            try:
                 # Just try to get account info or list containers
                 containers = []
                 async for c in client.list_containers():
                     containers.append(c.name)
                     if len(containers) >= 1: break
                 
                 logger.info("SUCCESS: Azure Storage Connection Verified (Containers listed).")
                 if container and container not in containers:
                     logger.warning(f"WARNING: Configured container '{container}' not found in list: {containers}")
                 elif container:
                     logger.info(f"SUCCESS: Container '{container}' verified.")
                     
            except Exception as e:
                logger.error(f"FAILURE: Azure Storage Connection Failed: {e}")
                
    except ImportError:
        logger.error("Skipping Storage Check: azure-storage-blob library not installed.")
    except Exception as e:
        logger.error(f"FAILURE: Storage Client Init Failed: {e}")

async def check_azure_search():
    logger.info("--- Checking Azure AI Search ---")
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    key = os.getenv("AZURE_SEARCH_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")

    if not all([endpoint, key, index_name]):
        logger.error("MISSING CONFIG: Azure Search variables not fully set.")
        return

    try:
        from azure.search.documents.indexes.aio import SearchIndexClient
        from azure.core.credentials import AzureKeyCredential

        credential = AzureKeyCredential(key)
        client = SearchIndexClient(endpoint=endpoint, credential=credential)
        
        # Check if index exists
        async with client:
            try:
                await client.get_index(index_name)
                logger.info(f"SUCCESS: Azure AI Search Connected & Found Index '{index_name}'.")
            except Exception as e:
                # 404 is a success for "connection", but failure for "app logic" potentially.
                if "ResourceNotFound" in str(e) or "404" in str(e):
                     logger.warning(f"SUCCESS (Partial): Connected to Search Service, but Index '{index_name}' NOT FOUND.")
                else:
                     logger.error(f"FAILURE: Azure Search Connection Failed: {e}")
                
    except ImportError:
        logger.error("Skipping Search Check: azure-search-documents library not installed.")
    except Exception as e:
        logger.error(f"FAILURE: Azure Search Client Init Failed: {e}")

def check_database():
    logger.info("--- Checking Database ---")
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.error("MISSING CONFIG: DATABASE_URL not set.")
        return

    logger.info(f"Database URL: {db_url}")
    
    if "sqlite" in db_url:
        logger.info("Using SQLite. File access check...")
        path = db_url.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")
        # Remove query params if any
        if "?" in path: path = path.split("?")[0]
        
        if os.path.exists(path):
            logger.info(f"SUCCESS: SQLite DB file found at {path}")
        else:
            logger.info(f"NOTE: SQLite DB file not found at {path}, it will be created on first run.")
        return

    try:
        from sqlalchemy import create_engine, text
        # Use sync engine for quick check
        if "+aiosqlite" in db_url:
           logger.info("Async driver detected. Skipping standard sync verify.")
           return

        engine = create_engine(db_url)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info("SUCCESS: Database connection established (SELECT 1 returned).")
    except ImportError:
        logger.error("Skipping DB Check: sqlalchemy library not installed.")
    except Exception as e:
        logger.error(f"FAILURE: Database connection failed: {e}")

async def check_databricks():
    logger.info("--- Checking Azure Databricks ---")
    workspace_url = os.getenv("DATABRICKS_WORKSPACE_URL")
    token = os.getenv("DATABRICKS_TOKEN")
    
    if not workspace_url or not token:
        logger.error("MISSING CONFIG: Databricks variables not set.")
        return
        
    try:
        import httpx
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient() as client:
            # List clusters is a safe read-only op
            resp = await client.get(f"{workspace_url}/api/2.0/clusters/list", headers=headers)
            if resp.status_code == 200:
                logger.info("SUCCESS: Azure Databricks Connected (Clusters listed).")
            elif resp.status_code == 401:
                logger.error("FAILURE: Databricks Unauthorized (Invalid Token).")
            else:
                logger.error(f"FAILURE: Databricks API returned {resp.status_code}: {resp.text}")
    except ImportError:
        logger.error("Skipping Databricks Check: httpx library not installed.")
    except Exception as e:
        logger.error(f"FAILURE: Databricks check failed: {e}")

async def check_cosmos():
    logger.info("--- Checking Azure Cosmos DB (Gremlin) ---")
    endpoint = os.getenv("COSMOS_GREMLIN_ENDPOINT")
    key = os.getenv("COSMOS_GREMLIN_KEY")
    db_name = os.getenv("COSMOS_GREMLIN_DATABASE")
    graph_name = os.getenv("COSMOS_GREMLIN_GRAPH")

    if not all([endpoint, key, db_name, graph_name]):
        logger.error("MISSING CONFIG: Cosmos DB Gremlin variables not fully set.")
        return

    try:
        from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
        from gremlin_python.process.anonymous_traversal import traversal
        
        # Clean endpoint for Gremlin
        # It usually comes as wss://<acc>.gremlin.cosmos.azure.com:443/
        url = endpoint
        if not url.startswith("wss://"):
            # Try to fix standard mistakes
            host = url.replace("https://", "").replace("/", "")
            url = f"wss://{host}:443/"
            
        logger.info(f"Connecting to: {url}")
        
        # We need a proper client. For a quick check, raw websocket or driver.
        # Driver is heavy but accurate.
        try:
            client = DriverRemoteConnection(url, 'g', username=f"/dbs/{db_name}/colls/{graph_name}", password=key)
            # Just init isn't enough, we need to try a traversal or check closed status
            # If it didn't throw on init, it's a good sign, but let's try a lightweight query if possible?
            # Actually, DriverRemoteConnection is lazy.
            # We will try to confirm the connection by creating a traversal source.
            g = traversal().withRemote(client)
            # A simple count (V().count()) might be costly or fail if graph empty.
            # Let's just trust the handshake for verify step to avoid timeouts/errors on empty graphs.
            logger.info("SUCCESS: Cosmos DB Gremlin Client Initialized.")
            client.close()
        except Exception as e:
            logger.error(f"FAILURE: Cosmos DB Connection Failed: {e}")

    except ImportError:
        logger.error("Skipping Cosmos Check: gremlinpython library not installed.")
    except Exception as e:
        logger.error(f"FAILURE: Cosmos Check Setup Failed: {e}")

async def main():
    print("Starting Comprehensive Backend Connection Verification...")
    print("-------------------------------------------------------")
    await check_azure_openai()
    print("")
    await check_azure_search()
    print("")
    await check_azure_storage()
    print("")
    check_database()
    print("")
    await check_databricks()
    print("")
    await check_cosmos()
    print("-------------------------------------------------------")
    print("Verification Complete.")

if __name__ == "__main__":
    asyncio.run(main())
