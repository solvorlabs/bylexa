import sys
import json
import subprocess

def open_application(app_name):
    try:
        subprocess.Popen(app_name)
        return f"Opened {app_name}"
    except Exception as e:
        return f"Error opening {app_name}: {str(e)}"

def perform_action(app, action, task):
    if app == "browser":
        if action == "open":
            return open_application(f"firefox {task}")  # Adjust browser as needed
    elif app == "text_editor":
        if action == "open":
            return open_application("gedit")  # Adjust text editor as needed
    # Add more application and action handlers here
    return f"Performed {action} on {app} with task: {task}"

def main(command_json):
    try:
        command = json.loads(command_json)
        result = perform_action(command['application'], command['action'], command['task'])
        print(result)
    except json.JSONDecodeError:
        print("Error: Invalid JSON input")
    except KeyError as e:
        print(f"Error: Missing key in JSON: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Error: No command provided")