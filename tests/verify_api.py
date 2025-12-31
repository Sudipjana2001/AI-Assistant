import requests
import time
import sys

BASE_URL = "http://localhost:8000/api/v1"

def check_health():
    print("Checking API Health...")
    try:
        # Try a simple GET first
        resp = requests.get(f"{BASE_URL}/files/list", timeout=10)
        print(f"Health Check Status: {resp.status_code}")
        return True
    except Exception as e:
        print(f"Health Check Failed: {e}")
        return False

def check_upload():
    print("\nTesting File Upload...")
    try:
        files = {'file': ('test.txt', b'Secret content 12345', 'text/plain')}
        resp = requests.post(f"{BASE_URL}/files/upload", files=files, timeout=10)
        print(f"Upload Status: {resp.status_code}")
        if resp.status_code == 200:
            return resp.json().get("file_id")
        print(f"Upload Result: {resp.text}")
    except Exception as e:
        print(f"Upload Failed: {e}")
    return None

def check_chat(file_id):
    print("\nTesting Chat...")
    try:
        payload = {
            "message": "Read the file I just uploaded", 
            "session_id": "test-session-1"
        }
        resp = requests.post(f"{BASE_URL}/chat/send", json=payload, timeout=30)
        print(f"Chat Status: {resp.status_code}")
        if resp.status_code == 200:
            ans = resp.json().get("response", "")
            print(f"Response: {ans}")
            if "12345" in ans:
                print("❌ FAILED: Content leaked.")
            else:
                print("✅ PASSED: No content leaked.")
    except Exception as e:
        print(f"Chat Failed: {e}")

if __name__ == "__main__":
    if check_health():
        fid = check_upload()
        if fid:
            check_chat(fid)
