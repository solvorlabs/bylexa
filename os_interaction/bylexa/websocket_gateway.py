import asyncio
import websockets
import json
import logging
import uuid
import time
import jwt
import hmac
import hashlib
import base64
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta

from .ai_orchestrator import get_orchestrator
from .config import load_token

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BylexaWSServer:
    """
    WebSocket gateway for Bylexa that handles remote connections,
    command processing, and event distribution.
    """
    
    def __init__(self, host: str = 'localhost', port: int = 8765):
        """
        Initialize the WebSocket server.
        
        Args:
            host: Hostname or IP to bind the server to
            port: Port number to listen on
        """
        self.host = host
        self.port = port
        
        # Connection tracking
        self.connections = {}  # Maps connection ID to websocket
        self.authenticated = set()  # Set of authenticated connection IDs
        self.rooms = {}  # Maps room codes to sets of connection IDs
        self.connection_to_room = {}  # Maps connection ID to room code
        self.connection_info = {}  # Maps connection ID to client info
        
        # Event subscribers
        self.event_subscribers = {}  # Maps event types to sets of connection IDs
        
        # Command handlers
        self.command_handlers = {
            'join_room': self._handle_join_room,
            'leave_room': self._handle_leave_room,
            'broadcast': self._handle_broadcast,
            'python_execute': self._handle_python_execute,
            'python_output': self._handle_python_output,
            'subscribe': self._handle_subscribe,
            'unsubscribe': self._handle_unsubscribe,
            'command': self._handle_command,
            'query': self._handle_query
        }
        
        # Start message processing task
        self.running = False
        self.message_queue = asyncio.Queue()
        self.processing_task = None
    
    async def start(self):
        """Start the WebSocket server."""
        self.running = True
        
        # Start message processing task
        self.processing_task = asyncio.create_task(self._process_message_queue())
        
        # Start the WebSocket server
        async with websockets.serve(
            self.handle_connection, self.host, self.port
        ):
            logger.info(f"WebSocket server started on {self.host}:{self.port}")
            await asyncio.Future()  # Run forever
    
    async def stop(self):
        """Stop the WebSocket server."""
        self.running = False
        
        # Cancel processing task
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        
        # Close all connections
        close_tasks = []
        for conn_id, websocket in self.connections.items():
            close_tasks.append(asyncio.create_task(websocket.close()))
        
        if close_tasks:
            await asyncio.gather(*close_tasks, return_exceptions=True)
        
        # Clear all state
        self.connections.clear()
        self.authenticated.clear()
        self.rooms.clear()
        self.connection_to_room.clear()
        self.connection_info.clear()
        self.event_subscribers.clear()
        
        logger.info("WebSocket server stopped")
    
    async def handle_connection(self, websocket, path):
        """
        Handle a new WebSocket connection.
        
        Args:
            websocket: The WebSocket connection object
            path: The connection path
        """
        # Generate a unique connection ID
        conn_id = str(uuid.uuid4())
        
        # Store the connection
        self.connections[conn_id] = websocket
        self.connection_info[conn_id] = {
            'connected_at': datetime.now().isoformat(),
            'remote': websocket.remote_address,
            'authenticated': False,
            'client_info': {}
        }
        
        logger.info(f"New connection: {conn_id} from {websocket.remote_address}")
        
        try:
            # Handle authentication
            authenticated = await self._authenticate(websocket, conn_id)
            if not authenticated:
                logger.warning(f"Authentication failed for {conn_id}")
                return
            
            # Mark as authenticated
            self.authenticated.add(conn_id)
            self.connection_info[conn_id]['authenticated'] = True
            
            # Send welcome message
            await websocket.send(json.dumps({
                'action': 'welcome',
                'connection_id': conn_id,
                'message': 'Connected to Bylexa WebSocket Gateway'
            }))
            
            # Handle messages until the connection is closed
            async for message in websocket:
                await self._handle_message(conn_id, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection closed: {conn_id}")
        except Exception as e:
            logger.error(f"Error handling connection {conn_id}: {str(e)}")
        finally:
            # Clean up
            await self._remove_connection(conn_id)
    
    async def _authenticate(self, websocket, conn_id: str) -> bool:
        """
        Authenticate a WebSocket connection.
        
        Args:
            websocket: The WebSocket connection object
            conn_id: The connection ID
            
        Returns:
            True if authentication succeeded, False otherwise
        """
        try:
            # Get auth header from websocket
            request_headers = websocket.request_headers
            auth_header = request_headers.get('Authorization', '')
            
            # Check authentication
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                
                # In a real system, you would verify the token properly
                # For now, just check if it's not empty and matches the local token
                local_token = load_token()
                if token and (token == local_token or self._verify_token(token)):
                    return True
            
            # If auth header is missing or invalid, send auth error and close
            await websocket.send(json.dumps({
                'action': 'error',
                'message': 'Authentication required'
            }))
            
            return False
            
        except Exception as e:
            logger.error(f"Authentication error for {conn_id}: {str(e)}")
            return False
    
    def _verify_token(self, token: str) -> bool:
        """
        Verify a JWT token.
        
        Args:
            token: JWT token to verify
            
        Returns:
            True if token is valid, False otherwise
        """
        try:
            # In a real system, you would verify the token signature, expiration, etc.
            # For this example, we'll just check basic JWT structure
            parts = token.split('.')
            if len(parts) != 3:
                return False
            
            # Try to decode payload
            payload = json.loads(base64.b64decode(
                parts[1] + '=' * ((4 - len(parts[1]) % 4) % 4)
            ).decode('utf-8'))
            
            # Check expiration
            exp = payload.get('exp', 0)
            if exp and exp < time.time():
                return False
            
            # For demonstration purposes, consider it valid if it has basic JWT structure
            return True
            
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            return False
    
    async def _remove_connection(self, conn_id: str):
        """
        Remove a connection and clean up associated data.
        
        Args:
            conn_id: Connection ID to remove
        """
        # Remove from authenticated set
        if conn_id in self.authenticated:
            self.authenticated.remove(conn_id)
        
        # Remove from rooms
        room_code = self.connection_to_room.get(conn_id)
        if room_code and room_code in self.rooms:
            self.rooms[room_code].discard(conn_id)
            # Remove empty rooms
            if not self.rooms[room_code]:
                del self.rooms[room_code]
        
        # Remove from room mapping
        if conn_id in self.connection_to_room:
            del self.connection_to_room[conn_id]
        
        # Remove from event subscribers
        for event_type, subscribers in list(self.event_subscribers.items()):
            if conn_id in subscribers:
                subscribers.remove(conn_id)
            # Remove empty subscriber lists
            if not subscribers:
                del self.event_subscribers[event_type]
        
        # Remove from connections dict
        if conn_id in self.connections:
            del self.connections[conn_id]
        
        # Remove from connection info
        if conn_id in self.connection_info:
            del self.connection_info[conn_id]
        
        logger.info(f"Connection removed: {conn_id}")
    
    async def _handle_message(self, conn_id: str, message: str):
        """
        Handle a message from a client.
        
        Args:
            conn_id: Connection ID of the sender
            message: Message string (expected to be JSON)
        """
        try:
            # Parse message as JSON
            data = json.loads(message)
            
            # Check for required action field
            if 'action' not in data:
                await self._send_error(conn_id, "Missing 'action' field in message")
                return
            
            # Get the action and handler
            action = data['action']
            handler = self.command_handlers.get(action)
            
            if handler:
                # Add to message queue for processing
                await self.message_queue.put((conn_id, action, data, handler))
            else:
                await self._send_error(conn_id, f"Unknown action: {action}")
        
        except json.JSONDecodeError:
            await self._send_error(conn_id, "Invalid JSON message")
        except Exception as e:
            await self._send_error(conn_id, f"Error processing message: {str(e)}")
    
    async def _process_message_queue(self):
        """Process messages from the queue."""
        while self.running:
            try:
                # Get a message from the queue
                conn_id, action, data, handler = await self.message_queue.get()
                
                # Process the message
                try:
                    await handler(conn_id, data)
                except Exception as e:
                    logger.error(f"Error handling action '{action}': {str(e)}")
                    await self._send_error(conn_id, f"Error handling action '{action}': {str(e)}")
                
                # Mark the task as done
                self.message_queue.task_done()
                
            except asyncio.CancelledError:
                # Task was cancelled, exit loop
                break
            except Exception as e:
                logger.error(f"Error in message processing loop: {str(e)}")
    
    async def _send_error(self, conn_id: str, message: str):
        """
        Send an error message to a client.
        
        Args:
            conn_id: Connection ID to send to
            message: Error message
        """
        if conn_id in self.connections:
            try:
                await self.connections[conn_id].send(json.dumps({
                    'action': 'error',
                    'message': message
                }))
            except Exception as e:
                logger.error(f"Error sending error message to {conn_id}: {str(e)}")
    
    async def _send_to_connection(self, conn_id: str, data: Dict):
        """
        Send data to a specific connection.
        
        Args:
            conn_id: Connection ID to send to
            data: Data dictionary to send
        """
        if conn_id in self.connections:
            try:
                await self.connections[conn_id].send(json.dumps(data))
            except Exception as e:
                logger.error(f"Error sending data to {conn_id}: {str(e)}")
                # Connection might be dead, remove it
                await self._remove_connection(conn_id)
    
    async def _broadcast_to_room(self, room_code: str, data: Dict, exclude_conn_id: str = None):
        """
        Broadcast data to all connections in a room.
        
        Args:
            room_code: Room code to broadcast to
            data: Data dictionary to send
            exclude_conn_id: Optional connection ID to exclude from broadcast
        """
        if room_code not in self.rooms:
            return
        
        # Get connections in the room
        connections = self.rooms[room_code].copy()
        
        # Send to each connection
        for conn_id in connections:
            if conn_id != exclude_conn_id and conn_id in self.connections:
                await self._send_to_connection(conn_id, data)
    
    async def _broadcast_event(self, event_type: str, data: Dict):
        """
        Broadcast an event to all subscribers.
        
        Args:
            event_type: Type of event
            data: Event data dictionary
        """
        if event_type not in self.event_subscribers:
            return
        
        # Get subscribers for this event type
        subscribers = self.event_subscribers[event_type].copy()
        
        # Send to each subscriber
        for conn_id in subscribers:
            if conn_id in self.connections:
                event_data = {
                    'action': 'event',
                    'event_type': event_type,
                    'data': data
                }
                await self._send_to_connection(conn_id, event_data)
    
    # Command handlers
    
    async def _handle_join_room(self, conn_id: str, data: Dict):
        """Handle a request to join a room."""
        room_code = data.get('room_code')
        if not room_code:
            await self._send_error(conn_id, "Missing 'room_code' field")
            return
        
        # Create room if it doesn't exist
        if room_code not in self.rooms:
            self.rooms[room_code] = set()
        
        # Leave current room if in one
        current_room = self.connection_to_room.get(conn_id)
        if current_room:
            if current_room in self.rooms:
                self.rooms[current_room].discard(conn_id)
                # Remove empty rooms
                if not self.rooms[current_room]:
                    del self.rooms[current_room]
            
            # Notify others in the room that this client left
            if current_room in self.rooms:
                await self._broadcast_to_room(
                    current_room,
                    {
                        'action': 'room_event',
                        'event': 'left',
                        'connection_id': conn_id,
                        'room_code': current_room
                    },
                    exclude_conn_id=conn_id
                )
        
        # Add to new room
        self.rooms[room_code].add(conn_id)
        self.connection_to_room[conn_id] = room_code
        
        # Notify client they joined the room
        await self._send_to_connection(
            conn_id,
            {
                'action': 'room_joined',
                'room_code': room_code,
                'members': len(self.rooms[room_code])
            }
        )
        
        # Notify others in the room that a new client joined
        await self._broadcast_to_room(
            room_code,
            {
                'action': 'room_event',
                'event': 'joined',
                'connection_id': conn_id,
                'room_code': room_code
            },
            exclude_conn_id=conn_id
        )
    
    async def _handle_leave_room(self, conn_id: str, data: Dict):
        """Handle a request to leave a room."""
        current_room = self.connection_to_room.get(conn_id)
        if not current_room:
            await self._send_error(conn_id, "Not in a room")
            return
        
        # Remove from room
        if current_room in self.rooms:
            self.rooms[current_room].discard(conn_id)
            # Remove empty rooms
            if not self.rooms[current_room]:
                del self.rooms[current_room]
        
        # Remove room mapping
        del self.connection_to_room[conn_id]
        
        # Notify client they left the room
        await self._send_to_connection(
            conn_id,
            {
                'action': 'room_left',
                'room_code': current_room
            }
        )
        
        # Notify others in the room that this client left
        if current_room in self.rooms:
            await self._broadcast_to_room(
                current_room,
                {
                    'action': 'room_event',
                    'event': 'left',
                    'connection_id': conn_id,
                    'room_code': current_room
                },
                exclude_conn_id=conn_id
            )
    
    async def _handle_broadcast(self, conn_id: str, data: Dict):
        """Handle a broadcast message to a room."""
        room_code = self.connection_to_room.get(conn_id)
        if not room_code:
            room_code = data.get('room_code')
            if not room_code:
                await self._send_error(conn_id, "Not in a room and no 'room_code' specified")
                return
        
        if room_code not in self.rooms:
            await self._send_error(conn_id, f"Room {room_code} does not exist")
            return
        
        # Get message content
        message = data.get('message')
        command = data.get('command')
        
        # Broadcast to room
        await self._broadcast_to_room(
            room_code,
            {
                'action': 'broadcast',
                'sender': conn_id,
                'message': message,
                'command': command,
                'room_code': room_code
            },
            exclude_conn_id=conn_id if data.get('exclude_self', False) else None
        )
    
    async def _handle_python_execute(self, conn_id: str, data: Dict):
        """Handle a request to execute Python code remotely."""
        code = data.get('code')
        if not code:
            await self._send_error(conn_id, "Missing 'code' field")
            return
        
        room_code = data.get('room_code') or self.connection_to_room.get(conn_id)
        
        # Forward to others in the room
        if room_code and room_code in self.rooms:
            await self._broadcast_to_room(
                room_code,
                {
                    'action': 'python_execute',
                    'code': code,
                    'sender': conn_id
                },
                exclude_conn_id=conn_id
            )
    
    async def _handle_python_output(self, conn_id: str, data: Dict):
        """Handle Python execution output."""
        result = data.get('result')
        if not result:
            await self._send_error(conn_id, "Missing 'result' field")
            return
        
        original_sender = data.get('original_sender')
        if original_sender and original_sender in self.connections:
            # Send back to the original sender
            await self._send_to_connection(
                original_sender,
                {
                    'action': 'python_result',
                    'result': result,
                    'executor': conn_id,
                    'code': data.get('code', '')
                }
            )
    
    async def _handle_subscribe(self, conn_id: str, data: Dict):
        """Handle a subscription request."""
        event_type = data.get('event_type')
        if not event_type:
            await self._send_error(conn_id, "Missing 'event_type' field")
            return
        
        # Create subscriber set if it doesn't exist
        if event_type not in self.event_subscribers:
            self.event_subscribers[event_type] = set()
        
        # Add to subscribers
        self.event_subscribers[event_type].add(conn_id)
        
        # Notify client they subscribed
        await self._send_to_connection(
            conn_id,
            {
                'action': 'subscribed',
                'event_type': event_type
            }
        )
    
    async def _handle_unsubscribe(self, conn_id: str, data: Dict):
        """Handle an unsubscribe request."""
        event_type = data.get('event_type')
        if not event_type:
            await self._send_error(conn_id, "Missing 'event_type' field")
            return
        
        # Remove from subscribers
        if event_type in self.event_subscribers:
            self.event_subscribers[event_type].discard(conn_id)
            # Remove empty subscriber lists
            if not self.event_subscribers[event_type]:
                del self.event_subscribers[event_type]
        
        # Notify client they unsubscribed
        await self._send_to_connection(
            conn_id,
            {
                'action': 'unsubscribed',
                'event_type': event_type
            }
        )
    
    async def _handle_command(self, conn_id: str, data: Dict):
        """Handle a command to be executed by the AI orchestrator."""
        command = data.get('command')
        if not command:
            await self._send_error(conn_id, "Missing 'command' field")
            return
        
        # Get AI orchestrator
        orchestrator = get_orchestrator()
        
        # Process the command
        result = orchestrator.process_text(command)
        
        # Send the result back
        await self._send_to_connection(
            conn_id,
            {
                'action': 'command_result',
                'result': result
            }
        )
        
        # Broadcast the command as an event if requested
        if data.get('broadcast_event', False):
            event_type = data.get('event_type', 'command')
            await self._broadcast_event(
                event_type,
                {
                    'command': command,
                    'result': result,
                    'sender': conn_id
                }
            )
    
    async def _handle_query(self, conn_id: str, data: Dict):
        """Handle a query for system information."""
        query_type = data.get('query_type')
        if not query_type:
            await self._send_error(conn_id, "Missing 'query_type' field")
            return
        
        response = {
            'action': 'query_result',
            'query_type': query_type
        }
        
        if query_type == 'rooms':
            # Return list of rooms and member counts
            rooms_info = {}
            for room, members in self.rooms.items():
                rooms_info[room] = len(members)
            response['rooms'] = rooms_info
            
        elif query_type == 'connections':
            # Return count of connections
            response['count'] = len(self.connections)
            response['authenticated'] = len(self.authenticated)
            
        elif query_type == 'subscribers':
            # Return count of subscribers per event type
            subscribers_info = {}
            for event_type, subscribers in self.event_subscribers.items():
                subscribers_info[event_type] = len(subscribers)
            response['subscribers'] = subscribers_info
            
        else:
            response['error'] = f"Unknown query type: {query_type}"
        
        # Send response
        await self._send_to_connection(conn_id, response)


# Global server instance
_server_instance = None

def get_ws_server() -> BylexaWSServer:
    """Get the global WebSocket server instance."""
    global _server_instance
    if _server_instance is None:
        _server_instance = BylexaWSServer()
    return _server_instance

async def start_ws_server(host: str = 'localhost', port: int = 8765):
    """Start the WebSocket server with the given host and port."""
    global _server_instance
    if _server_instance is None:
        _server_instance = BylexaWSServer(host, port)
    await _server_instance.start()

async def stop_ws_server():
    """Stop the WebSocket server if it's running."""
    global _server_instance
    if _server_instance is not None:
        await _server_instance.stop()
        _server_instance = None