import requests
import json

def test_backend():
    url = "https://api-handler-zkzefofekg.ap-southeast-1.fcapp.run/health"
    print(f"Testing backend at {url}...")
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {json.dumps(dict(response.headers), indent=2)}")
        print(f"Body: {response.text}")
        if response.status_code == 200:
            print("Backend health check PASSED!")
        else:
            print("Backend health check FAILED!")
    except Exception as e:
        print(f"Backend health check error: {e}")

if __name__ == "__main__":
    test_backend()
