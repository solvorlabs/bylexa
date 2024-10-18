import os
import jwt

TOKEN_FILE = os.path.expanduser("~/.bylexa_token")  # Assuming the token is saved in the user's home directory
JWT_SECRET = 'bylexa'  # This should match the secret used to sign the JWT

def save_token(token):
    """Save the token to a file."""
    with open(TOKEN_FILE, 'w') as f:
        f.write(token)

def load_token():
    """Load the saved token from a file."""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            return f.read().strip()
    return None

def load_email():
    """Extract email from the saved token."""
    token = load_token()
    if not token:
        print("No token found. Please run 'bylexa login' to authenticate.")
        return None

    try:
        # Decode the token and extract the payload
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        email = decoded_token.get('email')
        if email:
            return email
        else:
            print("Email not found in the token.")
            return None
    except jwt.ExpiredSignatureError:
        print("Token has expired. Please log in again.")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token. Please log in again.")
        return None
