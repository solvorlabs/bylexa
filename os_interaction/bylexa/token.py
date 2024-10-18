import requests
from .config import save_token

def login():
    """Prompt user for their Bylexa email and password to retrieve API token."""
    email = input("Enter your Bylexa email: ")
    password = input("Enter your Bylexa password: ")

    # Prepare the payload for the API call
    payload = {
        "email": email,
        "password": password
    }

    try:
        # Make a POST request to Bylexa API to log in
        response = requests.post("http://localhost:3000/api/auth/login", json=payload)

        # Check if the request was successful
        if response.status_code == 200:
            # Extract the token from the response
            token = response.json().get("token")

            if token:
                # Save the token using the save_token function
                save_token(token)
                print("Token saved successfully. You can now control your PC with Bylexa.")
            else:
                print("Error: Token not found in response.")
        else:
            print(f"Login failed: {response.status_code} - {response.text}")

    except requests.RequestException as e:
        print(f"Error connecting to Bylexa API: {e}")
