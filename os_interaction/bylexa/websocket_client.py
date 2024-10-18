import asyncio
import websockets
import json
from .commands import perform_action
from .config import load_email, load_token
import requests

def get_protected_data():
    """Send a request to the protected route and retrieve the user's email."""
    token = load_token()
    if not token:
        print("No token found. Please run 'bylexa login' to authenticate.")
        return

    try:
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.get("http://localhost:3000/protected", headers=headers)

        if response.status_code == 200:
            print(response.json().get("message"))
        else:
            print(f"Failed to retrieve protected data: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        print(f"Error connecting to the server: {e}")

async def listen_to_server(host, port):
    """Connect to the server and listen for commands."""
    email = load_email()
    if not email:
        print("No email found. Please run 'bylexa login' to authenticate.")
        return

    uri = f"ws://{host}:{port}/ws"
    
    while True:
        try:
            async with websockets.connect(uri, extra_headers={"Authorization": email}) as websocket:
                print(f"Connected to the Bylexa server at {uri}")

                while True:
                    command_json = await websocket.recv()
                    print(f"Received command: {command_json}")

                    try:
                        command = json.loads(command_json)
                        result = perform_action(command)
                    except json.JSONDecodeError:
                        result = "Error: Invalid JSON received"
                    except Exception as e:
                        result = f"Error: {str(e)}"

                    await websocket.send(json.dumps({"result": result}))
                    print(f"Sent result: {result}")

        except websockets.exceptions.InvalidURI:
            print(f"Invalid WebSocket URI: {uri}")
            return
        except websockets.exceptions.ConnectionClosedError:
            print(f"Connection closed unexpectedly. Retrying in 5 seconds...")
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Retrying in 5 seconds...")

        await asyncio.sleep(5)

def start_client(host="localhost", port=3000):
    """Start WebSocket client."""
    asyncio.get_event_loop().run_until_complete(listen_to_server(host, port))