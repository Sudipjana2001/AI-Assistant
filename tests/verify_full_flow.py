import requests
import time
import sys
import uuid

BASE_URL = "http://localhost:8000/api/v1"
SESSION_ID = f"test-session-{uuid.uuid4()}"

def print_result(step, success, msg=""):
    icon = "✅" if success else "❌"
    print(f"{icon} {step}: {msg}")
    if not success:
        sys.exit(1)

def test_full_flow():
    print(f"🚀 Starting Full Flow Verification (Session: {SESSION_ID})")
    
    # 1. Upload File
    print("\n--- Step 1: File Upload ---")
    files = {'file': ('ecommerce_data.csv', b'customer_id,product_id,amount,date\n1,101,50.0,2023-01-01\n2,102,100.0,2023-01-01', 'text/csv')}
    try:
        resp = requests.post(f"{BASE_URL}/files/upload", files=files, timeout=60)
        if resp.status_code == 200:
            file_id = resp.json().get("file_id")
            print_result("Upload", True, f"File ID: {file_id}")
        else:
            print_result("Upload", False, f"Status {resp.status_code} - {resp.text}")
    except Exception as e:
        print_result("Upload", False, str(e))

    # Wait for indexing (Real Azure might take longer)
    print("⏳ Waiting 15s for Azure Indexing...")
    time.sleep(15)

    # 2. Analyst Agent (Describe)
    print("\n--- Step 2: Analyst Agent (Describe) ---")
    payload = {
        "message": "Describe the ecommerce_data.csv I just uploaded",
        "session_id": SESSION_ID,
        "agent": "analyst" # Explicitly asking for analyst
    }
    try:
        resp = requests.post(f"{BASE_URL}/chat/send", json=payload, timeout=30)
        data = resp.json()
        response_text = data.get("response", "")
        print(f"Agent Response:\n{response_text[:300]}...") # Print first 300 chars
        
        if "ecommerce" in response_text.lower() or "customer" in response_text.lower():
             print_result("Analyst Description", True, "Detected dataset domain/content.")
        else:
             print_result("Analyst Description", False, "Response did not describe the data.")
    except Exception as e:
        print_result("Analyst Chat", False, str(e))

    # 3. SQL Agent (Query)
    print("\n--- Step 3: SQL Agent (Generate Query) ---")
    payload = {
        "message": "Write a SQL query to sum amount by product_id",
        "session_id": SESSION_ID,
        "agent": "sql"
    }
    try:
        resp = requests.post(f"{BASE_URL}/chat/send", json=payload, timeout=30)
        data = resp.json()
        response_text = data.get("response", "")
        print(f"Agent Response:\n{response_text[:300]}...")
        
        if "SELECT" in response_text and "GROUP BY" in response_text:
             print_result("SQL Generation", True, "Generated valid SQL.")
        else:
             print_result("SQL Generation", False, "Did not generate SQL.")
    except Exception as e:
        print_result("SQL Chat", False, str(e))

    # 4. Python Agent (Analysis Code)
    print("\n--- Step 4: Python Agent (Generate Code) ---")
    payload = {
        "message": "Write python code to plot the amount distribution",
        "session_id": SESSION_ID,
        "agent": "python"
    }
    try:
        resp = requests.post(f"{BASE_URL}/chat/send", json=payload, timeout=30)
        data = resp.json()
        response_text = data.get("response", "")
        print(f"Agent Response:\n{response_text[:300]}...")
        
        if "pd.read_csv" in response_text or "plt.hist" in response_text or "seaborn" in response_text:
             print_result("Python Code Generation", True, "Generated valid Analysis code.")
        else:
             print_result("Python Code Generation", False, "Did not generate Python code.")
    except Exception as e:
        print_result("Python Chat", False, str(e))

if __name__ == "__main__":
    test_full_flow()
