import os
import subprocess
import platform

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
            return f"Opened {app_name} successfully"
        except Exception as e:
            return f"Failed to open {app_name}: {e}"
    else:
        return f"Application {app_name} not recognized."

def perform_task(command):
    """Handles tasks like opening URLs, performing search actions."""
    app_name = command.get('application')
    action = command.get('action')
    task = command.get('task')

    if action == "open" and app_name:
        result = open_application(app_name)
        if task and app_name == "chrome":
            # Handle tasks for Chrome (like opening URLs)
            import time
            time.sleep(3)  # Give Chrome time to open
            os.system(f'start chrome {task}' if platform.system() == "Windows" else f'open -a "Google Chrome" {task}')
            result += f", Opened URL: {task}"
        return result
    else:
        return "Action not supported or unrecognized."
