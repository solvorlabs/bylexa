import os
import jwt
import json
import sys
from typing import Optional, Dict, List, Any

TOKEN_FILE = os.path.expanduser("~/.bylexa_token")
JWT_SECRET = 'bylexa'

# Updated DEFAULT_APP_CONFIGS to include custom_scripts
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
    "custom_scripts": {}  # New section for custom scripts
}

CONFIG_FILE = os.path.expanduser("~/.bylexa_config.json")

def get_platform() -> str:
    platforms = {
        'linux': 'linux',
        'win32': 'windows',
        'darwin': 'darwin'
    }
    return platforms.get(sys.platform, 'unknown')

def load_app_configs() -> dict:
    """Load application configurations from config file."""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return DEFAULT_APP_CONFIGS.copy()
    except Exception as e:
        print(f"Error loading config: {e}")
        return DEFAULT_APP_CONFIGS.copy()

def save_app_configs(app_configs: dict):
    """Save application configurations to config file."""
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(app_configs, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

# Enhanced CRUD operations for applications
def add_app_path(platform: str, app_name: str, path: str) -> bool:
    """Add an application path to the configuration."""
    try:
        app_configs = load_app_configs()
        if platform not in app_configs:
            app_configs[platform] = {}
        if app_name not in app_configs[platform]:
            app_configs[platform][app_name] = []
        if path not in app_configs[platform][app_name]:
            app_configs[platform][app_name].append(path)
            save_app_configs(app_configs)
        return True
    except Exception as e:
        print(f"Error adding app path: {e}")
        return False

def remove_app_path(platform: str, app_name: str, path: str) -> bool:
    """Remove an application path from the configuration."""
    try:
        app_configs = load_app_configs()
        if platform in app_configs and app_name in app_configs[platform]:
            if path in app_configs[platform][app_name]:
                app_configs[platform][app_name].remove(path)
                if not app_configs[platform][app_name]:
                    del app_configs[platform][app_name]
                save_app_configs(app_configs)
                return True
        return False
    except Exception as e:
        print(f"Error removing app path: {e}")
        return False

def update_app_path(platform: str, app_name: str, old_path: str, new_path: str) -> bool:
    """Update an application path in the configuration."""
    try:
        app_configs = load_app_configs()
        if platform in app_configs and app_name in app_configs[platform]:
            if old_path in app_configs[platform][app_name]:
                idx = app_configs[platform][app_name].index(old_path)
                app_configs[platform][app_name][idx] = new_path
                save_app_configs(app_configs)
                return True
        return False
    except Exception as e:
        print(f"Error updating app path: {e}")
        return False

def get_app_paths(platform: str, app_name: str) -> List[str]:
    """Get all paths for a specific application."""
    try:
        app_configs = load_app_configs()
        return app_configs.get(platform, {}).get(app_name, [])
    except Exception as e:
        print(f"Error getting app paths: {e}")
        return []

# Custom scripts CRUD operations
def add_custom_script(name: str, path: str) -> bool:
    """Add a custom script to the configuration."""
    try:
        app_configs = load_app_configs()
        if 'custom_scripts' not in app_configs:
            app_configs['custom_scripts'] = {}
        app_configs['custom_scripts'][name] = path
        save_app_configs(app_configs)
        return True
    except Exception as e:
        print(f"Error adding custom script: {e}")
        return False

def remove_custom_script(name: str) -> bool:
    """Remove a custom script from the configuration."""
    try:
        app_configs = load_app_configs()
        if 'custom_scripts' in app_configs and name in app_configs['custom_scripts']:
            del app_configs['custom_scripts'][name]
            save_app_configs(app_configs)
            return True
        return False
    except Exception as e:
        print(f"Error removing custom script: {e}")
        return False

def update_custom_script(name: str, new_path: str) -> bool:
    """Update a custom script path in the configuration."""
    try:
        app_configs = load_app_configs()
        if 'custom_scripts' in app_configs and name in app_configs['custom_scripts']:
            app_configs['custom_scripts'][name] = new_path
            save_app_configs(app_configs)
            return True
        return False
    except Exception as e:
        print(f"Error updating custom script: {e}")
        return False

def get_custom_scripts() -> Dict[str, str]:
    """Get all custom scripts from the configuration."""
    try:
        app_configs = load_app_configs()
        return app_configs.get('custom_scripts', {})
    except Exception as e:
        print(f"Error getting custom scripts: {e}")
        return {}

# Token management functions remain the same
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
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        email = decoded_token.get('email')
        return email if email else None
    except jwt.ExpiredSignatureError:
        print("Token has expired. Please log in again.")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token. Please log in again.")
        return None