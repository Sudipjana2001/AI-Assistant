import requests
import time
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_file_upload():
    print("\n1. Testing File Upload...")
    # Create a dummy file
    files = {'file': ('test_metadata_doc.txt', b'This is a test file content. It contains secret info: 12345.', 'text/plain')}
    
    try:
        response = requests.post(f"{BASE_URL}/files/upload", files=files)
        print(f"   Upload Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            file_id = data.get("file_id")
            print(f"   ✅ Upload Success! File ID: {file_id}")
            return file_id
        else:
            print(f"   ❌ Upload Failed: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
        return None

def test_chat_metadata_only(file_id):
    print("\n2. Testing Chat (Metadata Verification)...")
    if not file_id:
        print("   ⚠️  Skipping chat test due to upload failure.")
        return

    # Give it a second to "process" (mock or real)
    time.sleep(2)
    
    chat_payload = {
        "message": "What is in the file I just uploaded?",
        "conversation_id": "test-conv-1"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=chat_payload)
        print(f"   Chat Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("response", "")
            print(f"   Assistant Answer: {answer}")
            
            # VERIFICATION LOGIC
            if "12345" in answer:
                print("   ❌ FAIL: Assistant read the content (12345)!")
            elif "cannot read the file content" in answer or "metadata" in answer.lower() or "test_metadata_doc.txt" in answer:
                print("   ✅ PASS: Assistant respected metadata-only policy.")
            else:
                print("   ❓ INDETERMINATE: Check answer manually.")
                
        else:
            print(f"   ❌ Chat Failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting E2E Verification")
    fid = test_file_upload()
    test_chat_metadata_only(fid)
