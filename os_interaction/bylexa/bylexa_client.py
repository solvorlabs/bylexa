import asyncio
import websockets
import json
import logging
import uuid
import sys
import threading
import queue
import time
import base64
from typing import Dict, List, Any, Optional, Callable, Set, Union

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BylexaClient:
    """
    Client SDK for Bylexa that allows applications to interact with the system.
    Provides event subscription, command execution, and remote triggers.
    """
    
    def __init__(self, api_key: str, server_url: str = 'ws://localhost:8765'):
        """
        Initialize the Bylexa client.
        
        Args:
            api_key: API key or authentication token
            server_url: WebSocket server URL
        """
        self.api_key = api_key
        self.server_url = server_url
        
        # Connection state
        self.websocket = None
        self.connected = False
        self.connection_id = None
        self.current_room = None
        
        # Event handling
        self._triggers = {}  # Maps event types to callbacks
        self._command_handlers = {}  # Maps action types to handlers
        self._message_queue = queue.Queue()
        self._response_events = {}  # Maps message IDs to events
        self._response_data = {}  # Maps message IDs to response data
        
        # Threading
        self._receive_thread = None
        self._process_thread = None
        self._running = False
    
    async def connect(self) -> bool:
        """
        Connect to the Bylexa WebSocket server.
        
        Returns:
            True if connection successful, False otherwise
        """
        if self.connected:
            return True
        
        try:
            # Create authentication header
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            
            # Connect to the server
            self.websocket = await websockets.connect(
                self.server_url,
                extra_headers=headers
            )
            
            # Wait for welcome message
            welcome = await self.websocket.recv()
            welcome_data = json.loads(welcome)
            
            if welcome_data.get('action') == 'welcome':
                self.connected = True
                self.connection_id = welcome_data.get('connection_id')
                logger.info(f"Connected to Bylexa server: {self.connection_id}")
                return True
            else:
                logger.error(f"Unexpected welcome message: {welcome_data}")
                await self.websocket.close()
                self.websocket = None
                return False
                
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            if self.websocket:
                await self.websocket.close()
                self.websocket = None
            return False
    
    async def disconnect(self):
        """Disconnect from the Bylexa WebSocket server."""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        
        self.connected = False
        self.connection_id = None
        self.current_room = None
        logger.info("Disconnected from Bylexa server")
    
    async def join_room(self, room_code: str) -> bool:
        """
        Join a room on the server.
        
        Args:
            room_code: Code for the room to join
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected:
            logger.error("Not connected to server")
            return False
        
        try:
            # Send join room message
            await self.websocket.send(json.dumps({
                'action': 'join_room',
                'room_code': room_code
            }))
            
            # Wait for response
            response = await self.websocket.recv()
            data = json.loads(response)
            
            if data.get('action') == 'room_joined' and data.get('room_code') == room_code:
                self.current_room = room_code
                logger.info(f"Joined room: {room_code}")
                return True
            else:
                logger.error(f"Failed to join room: {data}")
                return False
                
        except Exception as e:
            logger.error(f"Error joining room: {str(e)}")
            return False
    
    async def leave_room(self) -> bool:
        """
        Leave the current room.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.connected:
            logger.error("Not connected to server")
            return False
        
        if not self.current_room:
            logger.warning("Not in a room")
            return True
        
        try:
            # Send leave room message
            await self.websocket.send(json.dumps({
                'action': 'leave_room'
            }))
            
            # Wait for response
            response = await self.websocket.recv()
            data = json.loads(response)
            
            if data.get('action') == 'room_left':
                previous_room = self.current_room
                self.current_room = None
                logger.info(f"Left room: {previous_room}")
                return True
            else:
                logger.error(f"Failed to leave room: {data}")
                return False
                
        except Exception as e:
            logger.error(f"Error leaving room: {str(e)}")
            return False
    
    async def send_command(self, command: str, wait_for_response: bool = True) -> Optional[Dict]:
        """
        Send a command to be executed by the AI orchestrator.
        
        Args:
            command: Command string to execute
            wait_for_response: Whether to wait for the response
            
        Returns:
            Response dictionary if wait_for_response is True, None otherwise
        """
        if not self.connected:
            logger.error("Not connected to server")
            return None
        
        try:
            # Generate message ID
            message_id = str(uuid.uuid4())
            
            # Create response event if waiting
            if wait_for_response:
                response_event = threading.Event()
                self._response_events[message_id] = response_event
            
            # Send command
            await self.websocket.send(json.dumps({
                'action': 'command',
                'command': command,
                'message_id': message_id
            }))
            
            # Wait for response if requested
            if wait_for_response:
                response_event.wait(timeout=30.0)
                
                # Get and clear response data
                response = self._response_data.pop(message_id, None)
                self._response_events.pop(message_id, None)
                
                return response
            
            return None
                
        except Exception as e:
            logger.error(f"Error sending command: {str(e)}")
            return None
    
    async def execute_remote(self, command: Dict, target_room: str = None) -> bool:
        """
        Execute a command on remote devices.
        
        Args:
            command: Command dictionary to execute
            target_room: Optional room to target (defaults to current room)
            
        Returns:
            True if command was sent, False otherwise
        """
        if not self.connected:
            logger.error("Not connected to server")
            return False
        
        room_code = target_room or self.current_room
        if not room_code:
            logger.error("No room specified and not in a room")
            return False
        
        try:
            # Send broadcast message with command
            await self.websocket.send(json.dumps({
                'action': 'broadcast',
                'room_code': room_code,
                'command': command
            }))
            
            return True
                
        except Exception as e:
            logger.error(f"Error executing remote command: {str(e)}")
            return False
    
    async def register_trigger(self, event_type: str, callback: Callable) -> bool:
        """
        Register a callback for a specific event type.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event occurs
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected:
            logger.error("Not connected to server")
            return False
        
        try:
            # Register callback locally
            self._triggers[event_type] = callback
            
            # Subscribe to event on server
            await self.websocket.send(json.dumps({
                'action': 'subscribe',
                'event_type': event_type
            }))
            
            # Wait for subscription confirmation
            response = await self.websocket.recv()
            data = json.loads(response)
            
            if data.get('action') == 'subscribed' and data.get('event_type') == event_type:
                logger.info(f"Subscribed to event: {event_type}")
                return True
            else:
                logger.error(f"Failed to subscribe to event: {data}")
                return False
                
        except Exception as e:
            logger.error(f"Error registering trigger: {str(e)}")
            return False
    
    async def unregister_trigger(self, event_type: str) -> bool:
        """
        Unregister a callback for a specific event type.
        
        Args:
            event_type: Type of event to unsubscribe from
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected:
            logger.error("Not connected to server")
            return False
        
        try:
            # Unregister callback locally
            if event_type in self._triggers:
                del self._triggers[event_type]
            
            # Unsubscribe from event on server
            await self.websocket.send(json.dumps({
                'action': 'unsubscribe',
                'event_type': event_type
            }))
            
            # Wait for unsubscription confirmation
            response = await self.websocket.recv()
            data = json.loads(response)
            
            if data.get('action') == 'unsubscribed' and data.get('event_type') == event_type:
                logger.info(f"Unsubscribed from event: {event_type}")
                return True
            else:
                logger.error(f"Failed to unsubscribe from event: {data}")
                return False
                
        except Exception as e:
            logger.error(f"Error unregistering trigger: {str(e)}")
            return False
    
    def start(self):
        """Start the client in the background."""
        if self._running:
            return
        
        self._running = True
        
        # Start the connection in a separate thread
        self._connect_thread = threading.Thread(target=self._connect_loop)
        self._connect_thread.daemon = True
        self._connect_thread.start()
    
    def stop(self):
        """Stop the client."""
        self._running = False
        
        # Wait for threads to finish
        if self._receive_thread and self._receive_thread.is_alive():
            self._receive_thread.join(timeout=5.0)
        
        if self._process_thread and self._process_thread.is_alive():
            self._process_thread.join(timeout=5.0)
        
        if self._connect_thread and self._connect_thread.is_alive():
            self._connect_thread.join(timeout=5.0)
        
        # Close WebSocket connection
        if self.websocket:
            asyncio.run(self.disconnect())
    
    def _connect_loop(self):
        """Connect and maintain the WebSocket connection."""
        while self._running:
            try:
                # Create and run event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Connect to server
                loop.run_until_complete(self.connect())
                
                if self.connected:
                    # Start receive and process threads
                    self._receive_thread = threading.Thread(target=self._receive_loop, args=(loop,))
                    self._receive_thread.daemon = True
                    self._receive_thread.start()
                    
                    self._process_thread = threading.Thread(target=self._process_loop)
                    self._process_thread.daemon = True
                    self._process_thread.start()
                    
                    # Keep the connection alive
                    self._keep_alive(loop)
                
                loop.close()
                
            except Exception as e:
                logger.error(f"Connection thread error: {str(e)}")
            
            # Try to reconnect after a delay
            if self._running:
                time.sleep(5.0)
    
    def _keep_alive(self, loop):
        """Keep the WebSocket connection alive."""
        while self._running and self.connected:
            try:
                # Send a ping every 30 seconds
                loop.run_until_complete(asyncio.sleep(30.0))
                if self.websocket:
                    loop.run_until_complete(self.websocket.ping())
            except Exception as e:
                logger.error(f"Keep-alive error: {str(e)}")
                self.connected = False
                break
    
    def _receive_loop(self, loop):
        """Receive and queue messages from the WebSocket."""
        while self._running and self.connected:
            try:
                # Receive message
                message = loop.run_until_complete(self.websocket.recv())
                
                # Parse and queue for processing
                data = json.loads(message)
                self._message_queue.put(data)
                
            except websockets.exceptions.ConnectionClosed:
                logger.warning("WebSocket connection closed")
                self.connected = False
                break
            except Exception as e:
                logger.error(f"Receive error: {str(e)}")
                if str(e).startswith('no running event loop'):
                    # Event loop is closed, exit
                    break
    
    def _process_loop(self):
        """Process queued messages."""
        while self._running:
            try:
                # Get message from queue with timeout
                try:
                    data = self._message_queue.get(timeout=0.5)
                except queue.Empty:
                    continue
                
                # Process based on action type
                action = data.get('action')
                
                if action == 'event':
                    # Handle event
                    event_type = data.get('event_type')
                    event_data = data.get('data', {})
                    
                    # Call registered trigger callback if exists
                    if event_type and event_type in self._triggers:
                        try:
                            self._triggers[event_type](event_data)
                        except Exception as e:
                            logger.error(f"Error in trigger callback for {event_type}: {str(e)}")
                
                elif action == 'broadcast':
                    # Handle broadcast message
                    command = data.get('command')
                    message = data.get('message')
                    sender = data.get('sender')
                    
                    # Call registered broadcast handler if exists
                    if 'broadcast' in self._command_handlers:
                        try:
                            self._command_handlers['broadcast'](message, command, sender)
                        except Exception as e:
                            logger.error(f"Error in broadcast handler: {str(e)}")
                
                elif action == 'command_result':
                    # Handle command result
                    result = data.get('result')
                    message_id = data.get('message_id')
                    
                    # Wake up thread waiting for this response
                    if message_id and message_id in self._response_events:
                        self._response_data[message_id] = result
                        self._response_events[message_id].set()
                
                elif action == 'error':
                    # Log error message
                    error_msg = data.get('message', 'Unknown error')
                    logger.error(f"Server error: {error_msg}")
                
                elif action == 'room_event':
                    # Handle room event
                    event = data.get('event')
                    connection_id = data.get('connection_id')
                    room_code = data.get('room_code')
                    
                    # Call registered room handler if exists
                    if 'room_event' in self._command_handlers:
                        try:
                            self._command_handlers['room_event'](event, connection_id, room_code)
                        except Exception as e:
                            logger.error(f"Error in room event handler: {str(e)}")
                
                elif action == 'python_execute':
                    # Handle Python execution request
                    code = data.get('code')
                    sender = data.get('sender')
                    
                    # Call registered Python handler if exists
                    if 'python_execute' in self._command_handlers:
                        try:
                            result = self._command_handlers['python_execute'](code, sender)
                            
                            # Send result back if available
                            if result:
                                asyncio.run(self._send_python_result(code, result, sender))
                        except Exception as e:
                            logger.error(f"Error in Python execution handler: {str(e)}")
                
                # Handle other action types
                elif action in self._command_handlers:
                    try:
                        self._command_handlers[action](data)
                    except Exception as e:
                        logger.error(f"Error in handler for {action}: {str(e)}")
                
                # Mark as processed
                self._message_queue.task_done()
                
            except Exception as e:
                logger.error(f"Message processing error: {str(e)}")
    
    async def _send_python_result(self, code: str, result: Dict, original_sender: str):
        """Send Python execution result back to the server."""
        if not self.connected or not self.websocket:
            return
        
        try:
            await self.websocket.send(json.dumps({
                'action': 'python_output',
                'result': result,
                'code': code,
                'original_sender': original_sender
            }))
        except Exception as e:
            logger.error(f"Error sending Python result: {str(e)}")
    
    def register_command_handler(self, action: str, handler: Callable) -> bool:
        """
        Register a handler for a specific command action.
        
        Args:
            action: Action type to handle
            handler: Function to call when action is received
            
        Returns:
            True if successful, False otherwise
        """
        self._command_handlers[action] = handler
        return True
    
    def unregister_command_handler(self, action: str) -> bool:
        """
        Unregister a handler for a specific command action.
        
        Args:
            action: Action type to unregister
            
        Returns:
            True if successful, False otherwise
        """
        if action in self._command_handlers:
            del self._command_handlers[action]
            return True
        return False
    
    def execute_command(self, command: str) -> Optional[Dict]:
        """
        Execute a command synchronously and wait for the result.
        
        Args:
            command: Command string to execute
            
        Returns:
            Response dictionary or None if error
        """
        try:
            return asyncio.run(self.send_command(command))
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            return None
    
    def broadcast_message(self, message: str = None, command: Dict = None, target_room: str = None) -> bool:
        """
        Broadcast a message or command to a room.
        
        Args:
            message: Optional text message to broadcast
            command: Optional command dictionary to broadcast
            target_room: Optional room to target (defaults to current room)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            room_code = target_room or self.current_room
            if not room_code:
                logger.error("No room specified and not in a room")
                return False
            
            asyncio.run(self.websocket.send(json.dumps({
                'action': 'broadcast',
                'room_code': room_code,
                'message': message,
                'command': command
            })))
            
            return True
        except Exception as e:
            logger.error(f"Error broadcasting message: {str(e)}")
            return False


class TriggerHandler:
    """
    Class for defining and managing triggers in a Bylexa application.
    """
    
    def __init__(self, client: BylexaClient):
        """
        Initialize the trigger handler.
        
        Args:
            client: BylexaClient instance
        """
        self.client = client
        self.triggers = {}
        
    def on_event(self, event_type: str):
        """
        Decorator for registering event triggers.
        
        Args:
            event_type: Type of event to subscribe to
            
        Returns:
            Decorator function
        """
        def decorator(func):
            # Register the function as a trigger
            self.triggers[event_type] = func
            
            # Register with the client
            if self.client and self.client.connected:
                asyncio.run(self.client.register_trigger(event_type, func))
            
            return func
        
        return decorator
    
    def on_command(self, action: str):
        """
        Decorator for registering command handlers.
        
        Args:
            action: Action type to handle
            
        Returns:
            Decorator function
        """
        def decorator(func):
            # Register with the client
            if self.client:
                self.client.register_command_handler(action, func)
            
            return func
        
        return decorator
    
    def register_all_triggers(self):
        """Register all defined triggers with the client."""
        if not self.client or not self.client.connected:
            return False
        
        for event_type, func in self.triggers.items():
            asyncio.run(self.client.register_trigger(event_type, func))
        
        return True


def create_client(api_key: str, server_url: str = 'ws://localhost:8765') -> BylexaClient:
    """
    Create and initialize a Bylexa client.
    
    Args:
        api_key: API key or authentication token
        server_url: WebSocket server URL
        
    Returns:
        Initialized BylexaClient instance
    """
    client = BylexaClient(api_key, server_url)
    
    # Start client in background
    client.start()
    
    # Wait for connection
    start_time = time.time()
    while not client.connected and time.time() - start_time < 10.0:
        time.sleep(0.1)
    
    return client