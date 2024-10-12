import os
import subprocess
import platform

# Mapping of application names to their executable commands (customize as needed)
APP_PATHS = {
    "chrome": "chrome" if platform.system() == "Windows" else "google-chrome",
    "notepad": "notepad" if platform.system() == "Windows" else "gedit",
    "spotify": "spotify"
}

def open_application(app_name):
    """Opens the specified application if it exists in APP_PATHS."""
    if app_name in APP_PATHS:
        try:
            print(f"Opening {app_name}...")
            subprocess.Popen([APP_PATHS[app_name]])
        except Exception as e:
            print(f"Failed to open {app_name}: {e}")
    else:
        print(f"Application {app_name} not recognized.")

def perform_task(command):
    """Handle tasks like opening URLs, performing search actions."""
    app_name = command.get('application')
    action = command.get('action')
    task = command.get('task')

    if action == "open" and app_name:
        open_application(app_name)
        if task and app_name == "chrome":
            # Handle tasks for Chrome (like opening URLs)
            import time
            time.sleep(3)  # Give Chrome time to open
            os.system(f'start chrome {task}' if platform.system() == "Windows" else f'open -a "Google Chrome" {task}')
    else:
        print("Action not supported or unrecognized.")

# Example reusable function call
if __name__ == "__main__":
    # Simulate a command from the LLM: "open chrome and go to youtube.com"
    command = {
        "application": "chrome",
        "action": "open",
        "task": "https://youtube.com"
    }
    perform_task(command)
