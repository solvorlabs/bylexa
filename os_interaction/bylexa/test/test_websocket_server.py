# test_websocket_server.py
import asyncio
import json
from bylexa.websocket_gateway import BylexaWSServer

async def test_websocket_server():
    server = BylexaWSServer(host='localhost', port=8766)  # Different port for testing
    
    print("Starting WebSocket server for testing...")
    
    # Start server in background
    server_task = asyncio.create_task(server.start())
    
    # Wait a bit for server to start
    await asyncio.sleep(2)
    
    print("WebSocket server started successfully!")
    print(f"Server running on {server.host}:{server.port}")
    print("Connection tracking:")
    print(f"  Active connections: {len(server.connections)}")
    print(f"  Authenticated connections: {len(server.authenticated)}")
    print(f"  Active rooms: {len(server.rooms)}")
    
    # Stop server
    await server.stop()
    server_task.cancel()

if __name__ == "__main__":
    asyncio.run(test_websocket_server())