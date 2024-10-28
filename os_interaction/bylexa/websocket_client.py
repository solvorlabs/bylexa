import asyncio
import websockets
import json
from .commands import perform_action
from .config import load_email, load_token
import sys
import aioconsole

# WEBSOCKET_SERVER_URL = 'ws://localhost:3000/ws'
WEBSOCKET_SERVER_URL = 'wss://bylexa.onrender.com/ws'

async def listen(token, room_code=None):
    """Listen for commands and join a room if a room_code is provided."""
    headers = {'Authorization': f'Bearer {token}'}
    email = load_email()
    
    while True:
        try:
            print(f"Connecting to server at {WEBSOCKET_SERVER_URL}...")
            async with websockets.connect(WEBSOCKET_SERVER_URL, extra_headers=headers) as websocket:
                print(f"Connected to {WEBSOCKET_SERVER_URL} as {email}")
                
                if room_code:
                    # Send a message to join the room
                    await websocket.send(json.dumps({'action': 'join_room', 'room_code': room_code}))
                    print(f"Joined room: {room_code}")

                # Start message input handler
                input_task = asyncio.create_task(handle_user_input(websocket, room_code))
                receive_task = asyncio.create_task(handle_server_messages(websocket))

                # Wait for either task to complete (or raise an exception)
                done, pending = await asyncio.wait(
                    [input_task, receive_task],
                    return_when=asyncio.FIRST_COMPLETED
                )

                # Cancel the remaining task
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

                # Re-raise any exceptions
                for task in done:
                    try:
                        await task
                    except Exception as e:
                        print(f"Task error: {e}")
                        raise

        except websockets.exceptions.ConnectionClosed:
            print("Connection closed. Attempting to reconnect...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"An error occurred: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)

async def handle_user_input(websocket, room_code):
    """Handle user input for sending messages."""
    while True:
        try:
            print("\nPress Enter to send a message (or Ctrl+C to quit)")
            await aioconsole.ainput()  # Wait for Enter key
            
            action_type = await aioconsole.ainput("Enter action type (e.g., 'broadcast', 'show_notification'): ")
            message = await aioconsole.ainput("Enter the message you want to send: ")

            if action_type.lower() == 'broadcast' and room_code:
                action_data = {
                    "action": "broadcast",
                    "room_code": room_code,
                    "command": message
                }
            else:
                action_data = {
                    "action": action_type,
                    "message": message
                }

            await websocket.send(json.dumps(action_data))
            print(f"Sent: {action_data}")
            
        except asyncio.CancelledError:
            raise
        except Exception as e:
            print(f"Error sending message: {e}")

async def handle_server_messages(websocket):
    """Handle incoming messages from the server."""
    while True:
        try:
            message = await websocket.recv()
            command = json.loads(message)
            print(f"\nReceived: {command}")

            if 'command' in command:
                result = perform_action(command['command'])
                await websocket.send(json.dumps({'result': result}))
                print(f"Sent result: {result}")
            elif 'message' in command:
                print(f"Message from server: {command['message']}")
            else:
                print(f"Unhandled message: {command}")
                
        except asyncio.CancelledError:
            raise
        except Exception as e:
            print(f"Error handling server message: {e}")
            raise

async def main():
    token = load_token()
    if not token:
        print("No token found. Please run 'bylexa login' to authenticate.")
        return

    print("Press Ctrl+C to quit")
    print("Enter room code (or press Enter to skip):")
    room_code = await aioconsole.ainput()
    room_code = room_code.strip() if room_code else None

    await listen(token, room_code)

def start_client():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nClient stopped.")

if __name__ == "__main__":
    start_client()