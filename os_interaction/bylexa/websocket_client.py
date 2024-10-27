import asyncio
import websockets
import json
from .commands import perform_action
from .config import load_email, load_token
import requests
import threading
import keyboard
import sys

WEBSOCKET_SERVER_URL = 'wss://bylexa.onrender.com/ws'  # Replace with your backend URL

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
        response = requests.get("https://bylexa.onrender.com/protected", headers=headers)

        if response.status_code == 200:
            print(response.json().get("message"))
        else:
            print(f"Failed to retrieve protected data: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        print(f"Error connecting to the server: {e}")

async def listen(token, room_code=None):
    """Listen for commands and join a room if a room_code is provided."""
    headers = {'Authorization': f'Bearer {token}'}
    try:
        async with websockets.connect(WEBSOCKET_SERVER_URL, extra_headers=headers) as websocket:
            if room_code:
                # Send a message to join the room
                await websocket.send(json.dumps({'action': 'join_room', 'room_code': room_code}))
                print(f"Joined room: {room_code}")
            
            while True:
                try:
                    message = await websocket.recv()
                    command = json.loads(message)
                    print(f"Received command: {command}")
                    result = perform_action(command['command'])
                    print(f"Sent result: {result}")
                    # Send the result back to the server
                    await websocket.send(json.dumps({'result': result}))
                except websockets.exceptions.ConnectionClosed:
                    print("Connection closed")
                    break
                except Exception as e:
                    print(f"Error: {e}")
    except websockets.exceptions.InvalidURI:
        print(f"Invalid WebSocket URI: {WEBSOCKET_SERVER_URL}")
    except websockets.exceptions.ConnectionClosedError:
        print("Connection closed unexpectedly. Reconnecting in 5 seconds...")
        await asyncio.sleep(5)
    except Exception as e:
        print(f"An error occurred: {e}. Retrying in 5 seconds...")
        await asyncio.sleep(5)

async def prompt_room_code():
    """Prompt the user for a room code asynchronously."""
    while True:
        await asyncio.to_thread(keyboard.wait, 'F2')  # Block until F2 is pressed
        room_code = input("Enter the room code: ")
        token = load_token()
        if not token:
            print("No token found. Please run 'bylexa login' to authenticate.")
            continue
        await listen(token, room_code=room_code)

def start_client():
    token = load_token()
    if not token:
        print("No token found. Please run 'bylexa login' to authenticate.")
        sys.exit(1)
    
    loop = asyncio.get_event_loop()
    try:
        # Start the room code prompt listener in a separate async task
        loop.create_task(prompt_room_code())
        # Start the main client WebSocket listener without a room initially
        loop.run_until_complete(listen(token))
    except KeyboardInterrupt:
        print("Client stopped.")
    finally:
        # Clean up and close the loop
        loop.close()
