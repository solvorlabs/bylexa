from typing import Dict, Callable
from .actions import (
    open_application,
    run_shell_command,
    manipulate_file,
    interact_with_clipboard,
    schedule_task,
    open_document,
    control_media_player,
    perform_custom_script,
)
import json

# Registry for command handlers
COMMAND_HANDLERS: Dict[str, Callable] = {}

def register_command(action: str):
    """Decorator to register a command handler."""
    def decorator(func):
        COMMAND_HANDLERS[action.lower()] = func
        return func
    return decorator

def perform_action(command: Dict[str, str]) -> str:
    """Perform the action specified in the command dictionary."""
    action = command.get('action', '').lower()
    handler = COMMAND_HANDLERS.get(action)
    if handler:
        return handler(command)
    else:
        return f"Action '{action}' is not supported."

@register_command("open")
def handle_open_command(command: Dict[str, str]) -> str:
    app = command.get('application')
    task = command.get('task')
    file_path = command.get('file_path')
    if file_path:
        return open_document(file_path)
    if not app:
        return "Error: 'application' not specified in command."
    return open_application(app, task)

@register_command("run")
def handle_run_command(command: Dict[str, str]) -> str:
    command_str = command.get('command')
    if not command_str:
        return "Error: 'command' not specified."
    return run_shell_command(command_str)

@register_command("file")
def handle_file_command(command: Dict[str, str]) -> str:
    action = command.get('file_action')
    source = command.get('source')
    destination = command.get('destination')
    if not action or not source:
        return "Error: 'file_action' and 'source' are required."
    return manipulate_file(action, source, destination)

@register_command("clipboard")
def handle_clipboard_command(command: Dict[str, str]) -> str:
    action = command.get('clipboard_action')
    text = command.get('text')
    return interact_with_clipboard(action, text)

@register_command("schedule")
def handle_schedule_command(command: Dict[str, str]) -> str:
    time_str = command.get('time')
    if not time_str:
        return "Error: 'time' not specified."
    return schedule_task(time_str, command.get('task_command'))

@register_command("media")
def handle_media_command(command: Dict[str, str]) -> str:
    action = command.get('media_action')
    media = command.get('media')
    if not action:
        return "Error: 'media_action' not specified."
    return control_media_player(action, media)

@register_command("script")
def handle_script_command(command: Dict[str, str]) -> str:
    script_path = command.get('script_path')
    args = command.get('args', [])
    if not script_path:
        return "Error: 'script_path' not specified."
    return perform_custom_script(script_path, args)

@register_command("close")
def handle_close_command(command: Dict[str, str]) -> str:
    app = command.get('application')
    if not app:
        return "Error: 'application' not specified in command."
    # Implement logic to close the application
    # For example, use os.system("taskkill /im app.exe /f") on Windows
    try:
        if get_platform() == 'windows':
            os.system(f"taskkill /im {app}.exe /f")
        else:
            os.system(f"pkill {app}")
        return f"Closed '{app}'"
    except Exception as e:
        return f"Error closing '{app}': {str(e)}"
