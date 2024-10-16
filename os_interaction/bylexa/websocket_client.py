import asyncio
import websockets
import json
from .commands import perform_task
from .config import load_token

async def listen_to_server(uri):
    """Connect to the server and listen for commands."""
    token = load_token()
    if not token:
        print("No token found. Please run 'bylexa login' to authenticate.")
        return
    
    async with websockets.connect(uri, extra_headers={"Authorization": token}) as websocket:
        print("Connected to the Bylexa server...")
        
        while True:
            # Receive a command from the server
            command_json = await websocket.recv()
            print(f"Received command: {command_json}")
            
            # Perform the task based on the received command
            command = json.loads(command_json)
            result = perform_task(command)
            
            # Send the result back to the server
            await websocket.send(f"Result: {result}")
            print(f"Sent result: {result}")

def start_client():
    """Start WebSocket client."""
    uri = "ws://your-bylexa-server.com:8080"
    asyncio.get_event_loop().run_until_complete(listen_to_server(uri))
