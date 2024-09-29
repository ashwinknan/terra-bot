import requests

def test_backend():
    try:
        response = requests.get('http://localhost:5001')
        print(f"Server is running. Status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("Unable to connect to the server. Make sure it's running on http://localhost:5001")

if __name__ == "__main__":
    test_backend()