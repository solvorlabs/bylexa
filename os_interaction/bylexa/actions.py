import os
import subprocess
from typing import Optional
from .config import get_platform, load_app_configs
import shutil
import glob
import json
from pathlib import Path
import pyperclip  # For clipboard operations
import schedule   # For scheduling tasks
import time


def find_executable(app: str) -> Optional[str]:
    """Find the executable path for the given application."""
    platform = get_platform()
    app_configs = load_app_configs()
    app_paths = app_configs.get(platform, {}).get(app.lower(), [])

    for path in app_paths:
        expanded_path = os.path.expandvars(path)
        matched_paths = glob.glob(expanded_path)
        for matched_path in matched_paths:
            if os.path.exists(matched_path) or shutil.which(matched_path):
                return matched_path

    return None

def open_application(app: str, task: Optional[str] = None) -> str:
    """Open the specified application and perform a task if provided."""
    app_path = find_executable(app)
    if not app_path:
        return f"Application '{app}' not found or not supported."

    try:
        command = [app_path]
        if task:
            command.append(task)

        subprocess.Popen(command)
        result = f"Opened '{app}'"
        if task:
            result += f" with task: {task}"
        return result
    except Exception as e:
        return f"Error opening '{app}': {str(e)}"

def run_shell_command(command_str: str) -> str:
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(command_str, shell=True, capture_output=True, text=True)
        if result.stdout:
            return result.stdout
        else:
            return "Command executed with no output."
    except Exception as e:
        return f"Error executing command: {str(e)}"

def manipulate_file(action: str, source: str, destination: Optional[str] = None) -> str:
    """Perform file operations like copy, move, delete."""
    try:
        if action == 'copy':
            shutil.copy(source, destination)
            return f"Copied '{source}' to '{destination}'"
        elif action == 'move':
            shutil.move(source, destination)
            return f"Moved '{source}' to '{destination}'"
        elif action == 'delete':
            os.remove(source)
            return f"Deleted '{source}'"
        elif action == 'create_directory':
            os.makedirs(source, exist_ok=True)
            return f"Directory '{source}' created"
        else:
            return f"Unsupported file action '{action}'"
    except Exception as e:
        return f"Error performing file action '{action}': {str(e)}"

def interact_with_clipboard(action: str, text: Optional[str] = None) -> str:
    """Copy to or paste from the clipboard."""
    try:
        if action == 'copy':
            pyperclip.copy(text)
            return "Text copied to clipboard."
        elif action == 'paste':
            pasted_text = pyperclip.paste()
            return f"Pasted text from clipboard: {pasted_text}"
        else:
            return f"Unsupported clipboard action '{action}'"
    except Exception as e:
        return f"Error with clipboard action '{action}': {str(e)}"

def schedule_task(time_str: str, command: dict) -> str:
    """Schedule a task to be executed at a specific time."""
    action = command.get('action')
    if not action:
        return "Error: 'action' not specified in command."

    def job():
        perform_action(command)

    schedule.every().day.at(time_str).do(job)
    # Run the scheduler in a separate thread or process in production
    return f"Scheduled task '{action}' at {time_str}"

def open_document(file_path: str) -> str:
    """Open a document with the default application."""
    try:
        if os.path.exists(file_path):
            os.startfile(file_path)  # For Windows
            return f"Opened document '{file_path}'"
        else:
            return f"File '{file_path}' does not exist."
    except Exception as e:
        return f"Error opening document: {str(e)}"

def control_media_player(action: str, media: Optional[str] = None) -> str:
    """Control media player actions like play, pause, stop."""
    # Placeholder implementation, extend with actual media player control
    return f"Media player action '{action}' executed."

def perform_custom_script(script_path: str, args: Optional[list] = None) -> str:
    """Execute a custom script with optional arguments."""
    if not os.path.exists(script_path):
        return f"Script '{script_path}' does not exist."

    try:
        command = ['python', script_path] + (args if args else [])
        subprocess.Popen(command)
        return f"Executed script '{script_path}'"
    except Exception as e:
        return f"Error executing script: {str(e)}"

# Add more functions for additional features as needed
