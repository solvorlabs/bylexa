import sys
import json
import subprocess
import os
import platform
from typing import Dict, List, Optional

# Type aliases
AppConfig = Dict[str, List[str]]
PlatformConfig = Dict[str, AppConfig]

# Application configurations
APP_CONFIGS: PlatformConfig = {
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
        "spotify": [
            r"C:\Users\amane\AppData\Roaming\Spotify\Spotify.exe",
            r"C:\Program Files\WindowsApps\SpotifyAB.SpotifyMusic_*\Spotify.exe",
        ],
    },
    "darwin": {
        "chrome": ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"],
        "firefox": ["/Applications/Firefox.app/Contents/MacOS/firefox"],
        "text_editor": ["open", "-a", "TextEdit"],
        "spotify": ["/Applications/Spotify.app/Contents/MacOS/Spotify"],
    },
    "linux": {
        "chrome": ["google-chrome", "google-chrome-stable"],
        "firefox": ["firefox"],
        "text_editor": ["gedit", "nano", "vim"],
        "spotify": ["spotify"],
    },
}
def get_platform() -> str:
    """Return the current platform: 'windows', 'darwin', or 'linux'."""
    if sys.platform.startswith('win'):
        return 'windows'
    elif sys.platform == 'darwin':
        return 'darwin'
    else:
        return 'linux'
    
def find_executable(app: str) -> Optional[str]:
    """Find the executable path for the given application."""
    platform = get_platform()
    app_paths = APP_CONFIGS.get(platform, {}).get(app.lower(), [])
    
    for path in app_paths:
        # Expand environment variables (e.g., amane%USERNAME%)
        expanded_path = os.path.expandvars(path)
        if '*' in expanded_path:
            import glob
            matches = glob.glob(expanded_path)
            if matches:
                return matches[0]
        elif os.path.exists(expanded_path):
            return expanded_path
    
    return None

def open_application(app: str, task: Optional[str] = None) -> str:
    """Open the specified application and perform a task if provided."""
    # Convert app name to lowercase
    app = app.lower()
    app_path = find_executable(app)
    
    if not app_path:
        return f"Application {app.capitalize()} not found or not supported."

    try:
        command = [app_path]
        if task:
            command.append(task)
        
        subprocess.Popen(command)
        result = f"Opened {app.capitalize()}"
        if task:
            result += f" and performed task: {task}"
        return result
    except Exception as e:
        return f"Error opening {app.capitalize()}: {str(e)}"

def perform_action(command: Dict[str, str]) -> str:
    """Perform the action specified in the command dictionary."""
    app = command.get('application', '').lower()
    action = command.get('action', '').lower()
    task = command.get('task')

    if action == "open":
        return open_application(app, task)
    else:
        return f"Action {action} is not supported for {app}."

def main(command_input):
    """Main function to handle incoming commands."""
    try:
        if isinstance(command_input, str):
            command = json.loads(command_input)
        elif isinstance(command_input, dict):
            command = command_input
        else:
            raise ValueError("Invalid command input type")
        
        result = perform_action(command)
        return result
    except json.JSONDecodeError:
        return "Error: Invalid JSON input"
    except KeyError as e:
        return f"Error: Missing key in JSON: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        result = main(sys.argv[1])
        print(result)
    else:
        print("Error: No command provided")