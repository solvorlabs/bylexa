# test_websocket_client.py
import asyncio
import websockets
import json

async def test_websocket_client():
    uri = "ws://localhost:8765"
    
    try:
        # Test connection without auth (should fail)
        print("=== Testing Connection Without Auth ===")
        async with websockets.connect(uri) as websocket:
            response = await websocket.recv()
            data = json.loads(response)
            print(f"Response: {data}")
            
    except Exception as e:
        print(f"Expected auth error: {e}")
    
    try:
        # Test connection with auth
        print("\n=== Testing Connection With Auth ===")
        headers = {"Authorization": "Bearer test_token"}
        
        async with websockets.connect(uri, extra_headers=headers) as websocket:
            # Should receive welcome message
            welcome = await websocket.recv()
            print(f"Welcome: {json.loads(welcome)}")
            
            # Test command sending
            command = {
                "action": "command",
                "command": "open notepad"
            }
            
            await websocket.send(json.dumps(command))
            response = await websocket.recv()
            print(f"Command Response: {json.loads(response)}")
            
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_client())