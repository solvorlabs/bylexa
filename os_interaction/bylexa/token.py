from .config import save_token

def login():
    """Prompt user for their Bylexa API token."""
    token = input("Enter your Bylexa API token: ")
    save_token(token)
    print("Token saved successfully. You can now control your PC with Bylexa.")
