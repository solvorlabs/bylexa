import requests
from getpass import getpass
from .config import save_token

def login():
    """Prompt user for their Bylexa email and password to retrieve API token."""
    email = input("Enter your Bylexa email: ")
    password = getpass("Enter your Bylexa password: ")

    payload = {
        "email": email,
        "password": password
    }

    try:
        response = requests.post("http://localhost:3000/api/auth/login", json=payload)
        # response = requests.post("https://bylexa.onrender.com/api/auth/login", json=payload)

        if response.status_code == 200:
            token = response.json().get("token")
            if token:
                save_token(token)
                print("Token saved successfully. You can now control your PC with Bylexa.")
            else:
                print("Error: Token not found in response.")
        else:
            print(f"Login failed: {response.status_code} - {response.text}")

    except requests.RequestException as e:
        print(f"Error connecting to Bylexa API: {e}")
