import os
import jwt
import json
import sys

TOKEN_FILE = os.path.expanduser("~/.bylexa_token")  # Assuming the token is saved in the user's home directory
JWT_SECRET = 'bylexa'  # This should match the secret used to sign the JWT


DEFAULT_APP_CONFIGS = {
    "windows": {
        "chrome": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ],
        "firefox": [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        ],
        "notepad": ["notepad.exe"],
    },
    "darwin": {
        "chrome": ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"],
        "firefox": ["/Applications/Firefox.app/Contents/MacOS/firefox"],
        "text_editor": ["open", "-a", "TextEdit"],
    },
    "linux": {
        "chrome": ["google-chrome", "google-chrome-stable"],
        "firefox": ["firefox"],
        "text_editor": ["gedit", "nano", "vim"],
    },
}

CONFIG_FILE = os.path.expanduser("~/.bylexa_config.json")

def get_platform() -> str:
    """Detect the current operating system."""
    platforms = {
        'linux': 'linux',
        'win32': 'windows',
        'darwin': 'macos'
    }
    return platforms.get(os.sys.platform, 'unknown')

def load_app_configs() -> dict:
    """Load application configurations from .bylexa_config.json."""
    config_path = os.path.expanduser('~/.bylexa_config.json')
    if not os.path.exists(config_path):
        return {}
    with open(config_path, 'r') as f:
        return json.load(f)

def save_app_configs(app_configs: dict):
    """Save application configurations to .bylexa_config.json."""
    config_path = os.path.expanduser('~/.bylexa_config.json')
    with open(config_path, 'w') as f:
        json.dump(app_configs, f, indent=4)

# Functions to add or remove paths can be added as needed
def add_app_path(app_name: str, path: str):
    app_configs = load_app_configs()
    platform = get_platform()
    if platform not in app_configs:
        app_configs[platform] = {}
    if app_name not in app_configs[platform]:
        app_configs[platform][app_name] = []
    app_configs[platform][app_name].append(path)
    save_app_configs(app_configs)

def remove_app_path(app_name: str, path: str):
    app_configs = load_app_configs()
    platform = get_platform()
    if platform in app_configs and app_name in app_configs[platform]:
        if path in app_configs[platform][app_name]:
            app_configs[platform][app_name].remove(path)
            save_app_configs(app_configs)

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
